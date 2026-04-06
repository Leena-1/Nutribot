from __future__ import annotations

from functools import lru_cache

from backend.config import get_settings
from backend.utils.cache import RedisJsonCache, TTLCache


@lru_cache(maxsize=1)
def get_cache():
    s = get_settings()
    if s.redis_url:
        return RedisJsonCache(s.redis_url, ttl_seconds=s.cache_ttl_seconds)
    return TTLCache(ttl_seconds=s.cache_ttl_seconds)

