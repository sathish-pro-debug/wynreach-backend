import json

import pytest

from app.routers import metrics as metrics_mod
from app.core import config


class FakeRedis:
    def __init__(self):
        self.store = {}
        self.lists = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, val):
        # store as JSON/string like real Redis client
        self.store[key] = val

    def set(self, key, val):
        self.store[key] = val

    def keys(self, pattern):
        prefix = pattern.replace("*", "")
        return [k for k in self.store.keys() if k.startswith(prefix)]

    def lrange(self, name, start, end):
        vals = self.lists.get(name, [])
        # return JSON-encoded strings
        return [json.dumps(v) for v in vals]


def test_returns_cached_summary(monkeypatch):
    fake = FakeRedis()
    # Redis returns the cached blob directly
    fake.store["metrics:summary:cache"] = json.dumps({"cached": True})

    monkeypatch.setattr(metrics_mod.redis, "from_url", lambda url: fake)
    monkeypatch.setattr(config.settings, "ENABLE_REDIS_METRICS", True)
    monkeypatch.setattr(config.settings, "REDIS_URL", "redis://localhost:6379/0")

    result = metrics_mod.metrics_summary()
    assert result == {"cached": True}


def test_computes_and_writes_cache(monkeypatch):
    fake = FakeRedis()
    # Populate aggregated counters and recent list
    fake.store["metrics:counts:__total__"] = "10"
    fake.store["metrics:counts:/a"] = "7"
    fake.store["metrics:counts:/b"] = "3"
    fake.lists["metrics:recent"] = [
        {"duration_ms": 100, "sql_count": 2},
        {"duration_ms": 200, "sql_count": 4},
    ]

    monkeypatch.setattr(metrics_mod.redis, "from_url", lambda url: fake)
    monkeypatch.setattr(config.settings, "ENABLE_REDIS_METRICS", True)
    monkeypatch.setattr(config.settings, "REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setattr(config.settings, "METRICS_CACHE_TTL", 2)

    result = metrics_mod.metrics_summary()

    # Basic structure assertions
    assert result["total_requests"] == 10
    assert any(p["path"] == "/a" for p in result["top_paths"]) or any(p["path"] == "/a" for p in result["top_paths"])  # top paths present
    assert result["recent_window"] == 2
    assert result["avg_duration_ms"] == pytest.approx(150.0, rel=1e-3)
    assert result["avg_sql_count"] == pytest.approx(3.0, rel=1e-3)

    # Ensure the summary was cached in Redis
    assert "metrics:summary:cache" in fake.store
