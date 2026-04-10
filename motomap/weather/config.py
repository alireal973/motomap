"""Weather service configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class WeatherAPIConfig:
    api_key: str = field(default_factory=lambda: os.getenv("OPENWEATHER_API_KEY", ""))
    base_url: str = "https://api.openweathermap.org/data/2.5"
    timeout_seconds: float = 10.0
    retry_count: int = 3
    retry_delay_seconds: float = 1.0


@dataclass
class CacheConfig:
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    default_ttl_seconds: int = 300
    max_ttl_seconds: int = 900
    key_prefix: str = "motomap:weather:"


@dataclass
class RoadConditionThresholds:
    light_rain_threshold: float = 2.5
    moderate_rain_threshold: float = 7.5
    heavy_rain_threshold: float = 15.0
    light_snow_threshold: float = 1.0
    moderate_snow_threshold: float = 4.0
    heavy_snow_threshold: float = 10.0
    freezing_point: float = 0.0
    cold_threshold: float = 5.0
    optimal_low: float = 15.0
    optimal_high: float = 30.0
    hot_threshold: float = 35.0
    light_wind: float = 5.0
    moderate_wind: float = 10.0
    strong_wind: float = 15.0
    dangerous_wind: float = 20.0
    excellent_visibility: int = 10000
    good_visibility: int = 5000
    moderate_visibility: int = 2000
    poor_visibility: int = 1000
    dangerous_visibility: int = 500
    low_humidity: float = 30.0
    moderate_humidity: float = 60.0
    high_humidity: float = 80.0


@dataclass
class LaneSplittingModifiers:
    dry_roads: float = 1.0
    wet_roads_light: float = 0.6
    wet_roads_moderate: float = 0.3
    wet_roads_heavy: float = 0.0
    light_snow: float = 0.2
    moderate_snow: float = 0.0
    heavy_snow: float = 0.0
    icy_conditions: float = 0.0
    excellent_visibility: float = 1.0
    good_visibility: float = 0.9
    moderate_visibility: float = 0.6
    poor_visibility: float = 0.3
    dangerous_visibility: float = 0.0
    light_wind: float = 1.0
    moderate_wind: float = 0.8
    strong_wind: float = 0.5
    dangerous_wind: float = 0.0
    freezing: float = 0.2
    cold: float = 0.8
    optimal: float = 1.0
    hot: float = 0.9
    extreme_hot: float = 0.7


@dataclass
class WeatherConfig:
    api: WeatherAPIConfig = field(default_factory=WeatherAPIConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    thresholds: RoadConditionThresholds = field(default_factory=RoadConditionThresholds)
    modifiers: LaneSplittingModifiers = field(default_factory=LaneSplittingModifiers)
    enable_caching: bool = True
    enable_wind_assessment: bool = True
    enable_visibility_assessment: bool = True
    enable_temperature_assessment: bool = True
    log_api_calls: bool = True
    log_cache_hits: bool = False

    @classmethod
    def from_env(cls) -> "WeatherConfig":
        return cls(
            api=WeatherAPIConfig(
                api_key=os.getenv("OPENWEATHER_API_KEY", ""),
                timeout_seconds=float(os.getenv("WEATHER_API_TIMEOUT", "10")),
            ),
            cache=CacheConfig(
                redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
                default_ttl_seconds=int(os.getenv("WEATHER_CACHE_TTL", "300")),
            ),
            enable_caching=os.getenv("WEATHER_CACHE_ENABLED", "true").lower() == "true",
        )
