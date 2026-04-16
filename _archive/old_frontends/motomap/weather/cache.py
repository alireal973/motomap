"""Redis-based caching for weather data."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from .models import WeatherCondition, WeatherData
from .config import CacheConfig

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class WeatherCache:
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._redis = None
        self._memory_cache: dict[str, tuple[WeatherData, float]] = {}
        self._use_redis = REDIS_AVAILABLE

    async def _get_redis(self):
        if not self._use_redis:
            return None
        if self._redis is None:
            try:
                self._redis = aioredis.from_url(self.config.redis_url, decode_responses=True)
                await self._redis.ping()
            except Exception as e:
                logger.warning(f"Redis unavailable, using memory cache: {e}")
                self._use_redis = False
                self._redis = None
        return self._redis

    async def close(self):
        if self._redis is not None:
            await self._redis.close()
            self._redis = None

    def _serialize(self, data: WeatherData) -> str:
        return json.dumps({
            "condition": data.condition.value,
            "temperature_celsius": data.temperature_celsius,
            "humidity_percent": data.humidity_percent,
            "wind_speed_ms": data.wind_speed_ms,
            "wind_gust_ms": data.wind_gust_ms,
            "visibility_meters": data.visibility_meters,
            "precipitation_mm": data.precipitation_mm,
            "snow_mm": data.snow_mm,
            "clouds_percent": data.clouds_percent,
            "timestamp": data.timestamp.isoformat(),
            "location_lat": data.location_lat,
            "location_lng": data.location_lng,
        })

    def _deserialize(self, data_str: str) -> WeatherData:
        data = json.loads(data_str)
        return WeatherData(
            condition=WeatherCondition(data["condition"]),
            temperature_celsius=data["temperature_celsius"],
            humidity_percent=data["humidity_percent"],
            wind_speed_ms=data["wind_speed_ms"],
            wind_gust_ms=data["wind_gust_ms"],
            visibility_meters=data["visibility_meters"],
            precipitation_mm=data["precipitation_mm"],
            snow_mm=data["snow_mm"],
            clouds_percent=data["clouds_percent"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            location_lat=data["location_lat"],
            location_lng=data["location_lng"],
        )

    async def get(self, key: str) -> Optional[WeatherData]:
        full_key = f"{self.config.key_prefix}{key}"
        redis_client = await self._get_redis()
        if redis_client is not None:
            try:
                data_str = await redis_client.get(full_key)
                if data_str:
                    return self._deserialize(data_str)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")

        if full_key in self._memory_cache:
            data, expires_at = self._memory_cache[full_key]
            if datetime.now(timezone.utc).timestamp() < expires_at:
                return data
            del self._memory_cache[full_key]
        return None

    async def set(self, key: str, data: WeatherData, ttl_seconds: Optional[int] = None):
        full_key = f"{self.config.key_prefix}{key}"
        ttl = min(ttl_seconds or self.config.default_ttl_seconds, self.config.max_ttl_seconds)

        redis_client = await self._get_redis()
        if redis_client is not None:
            try:
                await redis_client.setex(full_key, ttl, self._serialize(data))
                return
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")

        expires_at = datetime.now(timezone.utc).timestamp() + ttl
        self._memory_cache[full_key] = (data, expires_at)
        if len(self._memory_cache) > 1000:
            self._cleanup()

    def _cleanup(self):
        now = datetime.now(timezone.utc).timestamp()
        expired = [k for k, (_, exp) in self._memory_cache.items() if exp < now]
        for k in expired:
            del self._memory_cache[k]
