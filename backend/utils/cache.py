from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class _Entry:
    value: Any
    expires_at: float


class TTLCache:
    """Simple in-memory TTL cache (single-process)."""

    def __init__(self, *, ttl_seconds: int = 3600, max_items: int = 2048):
        self._ttl = max(1, int(ttl_seconds))
        self._max = max(1, int(max_items))
        self._data: Dict[str, _Entry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            e = self._data.get(key)
            if e is None:
                return None
            if e.expires_at <= time.time():
                self._data.pop(key, None)
                return None
            return e.value

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            if len(self._data) >= self._max:
                # naive eviction: drop oldest expiry
                oldest = min(self._data.items(), key=lambda kv: kv[1].expires_at)[0]
                self._data.pop(oldest, None)
            self._data[key] = _Entry(value=value, expires_at=time.time() + self._ttl)


class RedisJsonCache:
    """
    Redis JSON cache.
    Requires `redis` package. Stores values as JSON strings.
    """

    def __init__(self, redis_url: str, *, ttl_seconds: int = 3600, key_prefix: str = "nutribot:"):
        self._url = redis_url
        self._ttl = max(1, int(ttl_seconds))
        self._prefix = key_prefix
        self._client = None

    async def _get_client(self):
        if self._client is None:
            import redis.asyncio as redis  # type: ignore

            self._client = redis.from_url(self._url, encoding="utf-8", decode_responses=True)
        return self._client

    def _k(self, key: str) -> str:
        return f"{self._prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        client = await self._get_client()
        raw = await client.get(self._k(key))
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    async def set(self, key: str, value: Any) -> None:
        client = await self._get_client()
        await client.set(self._k(key), json.dumps(value, ensure_ascii=False), ex=self._ttl)

