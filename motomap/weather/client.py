"""OpenWeatherMap API client."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import httpx

from .models import WeatherCondition, WeatherData
from .config import WeatherConfig
from .cache import WeatherCache

logger = logging.getLogger(__name__)


class WeatherAPIError(Exception):
    pass

class WeatherAPIConnectionError(WeatherAPIError):
    pass

class WeatherAPIRateLimitError(WeatherAPIError):
    pass

class WeatherAPIInvalidKeyError(WeatherAPIError):
    pass


class WeatherService:
    CONDITION_MAPPING: Dict[str, WeatherCondition] = {
        "Clear": WeatherCondition.CLEAR,
        "Clouds": WeatherCondition.CLOUDS,
        "Rain": WeatherCondition.RAIN,
        "Drizzle": WeatherCondition.DRIZZLE,
        "Thunderstorm": WeatherCondition.THUNDERSTORM,
        "Snow": WeatherCondition.SNOW,
        "Mist": WeatherCondition.MIST,
        "Fog": WeatherCondition.FOG,
        "Haze": WeatherCondition.HAZE,
        "Dust": WeatherCondition.DUST,
        "Sand": WeatherCondition.SAND,
        "Tornado": WeatherCondition.TORNADO,
    }

    def __init__(self, config: Optional[WeatherConfig] = None, cache: Optional[WeatherCache] = None):
        self.config = config or WeatherConfig.from_env()
        self._cache = cache
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def cache(self) -> Optional[WeatherCache]:
        if not self.config.enable_caching:
            return None
        if self._cache is None:
            self._cache = WeatherCache(self.config.cache)
        return self._cache

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.api.timeout_seconds),
                headers={"Accept": "application/json"},
            )
        return self._client

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        if self._cache is not None:
            await self._cache.close()

    async def __aenter__(self) -> "WeatherService":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _build_cache_key(self, lat: float, lng: float) -> str:
        return f"weather:{round(lat, 2)}:{round(lng, 2)}"

    async def get_weather(self, lat: float, lng: float, force_refresh: bool = False) -> WeatherData:
        if not (-90 <= lat <= 90):
            raise ValueError(f"Invalid latitude: {lat}")
        if not (-180 <= lng <= 180):
            raise ValueError(f"Invalid longitude: {lng}")

        if not force_refresh and self.cache is not None:
            cache_key = self._build_cache_key(lat, lng)
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        weather_data = await self._fetch_with_retry(lat, lng)

        if self.cache is not None:
            cache_key = self._build_cache_key(lat, lng)
            await self.cache.set(cache_key, weather_data)

        return weather_data

    async def _fetch_with_retry(self, lat: float, lng: float) -> WeatherData:
        last_error: Optional[Exception] = None
        for attempt in range(self.config.api.retry_count):
            try:
                return await self._fetch_weather(lat, lng)
            except (WeatherAPIRateLimitError, WeatherAPIInvalidKeyError):
                raise
            except WeatherAPIError as e:
                last_error = e
                if attempt < self.config.api.retry_count - 1:
                    delay = self.config.api.retry_delay_seconds * (2 ** attempt)
                    logger.warning(f"Weather API failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
        raise WeatherAPIConnectionError(f"Failed after {self.config.api.retry_count} attempts: {last_error}")

    async def _fetch_weather(self, lat: float, lng: float) -> WeatherData:
        if not self.config.api.api_key:
            raise WeatherAPIInvalidKeyError("OPENWEATHER_API_KEY not configured")

        url = f"{self.config.api.base_url}/weather"
        params = {"lat": lat, "lon": lng, "appid": self.config.api.api_key, "units": "metric"}

        try:
            client = await self._get_client()
            response = await client.get(url, params=params)
        except httpx.TimeoutException as e:
            raise WeatherAPIConnectionError(f"Timeout: {e}")
        except httpx.RequestError as e:
            raise WeatherAPIConnectionError(f"Connection error: {e}")

        if response.status_code == 401:
            raise WeatherAPIInvalidKeyError("Invalid API key")
        if response.status_code == 429:
            raise WeatherAPIRateLimitError("Rate limit exceeded")
        if response.status_code != 200:
            raise WeatherAPIError(f"Status {response.status_code}: {response.text}")

        return self._parse_response(response.json(), lat, lng)

    def _parse_response(self, data: Dict[str, Any], lat: float, lng: float) -> WeatherData:
        weather_list = data.get("weather", [])
        main_condition = weather_list[0].get("main", "Clear") if weather_list else "Clear"
        condition = self.CONDITION_MAPPING.get(main_condition, WeatherCondition.CLEAR)

        main_data = data.get("main", {})
        wind_data = data.get("wind", {})
        rain_data = data.get("rain", {})
        snow_data = data.get("snow", {})
        clouds_data = data.get("clouds", {})

        return WeatherData(
            condition=condition,
            temperature_celsius=main_data.get("temp", 20.0),
            humidity_percent=main_data.get("humidity", 50.0),
            wind_speed_ms=wind_data.get("speed", 0.0),
            wind_gust_ms=wind_data.get("gust"),
            visibility_meters=data.get("visibility", 10000),
            precipitation_mm=rain_data.get("1h", 0.0),
            snow_mm=snow_data.get("1h", 0.0),
            clouds_percent=clouds_data.get("all", 0),
            timestamp=datetime.now(timezone.utc),
            location_lat=lat,
            location_lng=lng,
        )

    async def get_weather_along_route(self, coordinates: list[tuple[float, float]], sample_interval: int = 10) -> list[WeatherData]:
        sampled = coordinates[::sample_interval]
        if coordinates and coordinates[-1] not in sampled:
            sampled.append(coordinates[-1])
        tasks = [self.get_weather(lat, lng) for lat, lng in sampled]
        return await asyncio.gather(*tasks)

    async def get_worst_weather_along_route(self, coordinates: list[tuple[float, float]], sample_interval: int = 10) -> WeatherData:
        weather_list = await self.get_weather_along_route(coordinates, sample_interval)
        if not weather_list:
            return WeatherData(
                condition=WeatherCondition.CLEAR, temperature_celsius=20.0,
                humidity_percent=50.0, wind_speed_ms=0.0, wind_gust_ms=None,
                visibility_meters=10000, precipitation_mm=0.0, snow_mm=0.0,
                clouds_percent=0, timestamp=datetime.now(timezone.utc),
                location_lat=coordinates[0][0] if coordinates else 0.0,
                location_lng=coordinates[0][1] if coordinates else 0.0,
            )
        worst = weather_list[0]
        for w in weather_list[1:]:
            if w.snow_mm > worst.snow_mm or w.precipitation_mm > worst.precipitation_mm or w.visibility_meters < worst.visibility_meters or w.wind_speed_ms > worst.wind_speed_ms:
                worst = w
        return worst
