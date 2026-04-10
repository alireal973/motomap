"""Redis cache layer with in-memory fallback."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


class CacheBackend:
    def __init__(self, url: str = REDIS_URL, prefix: str = "motomap:"):
        self._url = url
        self._prefix = prefix
        self._redis: Optional[Any] = None
        self._use_redis = REDIS_AVAILABLE
        self._memory: dict[str, tuple[str, float]] = {}

    async def connect(self) -> None:
        if not self._use_redis:
            logger.info("Redis not available, using in-memory cache")
            return
        try:
            self._redis = aioredis.from_url(self._url, decode_responses=True)
            await self._redis.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning("Redis connect failed, falling back to memory: %s", e)
            self._use_redis = False
            self._redis = None

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()
            self._redis = None

    def _key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    async def get(self, key: str) -> Optional[str]:
        fk = self._key(key)
        if self._redis:
            try:
                return await self._redis.get(fk)
            except Exception:
                pass
        if fk in self._memory:
            val, exp = self._memory[fk]
            if datetime.now(timezone.utc).timestamp() < exp:
                return val
            del self._memory[fk]
        return None

    async def set(self, key: str, value: str, ttl: int = 300) -> None:
        fk = self._key(key)
        if self._redis:
            try:
                await self._redis.setex(fk, ttl, value)
                return
            except Exception:
                pass
        self._memory[fk] = (value, datetime.now(timezone.utc).timestamp() + ttl)
        if len(self._memory) > 5000:
            self._evict()

    async def delete(self, key: str) -> None:
        fk = self._key(key)
        if self._redis:
            try:
                await self._redis.delete(fk)
            except Exception:
                pass
        self._memory.pop(fk, None)

    async def get_json(self, key: str) -> Optional[Any]:
        raw = await self.get(key)
        return json.loads(raw) if raw else None

    async def set_json(self, key: str, value: Any, ttl: int = 300) -> None:
        await self.set(key, json.dumps(value, default=str), ttl)

    def _evict(self) -> None:
        now = datetime.now(timezone.utc).timestamp()
        expired = [k for k, (_, exp) in self._memory.items() if exp < now]
        for k in expired:
            del self._memory[k]
        if len(self._memory) > 5000:
            oldest = sorted(self._memory, key=lambda k: self._memory[k][1])
            for k in oldest[:1000]:
                del self._memory[k]


cache = CacheBackend()
