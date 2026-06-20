from app.core.redis import redis_client

DAILY_LIMIT = 5000

def check_rate_limit(tenant_id):

    key = f"tenant_daily:{tenant_id}"

    current = redis_client.incr(key)

    if current == 1:
        redis_client.expire(key, 86400)

    if current > DAILY_LIMIT:
        raise Exception(
            "Daily email limit exceeded"
        )