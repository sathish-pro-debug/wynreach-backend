import time
import logging
import threading
import contextvars
from collections import deque
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import event

from app.database import main_engine
from app.core.config import settings
import json
try:
    import redis
except Exception:
    redis = None

logger = logging.getLogger("middleware.metrics")

# Context variable to store SQL statement samples for this request (list of dicts)
sql_stmt_samples = contextvars.ContextVar("sql_stmt_samples", default=None)

# Global request counters per path
request_counts = {}
request_counts_lock = threading.Lock()

# Recent requests ring buffer storing last N request summaries
RECENT_REQUESTS_MAX = 200
recent_requests = deque(maxlen=RECENT_REQUESTS_MAX)
recent_requests_lock = threading.Lock()

# Prometheus metric placeholders (populated in registration if prometheus_client available)
REQUEST_COUNTER = None
REQUEST_LATENCY = None
DB_STATEMENTS = None


def _register_sql_event_listeners():
    """Register SQLAlchemy event listeners to record timing and sample statements."""

    @event.listens_for(main_engine, "before_cursor_execute")
    def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        # store start time on connection info stack
        conn.info.setdefault("query_start_time", []).append(time.perf_counter())

    @event.listens_for(main_engine, "after_cursor_execute")
    def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        try:
            start = conn.info.get("query_start_time", []).pop(-1)
        except Exception:
            start = None
        duration = (time.perf_counter() - start) if start else None

        # Append sample to the current request contextvar list (best-effort)
        try:
            s = sql_stmt_samples.get()
            if s is None:
                s = []
                sql_stmt_samples.set(s)
            # store truncated statement and duration
            sample = {
                "statement": (statement[:1000] + "...") if statement and len(statement) > 1000 else statement,
                "duration_ms": round(duration * 1000, 3) if duration is not None else None,
            }
            s.append(sample)
        except Exception:
            # best-effort; don't raise
            pass


    # Prometheus metrics objects (lazy import)
    global REQUEST_COUNTER, REQUEST_LATENCY, DB_STATEMENTS
    try:
        from prometheus_client import Counter, Histogram

        REQUEST_COUNTER = Counter("app_requests_total", "Total HTTP requests", ["method", "path", "status"])
        REQUEST_LATENCY = Histogram("app_request_duration_seconds", "HTTP request latency seconds", ["method", "path"])  # seconds
        DB_STATEMENTS = Counter("app_db_statements_total", "Total DB statements executed")
    except Exception:
        REQUEST_COUNTER = None
        REQUEST_LATENCY = None
        DB_STATEMENTS = None


class SQLCountMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Register listeners once
        _register_sql_event_listeners()

    async def dispatch(self, request, call_next):
        # initialize sql samples list for this request
        token = sql_stmt_samples.set([])
        path = request.url.path
        start = time.perf_counter()
        status_code = None
        try:
            response = await call_next(request)
            status_code = getattr(response, "status_code", None)
            return response
        finally:
            duration = time.perf_counter() - start
            try:
                samples = sql_stmt_samples.get()
                sql_count = len(samples) if isinstance(samples, list) else -1
            except Exception:
                samples = []
                sql_count = -1

            # update global request counts
            with request_counts_lock:
                request_counts[path] = request_counts.get(path, 0) + 1

            # record recent request summary
            summary = {
                "method": request.method,
                "path": path,
                "status": status_code,
                "duration_ms": round(duration * 1000, 3),
                "sql_count": sql_count,
                "top_statements": sorted(samples, key=lambda x: (x.get("duration_ms") or 0), reverse=True)[:5],
            }
            try:
                with recent_requests_lock:
                    recent_requests.appendleft(summary)
            except Exception:
                pass

            # Redis aggregation (best-effort)
            try:
                if settings.ENABLE_REDIS_METRICS and settings.REDIS_URL and redis is not None:
                    r = redis.from_url(settings.REDIS_URL)
                    # push recent summary
                    r.lpush("metrics:recent", json.dumps(summary))
                    r.ltrim("metrics:recent", 0, RECENT_REQUESTS_MAX - 1)
                    # increment path counter
                    r.incr(f"metrics:counts:{path}")
                    # increment total
                    r.incr("metrics:counts:__total__")
                    # set TTL for list key
                    r.expire("metrics:recent", 60 * 60 * 24)
            except Exception:
                pass
            logger.info(
                "%s %s completed status=%s duration=%0.3fs sql_count=%s",
                request.method,
                path,
                status_code,
                duration,
                sql_count,
            )

            # update prometheus metrics if available
            try:
                if REQUEST_COUNTER is not None:
                    REQUEST_COUNTER.labels(method=request.method, path=path, status=str(status_code)).inc()
                if REQUEST_LATENCY is not None:
                    REQUEST_LATENCY.labels(method=request.method, path=path).observe(duration)
                if DB_STATEMENTS is not None and isinstance(sql_count, int) and sql_count > 0:
                    DB_STATEMENTS.inc(sql_count)
            except Exception:
                pass

            # reset contextvar
            try:
                sql_stmt_samples.reset(token)
            except Exception:
                pass


def get_request_counts():
    with request_counts_lock:
        return dict(request_counts)


def get_recent_requests():
    with recent_requests_lock:
        return list(recent_requests)
