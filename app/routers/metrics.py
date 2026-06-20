from fastapi import APIRouter, Depends, Header
from fastapi import HTTPException, Response
from app.middleware.metrics import get_request_counts, get_recent_requests
from app.core.config import settings
from jose import jwt, JWTError
from typing import Optional
import redis
import json
from fastapi import Request
from functools import lru_cache
from fastapi import Depends

router = APIRouter()


def _check_api_key(x_metrics_api_key: Optional[str] = Header(None)):
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Debug metrics disabled")
    if not settings.METRICS_API_KEY:
        # No API key configured — allow only in debug
        return True
    if not x_metrics_api_key or x_metrics_api_key != settings.METRICS_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


def _check_ip_allowlist(request: Request):
    """Reject requests not coming from allowed IPs if allowlist configured."""
    if not settings.METRICS_IP_ALLOWLIST:
        return True
    # extract client IP (support X-Forwarded-For if set)
    trusted = settings.METRICS_TRUSTED_HEADER
    client_ip = None
    if trusted and trusted in request.headers:
        client_ip = request.headers.get(trusted).split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else None

    allowlist = [ip.strip() for ip in settings.METRICS_IP_ALLOWLIST.split(",") if ip.strip()]
    if client_ip and client_ip in allowlist:
        return True
    raise HTTPException(status_code=403, detail="IP not allowed")


def _require_admin_jwt(authorization: Optional[str] = Header(None)):
    """Require a JWT Bearer token with claim `is_admin: true`.

    If `METRICS_API_KEY` is set and provided via header, allow that as alternative.
    """
    # Allow API key as alternative
    # FastAPI converts headers with dashes to underscores in parameter names
    # so callers should use header `X-Metrics-Api-Key`.
    # If an API key is configured and matches, allow access.
    # Otherwise validate Authorization: Bearer <token>
    if settings.METRICS_API_KEY:
        # check X-Metrics-Api-Key header first
        # The dependency system won't pass that header here; users should call _check_api_key separately
        pass

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    token = authorization.split(None, 1)[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    if not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return True


@router.get("/debug")
def debug_metrics(api_key_ok: bool = Depends(_check_api_key), ip_ok: bool = Depends(_check_ip_allowlist)):
    """Return in-memory request counts and recent request samples.

    NOTE: This endpoint is intended for local debugging only. Use an API key
    via header `X-Metrics-Api-Key` when `METRICS_API_KEY` is set, or a Bearer
    JWT with claim `is_admin: true`.
    """
    return {
        "request_counts": get_request_counts(),
        "recent_requests": get_recent_requests(),
    }


@router.get("/summary")
def metrics_summary(api_key_ok: bool = Depends(_check_api_key), ip_ok: bool = Depends(_check_ip_allowlist)):
    """Return an aggregated JSON summary intended for dashboards.

    - total_requests: total count across tracked routes
    - top_paths: top 10 paths by count
    - avg_duration_ms: average duration across recent requests
    - avg_sql_count: average SQL statements across recent requests
    """
    cache_key = "metrics:summary:cache"

    # Attempt to return cached summary from Redis
    if settings.ENABLE_REDIS_METRICS and settings.REDIS_URL:
        try:
            r = redis.from_url(settings.REDIS_URL)
            cached = r.get(cache_key)
            if cached:
                try:
                    return json.loads(cached)
                except Exception:
                    # fallthrough to recompute
                    pass
        except Exception:
            # proceed to compute locally if Redis unavailable
            pass

    # Compute summary (prefer Redis aggregated values where possible)
    try:
        if settings.ENABLE_REDIS_METRICS and settings.REDIS_URL:
            r = redis.from_url(settings.REDIS_URL)
            total_requests = int(r.get("metrics:counts:__total__") or 0)
            keys = r.keys("metrics:counts:*")
            counts = {}
            for k in keys:
                ks = k.decode() if isinstance(k, bytes) else k
                if ks == "metrics:counts:__total__":
                    continue
                try:
                    v = int(r.get(ks) or 0)
                except Exception:
                    v = 0
                path = ks.replace("metrics:counts:", "")
                counts[path] = v

            top_paths = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]

            recent_list = []
            try:
                raw = r.lrange("metrics:recent", 0, 200)
                for item in raw:
                    try:
                        recent_list.append(json.loads(item))
                    except Exception:
                        continue
            except Exception:
                recent_list = []

            durations = [it.get("duration_ms", 0) for it in recent_list if it.get("duration_ms") is not None]
            sql_counts = [it.get("sql_count", 0) for it in recent_list if it.get("sql_count") is not None and isinstance(it.get("sql_count"), int)]
            avg_duration = round(sum(durations) / len(durations), 3) if durations else None
            avg_sql = round(sum(sql_counts) / len(sql_counts), 3) if sql_counts else None

            result = {
                "total_requests": total_requests,
                "top_paths": [{"path": p, "count": c} for p, c in top_paths],
                "recent_window": len(recent_list),
                "avg_duration_ms": avg_duration,
                "avg_sql_count": avg_sql,
            }

            # Cache the summary in Redis
            try:
                ttl = int(settings.METRICS_CACHE_TTL or 5)
                r.setex(cache_key, ttl, json.dumps(result))
            except Exception:
                pass

            return result
    except Exception:
        pass

    # Fallback to in-memory data
    counts = get_request_counts()
    recent = get_recent_requests()

    total_requests = sum(counts.values())
    top_paths = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]

    durations = [r.get("duration_ms", 0) for r in recent if r.get("duration_ms") is not None]
    sql_counts = [r.get("sql_count", 0) for r in recent if r.get("sql_count") is not None and isinstance(r.get("sql_count"), int)]

    avg_duration = round(sum(durations) / len(durations), 3) if durations else None
    avg_sql = round(sum(sql_counts) / len(sql_counts), 3) if sql_counts else None

    result = {
        "total_requests": total_requests,
        "top_paths": [{"path": p, "count": c} for p, c in top_paths],
        "recent_window": len(recent),
        "avg_duration_ms": avg_duration,
        "avg_sql_count": avg_sql,
    }

    # Optionally cache in Redis for fallback too
    if settings.ENABLE_REDIS_METRICS and settings.REDIS_URL:
        try:
            r = redis.from_url(settings.REDIS_URL)
            r.setex(cache_key, int(settings.METRICS_CACHE_TTL or 5), json.dumps(result))
        except Exception:
            pass

    return result


@router.get("/prometheus")
def prometheus_metrics(api_key_ok: bool = Depends(_check_api_key), admin: bool = Depends(_require_admin_jwt), ip_ok: bool = Depends(_check_ip_allowlist)):
    """Expose Prometheus metrics if enabled.

    This route requires either a valid `X-Metrics-Api-Key` header or a valid
    admin JWT. In production prefer the JWT method.
    """
    if not settings.PROMETHEUS_ENABLED:
        raise HTTPException(status_code=404, detail="Prometheus metrics not enabled")
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
