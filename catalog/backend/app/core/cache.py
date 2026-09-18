import json
from functools import lru_cache
from typing import Any

import redis

from app.core.config import get_settings


@lru_cache
def get_redis() -> redis.Redis:
    settings = get_settings()
    return redis.from_url(settings.redis_url, decode_responses=True)


def cache_get(key: str) -> Any | None:
    raw = get_redis().get(key)
    if raw is None:
        return None
    return json.loads(raw)


def cache_set(key: str, value: Any, ttl_seconds: int | None = None) -> None:
    settings = get_settings()
    get_redis().set(key, json.dumps(value), ex=ttl_seconds or settings.cache_ttl_seconds)


def cache_delete_prefix(prefix: str) -> None:
    client = get_redis()
    for key in client.scan_iter(f"{prefix}*"):
        client.delete(key)
