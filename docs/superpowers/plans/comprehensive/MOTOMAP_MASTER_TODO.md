# MotoMap Comprehensive Feature Implementation Plan
# =================================================
# Date: 2026-04-05
# Version: 2.0.0
# Status: Master Implementation Blueprint
# Target: 10,000+ lines comprehensive development roadmap

---

## Executive Summary

This document outlines the complete implementation plan for MotoMap's next-generation features including:

1. **Weather-Aware Lane Splitting** - Real-time weather integration affecting routing recommendations
2. **Visual Route Safety Overlay** - Color-coded route segments (green/yellow/red) for lane splitting suitability
3. **User Authentication & Profiles** - Complete user management with motorcycle garage
4. **Community Platform** - Brand-based communities, chat, and mutual assistance
5. **Crowdsourced Road Reports** - User-submitted warnings, hazards, and road conditions
6. **Gamification System** - Points, badges, leaderboards, and achievements

---

## Table of Contents

1. [Module 1: Weather Integration System](#module-1-weather-integration-system)
2. [Module 2: Visual Route Safety Overlay](#module-2-visual-route-safety-overlay)
3. [Module 3: User Authentication & Database](#module-3-user-authentication--database)
4. [Module 4: User Profile & Motorcycle Garage](#module-4-user-profile--motorcycle-garage)
5. [Module 5: Community Platform](#module-5-community-platform)
6. [Module 6: Road Reports & Warnings](#module-6-road-reports--warnings)
7. [Module 7: Gamification System](#module-7-gamification-system)
8. [Module 8: Backend API Extensions](#module-8-backend-api-extensions)
9. [Module 9: Mobile App Screens](#module-9-mobile-app-screens)
10. [Module 10: Testing & Quality Assurance](#module-10-testing--quality-assurance)
11. [Module 11: DevOps & Deployment](#module-11-devops--deployment)
12. [Module 12: Documentation](#module-12-documentation)

---

# MODULE 1: WEATHER INTEGRATION SYSTEM
# =====================================

## 1.1 Overview

The weather integration system will fetch real-time meteorological data and use it to dynamically
adjust lane splitting recommendations, route safety scores, and provide weather-aware navigation.

## 1.2 Architecture

`
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WEATHER INTEGRATION ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────────────┐   │
│  │ OpenWeather  │───▶│ Weather Service  │───▶│ Lane Split Calculator    │   │
│  │ API          │    │ (Python)         │    │ (algorithm.py)           │   │
│  └──────────────┘    └──────────────────┘    └──────────────────────────┘   │
│         │                    │                          │                    │
│         ▼                    ▼                          ▼                    │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────────────┐   │
│  │ Weather      │    │ Redis Cache      │    │ Route Safety Modifier    │   │
│  │ Response     │    │ (5 min TTL)      │    │ (Wet road penalty etc)   │   │
│  └──────────────┘    └──────────────────┘    └──────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
`

## 1.3 Weather Data Model

### 1.3.1 Python Data Classes

`python
# File: motomap/weather/models.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime

class WeatherCondition(Enum):
    CLEAR = "clear"
    CLOUDS = "clouds"
    RAIN = "rain"
    DRIZZLE = "drizzle"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    MIST = "mist"
    FOG = "fog"
    HAZE = "haze"
    DUST = "dust"
    SAND = "sand"
    TORNADO = "tornado"

class RoadSurfaceCondition(Enum):
    DRY = "dry"
    WET = "wet"
    ICY = "icy"
    SNOWY = "snowy"
    FLOODED = "flooded"

@dataclass
class WeatherData:
    condition: WeatherCondition
    temperature_celsius: float
    humidity_percent: float
    wind_speed_ms: float
    wind_gust_ms: Optional[float]
    visibility_meters: int
    precipitation_mm: float
    snow_mm: float
    clouds_percent: int
    timestamp: datetime
    location_lat: float
    location_lng: float

@dataclass
class RoadConditionAssessment:
    surface_condition: RoadSurfaceCondition
    grip_factor: float  # 0.0 to 1.0
    visibility_factor: float  # 0.0 to 1.0
    wind_risk_factor: float  # 0.0 to 1.0
    overall_safety_score: float  # 0.0 to 1.0
    lane_splitting_modifier: float  # 0.0 to 1.0 (multiplier)
    warnings: list[str]
`

---

## 1.4 Implementation Tasks

### TASK 1.4.1: Create Weather Module Directory Structure
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 30 minutes
- [ ] **Dependencies:** None

**Description:**
Create the weather module directory structure within the motomap package.

**Files to Create:**
`
motomap/
├── weather/
│   ├── __init__.py
│   ├── models.py
│   ├── client.py
│   ├── cache.py
│   ├── assessment.py
│   └── config.py
`

**Implementation Details:**

`python
# File: motomap/weather/__init__.py

"""
MotoMap Weather Integration Module
==================================

This module provides real-time weather data integration for
motorcycle-aware routing decisions.

Features:
- OpenWeatherMap API integration
- Redis-based caching (5 minute TTL)
- Road surface condition assessment
- Lane splitting safety modifiers
- Wind risk calculations for motorcycles

Usage:
    from motomap.weather import WeatherService, RoadConditionAssessor
    
    weather_service = WeatherService()
    weather_data = await weather_service.get_weather(lat=41.0082, lng=28.9784)
    
    assessor = RoadConditionAssessor()
    road_condition = assessor.assess(weather_data)
    
    if road_condition.lane_splitting_modifier < 0.5:
        print("Lane splitting not recommended due to weather")
"""

from .models import (
    WeatherCondition,
    RoadSurfaceCondition,
    WeatherData,
    RoadConditionAssessment,
)
from .client import WeatherService
from .assessment import RoadConditionAssessor
from .cache import WeatherCache
from .config import WeatherConfig

__all__ = [
    "WeatherCondition",
    "RoadSurfaceCondition",
    "WeatherData",
    "RoadConditionAssessment",
    "WeatherService",
    "RoadConditionAssessor",
    "WeatherCache",
    "WeatherConfig",
]

__version__ = "1.0.0"
`

**Acceptance Criteria:**
- [ ] All files created with proper docstrings
- [ ] Module imports work correctly
- [ ] Type hints are complete
- [ ] Unit tests pass

---

### TASK 1.4.2: Implement Weather Configuration
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 45 minutes
- [ ] **Dependencies:** TASK 1.4.1

**Description:**
Create configuration management for weather service including API keys,
cache settings, and threshold values.

**Implementation:**

`python
# File: motomap/weather/config.py

"""
Weather service configuration and thresholds.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class WeatherAPIConfig:
    """OpenWeatherMap API configuration."""
    
    api_key: str = field(default_factory=lambda: os.getenv("OPENWEATHER_API_KEY", ""))
    base_url: str = "https://api.openweathermap.org/data/2.5"
    timeout_seconds: float = 10.0
    retry_count: int = 3
    retry_delay_seconds: float = 1.0

@dataclass
class CacheConfig:
    """Redis cache configuration for weather data."""
    
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    default_ttl_seconds: int = 300  # 5 minutes
    max_ttl_seconds: int = 900  # 15 minutes
    key_prefix: str = "motomap:weather:"
    
@dataclass
class RoadConditionThresholds:
    """
    Thresholds for determining road conditions and safety modifiers.
    
    These values are calibrated based on motorcycle safety research and
    real-world riding conditions.
    """
    
    # Precipitation thresholds (mm/hour)
    light_rain_threshold: float = 2.5
    moderate_rain_threshold: float = 7.5
    heavy_rain_threshold: float = 15.0
    
    # Snow thresholds (mm/hour)
    light_snow_threshold: float = 1.0
    moderate_snow_threshold: float = 4.0
    heavy_snow_threshold: float = 10.0
    
    # Temperature thresholds (Celsius)
    freezing_point: float = 0.0
    cold_threshold: float = 5.0
    optimal_low: float = 15.0
    optimal_high: float = 30.0
    hot_threshold: float = 35.0
    
    # Wind thresholds (m/s)
    light_wind: float = 5.0
    moderate_wind: float = 10.0
    strong_wind: float = 15.0
    dangerous_wind: float = 20.0
    
    # Visibility thresholds (meters)
    excellent_visibility: int = 10000
    good_visibility: int = 5000
    moderate_visibility: int = 2000
    poor_visibility: int = 1000
    dangerous_visibility: int = 500
    
    # Humidity thresholds (percent)
    low_humidity: float = 30.0
    moderate_humidity: float = 60.0
    high_humidity: float = 80.0
    
@dataclass
class LaneSplittingModifiers:
    """
    Lane splitting safety modifiers based on weather conditions.
    
    These modifiers are multiplied with the base lane splitting distance
    to reduce recommendations during adverse weather.
    
    1.0 = No change (ideal conditions)
    0.0 = Lane splitting completely disabled
    """
    
    # Base condition modifiers
    dry_roads: float = 1.0
    wet_roads_light: float = 0.6
    wet_roads_moderate: float = 0.3
    wet_roads_heavy: float = 0.0
    
    # Snow/Ice modifiers (overrides rain)
    light_snow: float = 0.2
    moderate_snow: float = 0.0
    heavy_snow: float = 0.0
    icy_conditions: float = 0.0
    
    # Visibility modifiers (minimum applied)
    excellent_visibility: float = 1.0
    good_visibility: float = 0.9
    moderate_visibility: float = 0.6
    poor_visibility: float = 0.3
    dangerous_visibility: float = 0.0
    
    # Wind modifiers (additional reduction)
    light_wind: float = 1.0
    moderate_wind: float = 0.8
    strong_wind: float = 0.5
    dangerous_wind: float = 0.0
    
    # Temperature modifiers
    freezing: float = 0.2  # Ice risk even without precipitation
    cold: float = 0.8
    optimal: float = 1.0
    hot: float = 0.9  # Slight reduction due to fatigue risk
    extreme_hot: float = 0.7
    
@dataclass
class WeatherConfig:
    """
    Master configuration for weather integration.
    
    Usage:
        config = WeatherConfig()
        # Or with custom settings:
        config = WeatherConfig(
            api=WeatherAPIConfig(api_key="your_key"),
            cache=CacheConfig(default_ttl_seconds=600)
        )
    """
    
    api: WeatherAPIConfig = field(default_factory=WeatherAPIConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    thresholds: RoadConditionThresholds = field(default_factory=RoadConditionThresholds)
    modifiers: LaneSplittingModifiers = field(default_factory=LaneSplittingModifiers)
    
    # Feature flags
    enable_caching: bool = True
    enable_wind_assessment: bool = True
    enable_visibility_assessment: bool = True
    enable_temperature_assessment: bool = True
    
    # Logging
    log_api_calls: bool = True
    log_cache_hits: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            "api": {
                "base_url": self.api.base_url,
                "timeout_seconds": self.api.timeout_seconds,
                "retry_count": self.api.retry_count,
            },
            "cache": {
                "default_ttl_seconds": self.cache.default_ttl_seconds,
                "max_ttl_seconds": self.cache.max_ttl_seconds,
            },
            "feature_flags": {
                "enable_caching": self.enable_caching,
                "enable_wind_assessment": self.enable_wind_assessment,
                "enable_visibility_assessment": self.enable_visibility_assessment,
                "enable_temperature_assessment": self.enable_temperature_assessment,
            },
        }
    
    @classmethod
    def from_env(cls) -> "WeatherConfig":
        """Create configuration from environment variables."""
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
`

**Acceptance Criteria:**
- [ ] All configuration classes implemented
- [ ] Environment variable fallbacks work
- [ ] Threshold values are reasonable for motorcycle safety
- [ ] Configuration can be serialized to JSON
- [ ] Unit tests cover all scenarios

---

### TASK 1.4.3: Implement Weather API Client
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** TASK 1.4.1, TASK 1.4.2

**Description:**
Create the OpenWeatherMap API client with retry logic, error handling,
and response parsing.

**Implementation:**

`python
# File: motomap/weather/client.py

"""
OpenWeatherMap API client with retry logic and error handling.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import httpx

from .models import WeatherCondition, WeatherData
from .config import WeatherConfig, WeatherAPIConfig
from .cache import WeatherCache

logger = logging.getLogger(__name__)

class WeatherAPIError(Exception):
    """Base exception for weather API errors."""
    pass

class WeatherAPIConnectionError(WeatherAPIError):
    """Raised when unable to connect to the weather API."""
    pass

class WeatherAPIRateLimitError(WeatherAPIError):
    """Raised when API rate limit is exceeded."""
    pass

class WeatherAPIInvalidKeyError(WeatherAPIError):
    """Raised when API key is invalid or missing."""
    pass

class WeatherService:
    """
    OpenWeatherMap API client service.
    
    Provides real-time weather data for motorcycle routing decisions.
    Includes caching, retry logic, and comprehensive error handling.
    
    Usage:
        service = WeatherService()
        weather = await service.get_weather(lat=41.0082, lng=28.9784)
        print(f"Current condition: {weather.condition}")
        print(f"Temperature: {weather.temperature_celsius}°C")
    """
    
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
    
    def __init__(
        self,
        config: Optional[WeatherConfig] = None,
        cache: Optional[WeatherCache] = None,
    ):
        """
        Initialize the weather service.
        
        Args:
            config: Weather configuration. Uses defaults if not provided.
            cache: Weather cache instance. Created automatically if not provided.
        """
        self.config = config or WeatherConfig.from_env()
        self._cache = cache
        self._client: Optional[httpx.AsyncClient] = None
        
    @property
    def cache(self) -> Optional[WeatherCache]:
        """Get the weather cache if caching is enabled."""
        if not self.config.enable_caching:
            return None
        if self._cache is None:
            self._cache = WeatherCache(self.config.cache)
        return self._cache
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.api.timeout_seconds),
                headers={"Accept": "application/json"},
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client and cache connections."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        if self._cache is not None:
            await self._cache.close()
    
    async def __aenter__(self) -> "WeatherService":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    def _build_cache_key(self, lat: float, lng: float) -> str:
        """
        Build cache key for weather data.
        
        Uses 2 decimal places for location (roughly 1km precision)
        to allow cache hits for nearby requests.
        """
        lat_rounded = round(lat, 2)
        lng_rounded = round(lng, 2)
        return f"weather:{lat_rounded}:{lng_rounded}"
    
    async def get_weather(
        self,
        lat: float,
        lng: float,
        force_refresh: bool = False,
    ) -> WeatherData:
        """
        Get current weather for a location.
        
        Args:
            lat: Latitude (-90 to 90)
            lng: Longitude (-180 to 180)
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            WeatherData object with current conditions
            
        Raises:
            WeatherAPIError: If unable to fetch weather data
            ValueError: If coordinates are invalid
        """
        # Validate coordinates
        if not (-90 <= lat <= 90):
            raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
        if not (-180 <= lng <= 180):
            raise ValueError(f"Invalid longitude: {lng}. Must be between -180 and 180.")
        
        # Check cache first
        if not force_refresh and self.cache is not None:
            cache_key = self._build_cache_key(lat, lng)
            cached = await self.cache.get(cache_key)
            if cached is not None:
                if self.config.log_cache_hits:
                    logger.debug(f"Cache hit for weather at ({lat}, {lng})")
                return cached
        
        # Fetch from API
        weather_data = await self._fetch_weather_with_retry(lat, lng)
        
        # Store in cache
        if self.cache is not None:
            cache_key = self._build_cache_key(lat, lng)
            await self.cache.set(cache_key, weather_data)
        
        return weather_data
    
    async def _fetch_weather_with_retry(
        self,
        lat: float,
        lng: float,
    ) -> WeatherData:
        """
        Fetch weather data with retry logic.
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            WeatherData from API
            
        Raises:
            WeatherAPIError: After all retries exhausted
        """
        last_error: Optional[Exception] = None
        
        for attempt in range(self.config.api.retry_count):
            try:
                return await self._fetch_weather(lat, lng)
            except WeatherAPIRateLimitError:
                # Don't retry rate limit errors
                raise
            except WeatherAPIInvalidKeyError:
                # Don't retry invalid key errors
                raise
            except WeatherAPIError as e:
                last_error = e
                if attempt < self.config.api.retry_count - 1:
                    delay = self.config.api.retry_delay_seconds * (2 ** attempt)
                    logger.warning(
                        f"Weather API request failed (attempt {attempt + 1}/"
                        f"{self.config.api.retry_count}), retrying in {delay}s: {e}"
                    )
                    await asyncio.sleep(delay)
        
        raise WeatherAPIConnectionError(
            f"Failed to fetch weather after {self.config.api.retry_count} attempts: {last_error}"
        )
    
    async def _fetch_weather(self, lat: float, lng: float) -> WeatherData:
        """
        Make the actual API request to OpenWeatherMap.
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            Parsed WeatherData
            
        Raises:
            WeatherAPIError: On API errors
        """
        if not self.config.api.api_key:
            raise WeatherAPIInvalidKeyError(
                "OpenWeatherMap API key not configured. "
                "Set OPENWEATHER_API_KEY environment variable."
            )
        
        url = f"{self.config.api.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lng,
            "appid": self.config.api.api_key,
            "units": "metric",
        }
        
        if self.config.log_api_calls:
            logger.info(f"Fetching weather for ({lat}, {lng})")
        
        try:
            client = await self._get_client()
            response = await client.get(url, params=params)
        except httpx.TimeoutException as e:
            raise WeatherAPIConnectionError(f"Weather API request timed out: {e}")
        except httpx.RequestError as e:
            raise WeatherAPIConnectionError(f"Weather API connection error: {e}")
        
        if response.status_code == 401:
            raise WeatherAPIInvalidKeyError("Invalid OpenWeatherMap API key")
        if response.status_code == 429:
            raise WeatherAPIRateLimitError("OpenWeatherMap API rate limit exceeded")
        if response.status_code != 200:
            raise WeatherAPIError(
                f"Weather API returned status {response.status_code}: {response.text}"
            )
        
        return self._parse_response(response.json(), lat, lng)
    
    def _parse_response(
        self,
        data: Dict[str, Any],
        lat: float,
        lng: float,
    ) -> WeatherData:
        """
        Parse OpenWeatherMap API response into WeatherData.
        
        Args:
            data: Raw API response JSON
            lat: Original request latitude
            lng: Original request longitude
            
        Returns:
            Parsed WeatherData object
        """
        # Extract main weather condition
        weather_list = data.get("weather", [])
        if weather_list:
            main_condition = weather_list[0].get("main", "Clear")
        else:
            main_condition = "Clear"
        
        condition = self.CONDITION_MAPPING.get(
            main_condition,
            WeatherCondition.CLEAR
        )
        
        # Extract main data
        main_data = data.get("main", {})
        temperature = main_data.get("temp", 20.0)
        humidity = main_data.get("humidity", 50.0)
        
        # Extract wind data
        wind_data = data.get("wind", {})
        wind_speed = wind_data.get("speed", 0.0)
        wind_gust = wind_data.get("gust")
        
        # Extract visibility (default 10km if not provided)
        visibility = data.get("visibility", 10000)
        
        # Extract precipitation (rain and snow)
        rain_data = data.get("rain", {})
        rain_1h = rain_data.get("1h", 0.0)
        
        snow_data = data.get("snow", {})
        snow_1h = snow_data.get("1h", 0.0)
        
        # Extract clouds
        clouds_data = data.get("clouds", {})
        clouds_percent = clouds_data.get("all", 0)
        
        return WeatherData(
            condition=condition,
            temperature_celsius=temperature,
            humidity_percent=humidity,
            wind_speed_ms=wind_speed,
            wind_gust_ms=wind_gust,
            visibility_meters=visibility,
            precipitation_mm=rain_1h,
            snow_mm=snow_1h,
            clouds_percent=clouds_percent,
            timestamp=datetime.now(timezone.utc),
            location_lat=lat,
            location_lng=lng,
        )
    
    async def get_weather_along_route(
        self,
        coordinates: list[tuple[float, float]],
        sample_interval: int = 10,
    ) -> list[WeatherData]:
        """
        Get weather data at multiple points along a route.
        
        Args:
            coordinates: List of (lat, lng) tuples
            sample_interval: Sample every Nth coordinate
            
        Returns:
            List of WeatherData for sampled points
        """
        # Sample coordinates at interval
        sampled = coordinates[::sample_interval]
        
        # Ensure we include start and end
        if coordinates and coordinates[-1] not in sampled:
            sampled.append(coordinates[-1])
        
        # Fetch weather for all points concurrently
        tasks = [
            self.get_weather(lat, lng)
            for lat, lng in sampled
        ]
        
        return await asyncio.gather(*tasks)
    
    async def get_worst_weather_along_route(
        self,
        coordinates: list[tuple[float, float]],
        sample_interval: int = 10,
    ) -> WeatherData:
        """
        Get the worst weather conditions along a route.
        
        This is useful for determining the most restrictive safety
        modifiers to apply to the entire route.
        
        Args:
            coordinates: List of (lat, lng) tuples
            sample_interval: Sample every Nth coordinate
            
        Returns:
            WeatherData representing worst conditions
        """
        weather_list = await self.get_weather_along_route(
            coordinates,
            sample_interval
        )
        
        if not weather_list:
            # Return default clear weather if no data
            return WeatherData(
                condition=WeatherCondition.CLEAR,
                temperature_celsius=20.0,
                humidity_percent=50.0,
                wind_speed_ms=0.0,
                wind_gust_ms=None,
                visibility_meters=10000,
                precipitation_mm=0.0,
                snow_mm=0.0,
                clouds_percent=0,
                timestamp=datetime.now(timezone.utc),
                location_lat=coordinates[0][0] if coordinates else 0.0,
                location_lng=coordinates[0][1] if coordinates else 0.0,
            )
        
        # Find worst conditions
        # Priority: Snow > Rain > Visibility > Wind
        worst = weather_list[0]
        
        for weather in weather_list[1:]:
            # Check snow (worst)
            if weather.snow_mm > worst.snow_mm:
                worst = weather
                continue
            
            # Check rain
            if weather.precipitation_mm > worst.precipitation_mm:
                worst = weather
                continue
            
            # Check visibility (lower is worse)
            if weather.visibility_meters < worst.visibility_meters:
                worst = weather
                continue
            
            # Check wind
            if weather.wind_speed_ms > worst.wind_speed_ms:
                worst = weather
        
        return worst
`

**Acceptance Criteria:**
- [ ] API client connects successfully
- [ ] Retry logic works correctly
- [ ] Error handling covers all cases
- [ ] Response parsing is accurate
- [ ] Concurrent requests work for route weather
- [ ] Unit tests achieve 90%+ coverage

---

### TASK 1.4.4: Implement Weather Cache
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 1.5 hours
- [ ] **Dependencies:** TASK 1.4.1, TASK 1.4.2

**Description:**
Create Redis-based caching layer for weather data with TTL management.

**Implementation:**

`python
# File: motomap/weather/cache.py

"""
Redis-based caching for weather data.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .models import WeatherCondition, WeatherData
from .config import CacheConfig

logger = logging.getLogger(__name__)

class WeatherCache:
    """
    Redis-based cache for weather data.
    
    Provides fast access to recently fetched weather data to reduce
    API calls and improve response times.
    
    Falls back to in-memory caching if Redis is unavailable.
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """
        Initialize the weather cache.
        
        Args:
            config: Cache configuration. Uses defaults if not provided.
        """
        self.config = config or CacheConfig()
        self._redis: Optional["redis.Redis"] = None
        self._memory_cache: dict[str, tuple[WeatherData, float]] = {}
        self._use_redis = REDIS_AVAILABLE
        
    async def _get_redis(self) -> Optional["redis.Redis"]:
        """Get or create Redis connection."""
        if not self._use_redis:
            return None
            
        if self._redis is None:
            try:
                self._redis = redis.from_url(
                    self.config.redis_url,
                    decode_responses=True,
                )
                # Test connection
                await self._redis.ping()
                logger.info("Connected to Redis for weather caching")
            except Exception as e:
                logger.warning(
                    f"Redis unavailable, falling back to memory cache: {e}"
                )
                self._use_redis = False
                self._redis = None
                
        return self._redis
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None
    
    def _serialize(self, data: WeatherData) -> str:
        """Serialize WeatherData to JSON string."""
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
        """Deserialize JSON string to WeatherData."""
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
        """
        Get weather data from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached WeatherData or None if not found/expired
        """
        full_key = f"{self.config.key_prefix}{key}"
        
        # Try Redis first
        redis_client = await self._get_redis()
        if redis_client is not None:
            try:
                data_str = await redis_client.get(full_key)
                if data_str:
                    return self._deserialize(data_str)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        
        # Fallback to memory cache
        if full_key in self._memory_cache:
            data, expires_at = self._memory_cache[full_key]
            if datetime.now(timezone.utc).timestamp() < expires_at:
                return data
            else:
                # Expired, remove from cache
                del self._memory_cache[full_key]
        
        return None
    
    async def set(
        self,
        key: str,
        data: WeatherData,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """
        Store weather data in cache.
        
        Args:
            key: Cache key
            data: WeatherData to cache
            ttl_seconds: Time-to-live in seconds. Uses default if not provided.
        """
        full_key = f"{self.config.key_prefix}{key}"
        ttl = ttl_seconds or self.config.default_ttl_seconds
        
        # Ensure TTL doesn't exceed maximum
        ttl = min(ttl, self.config.max_ttl_seconds)
        
        # Try Redis first
        redis_client = await self._get_redis()
        if redis_client is not None:
            try:
                data_str = self._serialize(data)
                await redis_client.setex(full_key, ttl, data_str)
                return
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")
        
        # Fallback to memory cache
        expires_at = datetime.now(timezone.utc).timestamp() + ttl
        self._memory_cache[full_key] = (data, expires_at)
        
        # Clean up old entries (simple approach)
        self._cleanup_memory_cache()
    
    def _cleanup_memory_cache(self, max_entries: int = 1000) -> None:
        """Remove expired entries and limit cache size."""
        now = datetime.now(timezone.utc).timestamp()
        
        # Remove expired
        expired_keys = [
            k for k, (_, expires_at) in self._memory_cache.items()
            if expires_at < now
        ]
        for k in expired_keys:
            del self._memory_cache[k]
        
        # Limit size (remove oldest)
        if len(self._memory_cache) > max_entries:
            sorted_items = sorted(
                self._memory_cache.items(),
                key=lambda x: x[1][1]  # Sort by expires_at
            )
            for k, _ in sorted_items[:len(self._memory_cache) - max_entries]:
                del self._memory_cache[k]
    
    async def delete(self, key: str) -> None:
        """
        Delete weather data from cache.
        
        Args:
            key: Cache key
        """
        full_key = f"{self.config.key_prefix}{key}"
        
        # Delete from Redis
        redis_client = await self._get_redis()
        if redis_client is not None:
            try:
                await redis_client.delete(full_key)
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")
        
        # Delete from memory cache
        if full_key in self._memory_cache:
            del self._memory_cache[full_key]
    
    async def clear(self) -> None:
        """Clear all weather cache entries."""
        # Clear memory cache
        self._memory_cache.clear()
        
        # Clear Redis cache (by pattern)
        redis_client = await self._get_redis()
        if redis_client is not None:
            try:
                pattern = f"{self.config.key_prefix}*"
                cursor = 0
                while True:
                    cursor, keys = await redis_client.scan(
                        cursor,
                        match=pattern,
                        count=100
                    )
                    if keys:
                        await redis_client.delete(*keys)
                    if cursor == 0:
                        break
            except Exception as e:
                logger.warning(f"Redis clear failed: {e}")
`

**Acceptance Criteria:**
- [ ] Redis caching works when available
- [ ] Memory cache fallback works when Redis is unavailable
- [ ] TTL expiration works correctly
- [ ] Serialization/deserialization preserves all data
- [ ] Cache cleanup prevents memory leaks
- [ ] Unit tests cover all scenarios

---

### TASK 1.4.5: Implement Road Condition Assessor
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2.5 hours
- [ ] **Dependencies:** TASK 1.4.1, TASK 1.4.2, TASK 1.4.3

**Description:**
Create the road condition assessment engine that translates weather data
into safety scores and lane splitting modifiers.

**Implementation:**

```python
# File: motomap/weather/assessment.py

"""
Road condition assessment based on weather data.

This module provides the core logic for determining how weather
conditions affect motorcycle safety and lane splitting recommendations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Tuple

from .models import (
    WeatherCondition,
    WeatherData,
    RoadSurfaceCondition,
    RoadConditionAssessment,
)
from .config import WeatherConfig, RoadConditionThresholds, LaneSplittingModifiers

logger = logging.getLogger(__name__)

class RoadConditionAssessor:
    """
    Assesses road conditions based on weather data.
    
    This class is the core intelligence for weather-aware routing.
    It analyzes multiple weather factors and produces safety scores
    and lane splitting modifiers.
    
    Usage:
        assessor = RoadConditionAssessor()
        weather = WeatherData(...)  # From weather service
        assessment = assessor.assess(weather)
        
        if assessment.lane_splitting_modifier < 0.5:
            print("Lane splitting not recommended")
        
        for warning in assessment.warnings:
            print(f"⚠️ {warning}")
    """
    
    def __init__(self, config: WeatherConfig | None = None):
        """
        Initialize the assessor.
        
        Args:
            config: Weather configuration with thresholds and modifiers
        """
        self.config = config or WeatherConfig()
        self.thresholds = self.config.thresholds
        self.modifiers = self.config.modifiers
    
    def assess(self, weather: WeatherData) -> RoadConditionAssessment:
        """
        Assess road conditions based on weather data.
        
        Args:
            weather: Current weather data
            
        Returns:
            Complete road condition assessment
        """
        warnings: List[str] = []
        
        # Determine surface condition
        surface_condition = self._assess_surface_condition(weather)
        
        # Calculate individual factors
        grip_factor = self._calculate_grip_factor(weather, surface_condition)
        visibility_factor = self._calculate_visibility_factor(weather)
        wind_factor = self._calculate_wind_factor(weather)
        temperature_factor = self._calculate_temperature_factor(weather)
        
        # Collect warnings
        warnings.extend(self._get_surface_warnings(surface_condition, weather))
        warnings.extend(self._get_visibility_warnings(weather))
        warnings.extend(self._get_wind_warnings(weather))
        warnings.extend(self._get_temperature_warnings(weather))
        
        # Calculate overall safety score (0.0 to 1.0)
        # Weighted average with grip being most important
        overall_safety = (
            grip_factor * 0.40 +
            visibility_factor * 0.25 +
            wind_factor * 0.20 +
            temperature_factor * 0.15
        )
        
        # Calculate lane splitting modifier
        # This is the minimum of all factors - any single bad factor
        # can significantly reduce lane splitting recommendations
        lane_split_modifier = self._calculate_lane_split_modifier(
            surface_condition,
            weather,
            grip_factor,
            visibility_factor,
            wind_factor,
            temperature_factor,
        )
        
        return RoadConditionAssessment(
            surface_condition=surface_condition,
            grip_factor=grip_factor,
            visibility_factor=visibility_factor,
            wind_risk_factor=wind_factor,
            overall_safety_score=overall_safety,
            lane_splitting_modifier=lane_split_modifier,
            warnings=warnings,
        )
    
    def _assess_surface_condition(
        self,
        weather: WeatherData
    ) -> RoadSurfaceCondition:
        """
        Determine road surface condition from weather.
        
        Args:
            weather: Current weather data
            
        Returns:
            Assessed road surface condition
        """
        # Check for snow/ice first (most dangerous)
        if weather.snow_mm > 0:
            if weather.temperature_celsius < self.thresholds.freezing_point:
                return RoadSurfaceCondition.ICY
            return RoadSurfaceCondition.SNOWY
        
        # Check for freezing temperatures (ice risk)
        if weather.temperature_celsius < self.thresholds.freezing_point:
            # Even without precipitation, roads can be icy
            if weather.humidity_percent > self.thresholds.high_humidity:
                return RoadSurfaceCondition.ICY
        
        # Check for rain/precipitation
        if weather.precipitation_mm > 0:
            if weather.precipitation_mm > self.thresholds.heavy_rain_threshold:
                return RoadSurfaceCondition.FLOODED
            return RoadSurfaceCondition.WET
        
        # Check for recent rain (high humidity + clouds)
        if (weather.humidity_percent > self.thresholds.high_humidity and
            weather.condition in [WeatherCondition.CLOUDS, WeatherCondition.MIST]):
            return RoadSurfaceCondition.WET
        
        # Check for drizzle/mist conditions
        if weather.condition in [
            WeatherCondition.DRIZZLE,
            WeatherCondition.MIST,
            WeatherCondition.FOG
        ]:
            return RoadSurfaceCondition.WET
        
        return RoadSurfaceCondition.DRY
    
    def _calculate_grip_factor(
        self,
        weather: WeatherData,
        surface: RoadSurfaceCondition,
    ) -> float:
        """
        Calculate tire grip factor (0.0 to 1.0).
        
        1.0 = Maximum grip (dry conditions)
        0.0 = No grip (icy/flooded)
        """
        grip_map = {
            RoadSurfaceCondition.DRY: 1.0,
            RoadSurfaceCondition.WET: 0.7,
            RoadSurfaceCondition.SNOWY: 0.3,
            RoadSurfaceCondition.ICY: 0.1,
            RoadSurfaceCondition.FLOODED: 0.2,
        }
        
        base_grip = grip_map.get(surface, 1.0)
        
        # Additional reduction for heavy rain
        if weather.precipitation_mm > self.thresholds.heavy_rain_threshold:
            base_grip *= 0.7
        elif weather.precipitation_mm > self.thresholds.moderate_rain_threshold:
            base_grip *= 0.85
        
        # Reduction for painted road markings when wet
        # (they become very slippery)
        if surface == RoadSurfaceCondition.WET:
            base_grip *= 0.9  # General reduction for painted lines
        
        return max(0.0, min(1.0, base_grip))
    
    def _calculate_visibility_factor(self, weather: WeatherData) -> float:
        """
        Calculate visibility factor (0.0 to 1.0).
        
        1.0 = Excellent visibility (>10km)
        0.0 = Dangerous visibility (<500m)
        """
        v = weather.visibility_meters
        t = self.thresholds
        
        if v >= t.excellent_visibility:
            return 1.0
        elif v >= t.good_visibility:
            return 0.9
        elif v >= t.moderate_visibility:
            return 0.7
        elif v >= t.poor_visibility:
            return 0.4
        elif v >= t.dangerous_visibility:
            return 0.2
        else:
            return 0.0
    
    def _calculate_wind_factor(self, weather: WeatherData) -> float:
        """
        Calculate wind risk factor (0.0 to 1.0).
        
        1.0 = Calm conditions
        0.0 = Dangerous wind speeds
        
        Note: Uses gust speed if available as it's more relevant
        for motorcycle stability.
        """
        wind = weather.wind_gust_ms or weather.wind_speed_ms
        t = self.thresholds
        
        if wind <= t.light_wind:
            return 1.0
        elif wind <= t.moderate_wind:
            return 0.85
        elif wind <= t.strong_wind:
            return 0.6
        elif wind <= t.dangerous_wind:
            return 0.3
        else:
            return 0.0
    
    def _calculate_temperature_factor(self, weather: WeatherData) -> float:
        """
        Calculate temperature factor (0.0 to 1.0).
        
        1.0 = Optimal riding temperature (15-30°C)
        Lower = Too cold (grip/ice risk) or too hot (fatigue risk)
        """
        temp = weather.temperature_celsius
        t = self.thresholds
        
        if temp < t.freezing_point:
            return 0.2  # Ice risk
        elif temp < t.cold_threshold:
            return 0.6  # Cold, grip slightly reduced
        elif temp < t.optimal_low:
            return 0.85  # Cool but manageable
        elif temp <= t.optimal_high:
            return 1.0  # Optimal
        elif temp <= t.hot_threshold:
            return 0.9  # Warm, slight fatigue risk
        else:
            return 0.7  # Very hot, significant fatigue risk
    
    def _calculate_lane_split_modifier(
        self,
        surface: RoadSurfaceCondition,
        weather: WeatherData,
        grip: float,
        visibility: float,
        wind: float,
        temperature: float,
    ) -> float:
        """
        Calculate lane splitting modifier (0.0 to 1.0).
        
        This is the multiplier applied to lane splitting distance.
        0.0 = Completely disable lane splitting recommendations
        1.0 = Full lane splitting (ideal conditions)
        
        Uses a conservative approach - any single poor factor
        can significantly reduce the modifier.
        """
        m = self.modifiers
        
        # Start with surface condition modifier
        surface_mod = {
            RoadSurfaceCondition.DRY: m.dry_roads,
            RoadSurfaceCondition.WET: m.wet_roads_moderate,
            RoadSurfaceCondition.SNOWY: m.light_snow,
            RoadSurfaceCondition.ICY: m.icy_conditions,
            RoadSurfaceCondition.FLOODED: m.wet_roads_heavy,
        }.get(surface, 1.0)
        
        # Refine wet road modifier based on intensity
        if surface == RoadSurfaceCondition.WET:
            if weather.precipitation_mm < self.thresholds.light_rain_threshold:
                surface_mod = m.wet_roads_light
            elif weather.precipitation_mm < self.thresholds.moderate_rain_threshold:
                surface_mod = m.wet_roads_moderate
            else:
                surface_mod = m.wet_roads_heavy
        
        # Visibility modifier
        if visibility >= 0.9:
            vis_mod = m.excellent_visibility
        elif visibility >= 0.7:
            vis_mod = m.good_visibility
        elif visibility >= 0.4:
            vis_mod = m.moderate_visibility
        elif visibility >= 0.2:
            vis_mod = m.poor_visibility
        else:
            vis_mod = m.dangerous_visibility
        
        # Wind modifier
        if wind >= 0.85:
            wind_mod = m.light_wind
        elif wind >= 0.6:
            wind_mod = m.moderate_wind
        elif wind >= 0.3:
            wind_mod = m.strong_wind
        else:
            wind_mod = m.dangerous_wind
        
        # Temperature modifier
        if temperature >= 0.85:
            temp_mod = m.optimal
        elif temperature >= 0.6:
            temp_mod = m.cold
        elif temperature >= 0.3:
            temp_mod = m.freezing
        else:
            temp_mod = 0.0
        
        # Final modifier is the minimum of all modifiers
        # (conservative approach - worst condition wins)
        final_modifier = min(surface_mod, vis_mod, wind_mod, temp_mod)
        
        # Apply grip factor as additional multiplier
        final_modifier *= grip
        
        return max(0.0, min(1.0, final_modifier))
    
    def _get_surface_warnings(
        self,
        surface: RoadSurfaceCondition,
        weather: WeatherData,
    ) -> List[str]:
        """Get warnings related to road surface conditions."""
        warnings = []
        
        if surface == RoadSurfaceCondition.ICY:
            warnings.append("⚠️ BUZLU YOL: Yollar buzlu olabilir, şerit paylaşımı önerilmez")
        elif surface == RoadSurfaceCondition.SNOWY:
            warnings.append("❄️ KARLI YOL: Kar yağışı var, dikkatli sürün")
        elif surface == RoadSurfaceCondition.FLOODED:
            warnings.append("🌊 SU BİRİKİNTİSİ: Yoğun yağış, su birikintilerine dikkat")
        elif surface == RoadSurfaceCondition.WET:
            if weather.precipitation_mm > self.thresholds.moderate_rain_threshold:
                warnings.append("🌧️ YOĞUN YAĞIŞ: Yollar ıslak, fren mesafesi artırın")
            else:
                warnings.append("💧 ISLAK YOL: Yollar ıslak, yol çizgilerine dikkat")
        
        return warnings
    
    def _get_visibility_warnings(self, weather: WeatherData) -> List[str]:
        """Get warnings related to visibility."""
        warnings = []
        v = weather.visibility_meters
        t = self.thresholds
        
        if v < t.dangerous_visibility:
            warnings.append("🌫️ ÇOK DÜŞÜK GÖRÜŞ: Görüş mesafesi tehlikeli seviyede")
        elif v < t.poor_visibility:
            warnings.append("🌫️ DÜŞÜK GÖRÜŞ: Görüş mesafesi sınırlı, sis farlarını açın")
        elif v < t.moderate_visibility:
            warnings.append("🌁 SİSLİ: Görüş azalmış, takip mesafesini artırın")
        
        return warnings
    
    def _get_wind_warnings(self, weather: WeatherData) -> List[str]:
        """Get warnings related to wind conditions."""
        warnings = []
        wind = weather.wind_gust_ms or weather.wind_speed_ms
        t = self.thresholds
        
        if wind >= t.dangerous_wind:
            warnings.append("🌪️ ÇOK SERT RÜZGAR: Motosiklet kullanımı tehlikeli")
        elif wind >= t.strong_wind:
            warnings.append("💨 SERT RÜZGAR: Yan rüzgara dikkat, köprülerde yavaşlayın")
        elif wind >= t.moderate_wind:
            warnings.append("🍃 RÜZGARLI: Açık alanlarda yan rüzgara dikkat")
        
        return warnings
    
    def _get_temperature_warnings(self, weather: WeatherData) -> List[str]:
        """Get warnings related to temperature."""
        warnings = []
        temp = weather.temperature_celsius
        t = self.thresholds
        
        if temp < t.freezing_point:
            warnings.append("🥶 DONDURUCU: Sıcaklık 0°C altında, buz riski yüksek")
        elif temp < t.cold_threshold:
            warnings.append("❄️ SOĞUK: Motor ısınması için bekleyin, eldivenlerinizi kontrol edin")
        elif temp > t.hot_threshold:
            warnings.append("🔥 ÇOK SICAK: Sıvı alımına dikkat, düzenli mola verin")
        
        return warnings
    
    def assess_route_segment(
        self,
        weather: WeatherData,
        segment_type: str,
        has_tunnel: bool = False,
    ) -> Tuple[float, List[str]]:
        """
        Assess a specific route segment with weather conditions.
        
        This is used for segment-by-segment coloring on the map.
        
        Args:
            weather: Weather data for segment location
            segment_type: OSM highway type
            has_tunnel: Whether segment is in a tunnel
            
        Returns:
            Tuple of (safety_score, warnings)
        """
        assessment = self.assess(weather)
        
        # Tunnel bonus - protected from weather
        if has_tunnel:
            # In tunnels, weather matters less but visibility is still important
            tunnel_score = max(
                assessment.overall_safety_score,
                0.8  # Minimum 80% in tunnels
            )
            return tunnel_score, ["🚇 Tünel: Hava koşullarından korunaklı"]
        
        # Exposed roads (bridges, overpasses) get penalty
        if segment_type in ["motorway", "trunk"] and assessment.wind_risk_factor < 0.7:
            return (
                assessment.overall_safety_score * 0.9,
                assessment.warnings + ["🌉 Açık yol: Rüzgara maruz kalabilirsiniz"]
            )
        
        return assessment.overall_safety_score, assessment.warnings
```

**Acceptance Criteria:**
- [ ] Assessment logic correctly evaluates all weather factors
- [ ] Lane splitting modifiers are conservative and safe
- [ ] Warnings are in Turkish and user-friendly
- [ ] Segment-by-segment assessment works for map coloring
- [ ] Edge cases handled (missing data, extreme values)
- [ ] Unit tests cover all weather condition combinations

---

### TASK 1.4.6: Integrate Weather with Algorithm
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** TASK 1.4.1 through TASK 1.4.5

**Description:**
Modify the main routing algorithm (motomap/algorithm.py) to incorporate
weather-based lane splitting adjustments.

**Files to Modify:**
- motomap/algorithm.py

**Implementation Details:**

```python
# Add to motomap/algorithm.py

# Import weather module
from motomap.weather import (
    WeatherService,
    RoadConditionAssessor,
    WeatherData,
    RoadConditionAssessment,
)

# Add new function to calculate weather-adjusted lane splitting
async def calculate_weather_adjusted_lane_split(
    edges: list,
    weather_service: WeatherService,
    assessor: RoadConditionAssessor,
) -> dict:
    """
    Calculate lane splitting distances with weather adjustments.
    
    Args:
        edges: List of route edges with coordinates
        weather_service: Weather service instance
        assessor: Road condition assessor instance
        
    Returns:
        Dictionary with adjusted metrics and warnings
    """
    # Get coordinates for weather lookup
    if not edges:
        return {
            "serit_paylasimi_m": 0,
            "serit_paylasimi_adjusted_m": 0,
            "weather_modifier": 1.0,
            "weather_warnings": [],
        }
    
    # Sample coordinates along route
    sample_coords = []
    for edge in edges[::10]:  # Every 10th edge
        if "geometry" in edge:
            coords = edge["geometry"].coords
            if coords:
                mid_idx = len(coords) // 2
                sample_coords.append(coords[mid_idx])
    
    if not sample_coords:
        # Fallback to edge endpoints
        for edge in edges[:5]:
            sample_coords.append((edge.get("lat", 0), edge.get("lng", 0)))
    
    # Get worst weather along route
    try:
        worst_weather = await weather_service.get_worst_weather_along_route(
            [(c[1], c[0]) for c in sample_coords]  # Convert to (lat, lng)
        )
        assessment = assessor.assess(worst_weather)
    except Exception as e:
        # If weather unavailable, use full lane splitting
        return {
            "serit_paylasimi_m": _calculate_base_lane_split(edges),
            "serit_paylasimi_adjusted_m": _calculate_base_lane_split(edges),
            "weather_modifier": 1.0,
            "weather_warnings": [f"Hava durumu alınamadı: {str(e)}"],
        }
    
    # Calculate base lane splitting distance
    base_lane_split = _calculate_base_lane_split(edges)
    
    # Apply weather modifier
    adjusted_lane_split = int(base_lane_split * assessment.lane_splitting_modifier)
    
    return {
        "serit_paylasimi_m": base_lane_split,
        "serit_paylasimi_adjusted_m": adjusted_lane_split,
        "weather_modifier": assessment.lane_splitting_modifier,
        "weather_warnings": assessment.warnings,
        "road_surface": assessment.surface_condition.value,
        "overall_safety": assessment.overall_safety_score,
    }


def _calculate_base_lane_split(edges: list) -> int:
    """
    Calculate base lane splitting distance without weather adjustments.
    
    This is the existing lane splitting logic from algorithm.py.
    """
    total_suitable_m = 0
    
    for edge in edges:
        highway_type = edge.get("highway", "")
        lanes = edge.get("lanes", 1)
        tunnel = edge.get("tunnel", "no")
        maxspeed = edge.get("maxspeed", 50)
        length_m = edge.get("length", 0)
        
        # Skip tunnels
        if tunnel == "yes":
            continue
        
        # Check lane count
        if lanes < 2:
            continue
        
        # Check highway type and speed limits
        if highway_type in ["motorway", "trunk", "primary"]:
            # Major roads - always suitable with 2+ lanes
            total_suitable_m += length_m
        elif highway_type in ["secondary", "tertiary"]:
            # Urban roads - only if speed <= 70
            if maxspeed <= 70:
                total_suitable_m += length_m
    
    return int(total_suitable_m)
```

**Acceptance Criteria:**
- [ ] Weather integration is non-blocking (uses async)
- [ ] Fallback works when weather unavailable
- [ ] Adjusted distances are returned alongside base distances
- [ ] Weather warnings propagate to API response
- [ ] Performance impact is minimal (<500ms added latency)
- [ ] Unit and integration tests pass

---

### TASK 1.4.7: Add Weather API Endpoint
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 1.5 hours
- [ ] **Dependencies:** TASK 1.4.1 through TASK 1.4.5

**Description:**
Create FastAPI endpoint for fetching current weather and road conditions.

**Files to Create/Modify:**
- api/routes/weather.py
- api/main.py

**Implementation:**

```python
# File: api/routes/weather.py

"""
Weather API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from motomap.weather import (
    WeatherService,
    RoadConditionAssessor,
    WeatherConfig,
)

router = APIRouter(prefix="/api/weather", tags=["weather"])

# Initialize services
config = WeatherConfig.from_env()
weather_service = WeatherService(config)
assessor = RoadConditionAssessor(config)


class WeatherResponse(BaseModel):
    """Weather API response model."""
    
    condition: str = Field(..., description="Weather condition (clear, rain, etc.)")
    temperature_celsius: float = Field(..., description="Temperature in Celsius")
    humidity_percent: float = Field(..., description="Humidity percentage")
    wind_speed_ms: float = Field(..., description="Wind speed in m/s")
    wind_gust_ms: Optional[float] = Field(None, description="Wind gust speed in m/s")
    visibility_meters: int = Field(..., description="Visibility in meters")
    precipitation_mm: float = Field(..., description="Precipitation in mm/hour")
    
    class Config:
        json_schema_extra = {
            "example": {
                "condition": "clear",
                "temperature_celsius": 22.5,
                "humidity_percent": 55.0,
                "wind_speed_ms": 3.2,
                "wind_gust_ms": 5.1,
                "visibility_meters": 10000,
                "precipitation_mm": 0.0,
            }
        }


class RoadConditionResponse(BaseModel):
    """Road condition assessment response model."""
    
    surface_condition: str = Field(..., description="Road surface (dry, wet, icy, etc.)")
    overall_safety_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Overall safety score (0-1)"
    )
    lane_splitting_modifier: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Lane splitting modifier (0-1)"
    )
    grip_factor: float = Field(..., ge=0, le=1, description="Tire grip factor")
    visibility_factor: float = Field(..., ge=0, le=1, description="Visibility factor")
    wind_risk_factor: float = Field(..., ge=0, le=1, description="Wind risk factor")
    warnings: List[str] = Field(default_factory=list, description="Safety warnings")
    
    # Weather data
    weather: WeatherResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "surface_condition": "wet",
                "overall_safety_score": 0.72,
                "lane_splitting_modifier": 0.6,
                "grip_factor": 0.7,
                "visibility_factor": 0.9,
                "wind_risk_factor": 0.85,
                "warnings": ["💧 ISLAK YOL: Yollar ıslak, yol çizgilerine dikkat"],
                "weather": {
                    "condition": "rain",
                    "temperature_celsius": 18.5,
                    "humidity_percent": 85.0,
                    "wind_speed_ms": 4.5,
                    "visibility_meters": 6000,
                    "precipitation_mm": 2.1,
                }
            }
        }


@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
):
    """
    Get current weather for a location.
    
    Returns the current weather conditions at the specified coordinates.
    Data is cached for 5 minutes to reduce API calls.
    """
    try:
        weather = await weather_service.get_weather(lat, lng)
        return WeatherResponse(
            condition=weather.condition.value,
            temperature_celsius=weather.temperature_celsius,
            humidity_percent=weather.humidity_percent,
            wind_speed_ms=weather.wind_speed_ms,
            wind_gust_ms=weather.wind_gust_ms,
            visibility_meters=weather.visibility_meters,
            precipitation_mm=weather.precipitation_mm,
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Weather service error: {str(e)}")


@router.get("/road-conditions", response_model=RoadConditionResponse)
async def get_road_conditions(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
):
    """
    Get road conditions assessment for a location.
    
    Returns weather-based road condition assessment including
    safety scores, lane splitting recommendations, and warnings.
    """
    try:
        weather = await weather_service.get_weather(lat, lng)
        assessment = assessor.assess(weather)
        
        return RoadConditionResponse(
            surface_condition=assessment.surface_condition.value,
            overall_safety_score=assessment.overall_safety_score,
            lane_splitting_modifier=assessment.lane_splitting_modifier,
            grip_factor=assessment.grip_factor,
            visibility_factor=assessment.visibility_factor,
            wind_risk_factor=assessment.wind_risk_factor,
            warnings=assessment.warnings,
            weather=WeatherResponse(
                condition=weather.condition.value,
                temperature_celsius=weather.temperature_celsius,
                humidity_percent=weather.humidity_percent,
                wind_speed_ms=weather.wind_speed_ms,
                wind_gust_ms=weather.wind_gust_ms,
                visibility_meters=weather.visibility_meters,
                precipitation_mm=weather.precipitation_mm,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Weather service error: {str(e)}")


@router.get("/route-assessment")
async def get_route_weather_assessment(
    origin_lat: float = Query(..., ge=-90, le=90),
    origin_lng: float = Query(..., ge=-180, le=180),
    dest_lat: float = Query(..., ge=-90, le=90),
    dest_lng: float = Query(..., ge=-180, le=180),
):
    """
    Get weather assessment for a route.
    
    Samples weather at multiple points along the route and returns
    the worst conditions encountered.
    """
    try:
        # Create simple route line for sampling
        coords = [
            (origin_lat, origin_lng),
            ((origin_lat + dest_lat) / 2, (origin_lng + dest_lng) / 2),
            (dest_lat, dest_lng),
        ]
        
        worst_weather = await weather_service.get_worst_weather_along_route(coords)
        assessment = assessor.assess(worst_weather)
        
        return {
            "route_safety_score": assessment.overall_safety_score,
            "lane_splitting_modifier": assessment.lane_splitting_modifier,
            "worst_conditions": {
                "location": {
                    "lat": worst_weather.location_lat,
                    "lng": worst_weather.location_lng,
                },
                "condition": worst_weather.condition.value,
                "surface": assessment.surface_condition.value,
            },
            "warnings": assessment.warnings,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Weather service error: {str(e)}")
```

**Acceptance Criteria:**
- [ ] All endpoints return correct response format
- [ ] Error handling returns appropriate HTTP status codes
- [ ] API documentation (OpenAPI/Swagger) is generated correctly
- [ ] Rate limiting works for weather endpoints
- [ ] Integration tests pass

---

## 1.5 Testing Requirements

### TASK 1.5.1: Unit Tests for Weather Module
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** TASK 1.4.1 through TASK 1.4.5

**Files to Create:**
- tests/weather/test_models.py
- tests/weather/test_client.py
- tests/weather/test_cache.py
- tests/weather/test_assessment.py
- tests/weather/test_integration.py

**Test Coverage Requirements:**
- [ ] 90%+ line coverage for all weather module files
- [ ] All weather conditions tested
- [ ] All edge cases covered
- [ ] Mock API responses for consistent testing
- [ ] Redis mock for cache testing

---

## 1.6 Mobile App Integration

### TASK 1.6.1: Add Weather Types to TypeScript
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 1 hour
- [ ] **Dependencies:** TASK 1.4.7

**Files to Modify:**
- app/mobile/types/index.ts

**Implementation:**

```typescript
// Add to app/mobile/types/index.ts

// Weather Types
export type WeatherCondition = 
  | "clear"
  | "clouds"
  | "rain"
  | "drizzle"
  | "thunderstorm"
  | "snow"
  | "mist"
  | "fog"
  | "haze"
  | "dust"
  | "sand"
  | "tornado";

export type RoadSurfaceCondition = 
  | "dry"
  | "wet"
  | "icy"
  | "snowy"
  | "flooded";

export type WeatherData = {
  condition: WeatherCondition;
  temperature_celsius: number;
  humidity_percent: number;
  wind_speed_ms: number;
  wind_gust_ms: number | null;
  visibility_meters: number;
  precipitation_mm: number;
};

export type RoadConditionAssessment = {
  surface_condition: RoadSurfaceCondition;
  overall_safety_score: number;
  lane_splitting_modifier: number;
  grip_factor: number;
  visibility_factor: number;
  wind_risk_factor: number;
  warnings: string[];
  weather: WeatherData;
};

// Extended ModeStats with weather
export type ModeStatsWithWeather = ModeStats & {
  serit_paylasimi_adjusted: number;
  weather_modifier: number;
  weather_warnings: string[];
  road_surface: RoadSurfaceCondition;
  overall_safety: number;
};
```

---

### TASK 1.6.2: Create Weather Service Hook
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 1.5 hours
- [ ] **Dependencies:** TASK 1.6.1

**Files to Create:**
- app/mobile/hooks/useWeather.ts

**Implementation:**

```typescript
// File: app/mobile/hooks/useWeather.ts

import { useState, useEffect, useCallback } from "react";
import { API_URL } from "../utils/api";
import { RoadConditionAssessment, WeatherData } from "../types";

type UseWeatherOptions = {
  refreshInterval?: number; // ms, default 5 minutes
  enabled?: boolean;
};

type UseWeatherResult = {
  weather: WeatherData | null;
  roadConditions: RoadConditionAssessment | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  lastUpdated: Date | null;
};

export function useWeather(
  lat: number | null,
  lng: number | null,
  options: UseWeatherOptions = {}
): UseWeatherResult {
  const { refreshInterval = 300000, enabled = true } = options; // 5 min default
  
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [roadConditions, setRoadConditions] = useState<RoadConditionAssessment | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  
  const fetchWeather = useCallback(async () => {
    if (lat === null || lng === null || !enabled) {
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        $/api/weather/road-conditions?lat=___BEGIN___COMMAND_DONE_MARKER___$LASTEXITCODE{lat}&lng=___BEGIN___COMMAND_DONE_MARKER___$LASTEXITCODE{lng}
      );
      
      if (!response.ok) {
        throw new Error(HTTP ___BEGIN___COMMAND_DONE_MARKER___$LASTEXITCODE{response.status});
      }
      
      const data: RoadConditionAssessment = await response.json();
      setWeather(data.weather);
      setRoadConditions(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Hava durumu alınamadı");
    } finally {
      setIsLoading(false);
    }
  }, [lat, lng, enabled]);
  
  // Initial fetch
  useEffect(() => {
    fetchWeather();
  }, [fetchWeather]);
  
  // Refresh interval
  useEffect(() => {
    if (!enabled || refreshInterval <= 0) {
      return;
    }
    
    const interval = setInterval(fetchWeather, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchWeather, refreshInterval, enabled]);
  
  return {
    weather,
    roadConditions,
    isLoading,
    error,
    refresh: fetchWeather,
    lastUpdated,
  };
}

// Hook for route-specific weather
export function useRouteWeather(
  originLat: number | null,
  originLng: number | null,
  destLat: number | null,
  destLng: number | null,
  enabled: boolean = true
) {
  const [routeAssessment, setRouteAssessment] = useState<{
    route_safety_score: number;
    lane_splitting_modifier: number;
    warnings: string[];
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    if (
      originLat === null ||
      originLng === null ||
      destLat === null ||
      destLng === null ||
      !enabled
    ) {
      return;
    }
    
    const fetchRouteWeather = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const params = new URLSearchParams({
          origin_lat: originLat.toString(),
          origin_lng: originLng.toString(),
          dest_lat: destLat.toString(),
          dest_lng: destLng.toString(),
        });
        
        const response = await fetch(
          $/api/weather/route-assessment?___BEGIN___COMMAND_DONE_MARKER___$LASTEXITCODE{params}
        );
        
        if (!response.ok) {
          throw new Error(HTTP ___BEGIN___COMMAND_DONE_MARKER___$LASTEXITCODE{response.status});
        }
        
        const data = await response.json();
        setRouteAssessment(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Rota hava durumu alınamadı");
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchRouteWeather();
  }, [originLat, originLng, destLat, destLng, enabled]);
  
  return { routeAssessment, isLoading, error };
}
```

---

### TASK 1.6.3: Create Weather Display Component
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** TASK 1.6.1, TASK 1.6.2

**Files to Create:**
- app/mobile/components/WeatherCard.tsx
- app/mobile/components/WeatherWarnings.tsx

**Implementation:**

```tsx
// File: app/mobile/components/WeatherCard.tsx

import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { colors, typography, spacing, radius } from "../theme";
import { WeatherData, RoadConditionAssessment } from "../types";

type WeatherCardProps = {
  weather: WeatherData | null;
  roadConditions: RoadConditionAssessment | null;
  isLoading?: boolean;
  compact?: boolean;
};

const WEATHER_ICONS: Record<string, string> = {
  clear: "☀️",
  clouds: "☁️",
  rain: "🌧️",
  drizzle: "🌦️",
  thunderstorm: "⛈️",
  snow: "❄️",
  mist: "🌫️",
  fog: "🌫️",
  haze: "🌁",
};

const SURFACE_COLORS: Record<string, string[]> = {
  dry: [colors.success, colors.success + "80"],
  wet: [colors.warning, colors.warning + "80"],
  icy: ["#60A5FA", "#3B82F6"],
  snowy: ["#E5E7EB", "#9CA3AF"],
  flooded: [colors.danger, colors.danger + "80"],
};

export function WeatherCard({
  weather,
  roadConditions,
  isLoading = false,
  compact = false,
}: WeatherCardProps) {
  if (isLoading) {
    return (
      <View style={[styles.container, compact && styles.compact]}>
        <Text style={styles.loadingText}>Hava durumu yükleniyor...</Text>
      </View>
    );
  }
  
  if (!weather || !roadConditions) {
    return null;
  }
  
  const weatherIcon = WEATHER_ICONS[weather.condition] || "🌡️";
  const surfaceGradient = SURFACE_COLORS[roadConditions.surface_condition] || SURFACE_COLORS.dry;
  const safetyPercent = Math.round(roadConditions.overall_safety_score * 100);
  
  if (compact) {
    return (
      <View style={[styles.container, styles.compact]}>
        <Text style={styles.weatherIcon}>{weatherIcon}</Text>
        <Text style={styles.tempCompact}>
          {Math.round(weather.temperature_celsius)}°C
        </Text>
        <View style={[styles.safetyBadge, { backgroundColor: getSafetyColor(safetyPercent) }]}>
          <Text style={styles.safetyText}>{safetyPercent}%</Text>
        </View>
      </View>
    );
  }
  
  return (
    <LinearGradient
      colors={surfaceGradient}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.container}
    >
      <View style={styles.header}>
        <Text style={styles.weatherIcon}>{weatherIcon}</Text>
        <View>
          <Text style={styles.temp}>{Math.round(weather.temperature_celsius)}°C</Text>
          <Text style={styles.condition}>
            {translateCondition(weather.condition)}
          </Text>
        </View>
      </View>
      
      <View style={styles.stats}>
        <StatItem
          icon="💨"
          value={$ m/s}
          label="Rüzgar"
        />
        <StatItem
          icon="💧"
          value={$%}
          label="Nem"
        />
        <StatItem
          icon="👁️"
          value={formatVisibility(weather.visibility_meters)}
          label="Görüş"
        />
      </View>
      
      <View style={styles.safetySection}>
        <Text style={styles.safetyLabel}>Yol Güvenliği</Text>
        <View style={styles.safetyBar}>
          <View
            style={[
              styles.safetyFill,
              {
                width: $%,
                backgroundColor: getSafetyColor(safetyPercent),
              },
            ]}
          />
        </View>
        <Text style={styles.safetyValue}>{safetyPercent}%</Text>
      </View>
      
      <View style={styles.laneInfo}>
        <Text style={styles.laneLabel}>
          ✂️ Şerit Paylaşımı: {Math.round(roadConditions.lane_splitting_modifier * 100)}% uygun
        </Text>
      </View>
    </LinearGradient>
  );
}

function StatItem({ icon, value, label }: { icon: string; value: string; label: string }) {
  return (
    <View style={styles.statItem}>
      <Text style={styles.statIcon}>{icon}</Text>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function getSafetyColor(percent: number): string {
  if (percent >= 80) return colors.success;
  if (percent >= 60) return colors.warning;
  return colors.danger;
}

function translateCondition(condition: string): string {
  const translations: Record<string, string> = {
    clear: "Açık",
    clouds: "Bulutlu",
    rain: "Yağmurlu",
    drizzle: "Çiseleyen",
    thunderstorm: "Fırtınalı",
    snow: "Karlı",
    mist: "Sisli",
    fog: "Puslu",
    haze: "Dumanlı",
  };
  return translations[condition] || condition;
}

function formatVisibility(meters: number): string {
  if (meters >= 10000) return ">10 km";
  if (meters >= 1000) return $ km;
  return $ m;
}

const styles = StyleSheet.create({
  container: {
    borderRadius: radius.lg,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  compact: {
    flexDirection: "row",
    alignItems: "center",
    padding: spacing.sm,
    backgroundColor: colors.surfaceGlass,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  weatherIcon: {
    fontSize: 48,
    marginRight: spacing.md,
  },
  temp: {
    ...typography.heroMedium,
    color: colors.textPrimary,
  },
  tempCompact: {
    ...typography.bodyBold,
    color: colors.textPrimary,
    marginRight: spacing.sm,
  },
  condition: {
    ...typography.body,
    color: colors.textSecondary,
  },
  stats: {
    flexDirection: "row",
    justifyContent: "space-around",
    marginBottom: spacing.md,
  },
  statItem: {
    alignItems: "center",
  },
  statIcon: {
    fontSize: 20,
    marginBottom: spacing.xs,
  },
  statValue: {
    ...typography.bodyBold,
    color: colors.textPrimary,
  },
  statLabel: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  safetySection: {
    marginBottom: spacing.sm,
  },
  safetyLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  safetyBar: {
    height: 8,
    backgroundColor: "rgba(255,255,255,0.2)",
    borderRadius: radius.pill,
    overflow: "hidden",
  },
  safetyFill: {
    height: "100%",
    borderRadius: radius.pill,
  },
  safetyValue: {
    ...typography.bodyBold,
    color: colors.textPrimary,
    textAlign: "right",
    marginTop: spacing.xs,
  },
  safetyBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
  },
  safetyText: {
    ...typography.caption,
    color: colors.textPrimary,
  },
  laneInfo: {
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: "rgba(255,255,255,0.2)",
  },
  laneLabel: {
    ...typography.body,
    color: colors.textPrimary,
  },
  loadingText: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: "center",
    padding: spacing.md,
  },
});
```

---


---

# MODULE 2: VISUAL ROUTE SAFETY OVERLAY
# ======================================

## 2.1 Overview

The Visual Route Safety Overlay system provides color-coded route visualization
on the map, showing lane splitting suitability and safety levels for each
road segment. This creates an intuitive visual guide for riders.

## 2.2 Color Coding System

`
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ROUTE SAFETY COLOR SCHEME                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  🟢 GREEN (Safe/Optimal)                                                     │
│     - Lane splitting fully recommended                                       │
│     - Dry roads, good visibility, light wind                                │
│     - Safety score: 80-100%                                                  │
│     - Hex: #22C55E                                                          │
│                                                                              │
│  🟡 YELLOW (Caution)                                                         │
│     - Lane splitting possible with caution                                   │
│     - Slightly wet roads, moderate conditions                               │
│     - Safety score: 60-79%                                                   │
│     - Hex: #F59E0B                                                          │
│                                                                              │
│  🟠 ORANGE (Limited)                                                         │
│     - Lane splitting not recommended                                         │
│     - Wet roads, reduced visibility, wind                                   │
│     - Safety score: 40-59%                                                   │
│     - Hex: #F97316                                                          │
│                                                                              │
│  🔴 RED (Dangerous)                                                          │
│     - Lane splitting prohibited                                              │
│     - Icy/snowy roads, poor visibility, strong wind                         │
│     - Safety score: 0-39%                                                    │
│     - Hex: #EF4444                                                          │
│                                                                              │
│  🔵 BLUE (Neutral/Google Route)                                              │
│     - Google Maps comparison route                                           │
│     - Not analyzed for motorcycle safety                                    │
│     - Hex: #3B82F6 (dashed)                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
`

## 2.3 Implementation Tasks

### TASK 2.3.1: Create Route Segment Analyzer
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** Module 1 (Weather Integration)

**Description:**
Create a Python module that analyzes route segments and assigns safety
scores based on road characteristics and weather conditions.

**Files to Create:**
- motomap/routing/segment_analyzer.py

**Implementation:**

`python
# File: motomap/routing/segment_analyzer.py

"""
Route segment analyzer for safety scoring and visualization.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional
import math

from motomap.weather import WeatherData, RoadConditionAssessor

class SafetyLevel(Enum):
    """Safety level for route segments."""
    SAFE = "safe"           # Green - 80-100%
    CAUTION = "caution"     # Yellow - 60-79%
    LIMITED = "limited"     # Orange - 40-59%
    DANGEROUS = "dangerous" # Red - 0-39%

@dataclass
class SegmentAnalysis:
    """Analysis result for a single route segment."""
    
    segment_id: int
    start_coord: Tuple[float, float]  # (lat, lng)
    end_coord: Tuple[float, float]
    length_m: float
    
    # Road characteristics
    highway_type: str
    lanes: int
    maxspeed: int
    surface: str
    is_tunnel: bool
    is_bridge: bool
    
    # Safety analysis
    safety_score: float  # 0.0 to 1.0
    safety_level: SafetyLevel
    lane_split_suitable: bool
    lane_split_score: float  # 0.0 to 1.0
    
    # Weather impact (if available)
    weather_modifier: float
    weather_warnings: List[str]
    
    # Visualization
    color_hex: str
    stroke_width: int
    opacity: float

class RouteSegmentAnalyzer:
    """
    Analyzes route segments for safety and lane splitting suitability.
    
    This analyzer processes route data and produces segment-by-segment
    analysis that can be used for map visualization and user guidance.
    
    Usage:
        analyzer = RouteSegmentAnalyzer()
        segments = analyzer.analyze_route(route_edges, weather_data)
        
        for segment in segments:
            if segment.safety_level == SafetyLevel.DANGEROUS:
                print(f"⚠️ Dangerous segment: {segment.highway_type}")
    """
    
    # Safety color palette
    COLORS = {
        SafetyLevel.SAFE: "#22C55E",
        SafetyLevel.CAUTION: "#F59E0B",
        SafetyLevel.LIMITED: "#F97316",
        SafetyLevel.DANGEROUS: "#EF4444",
    }
    
    # Base safety scores by road type
    BASE_SAFETY_SCORES = {
        "motorway": 0.90,
        "motorway_link": 0.85,
        "trunk": 0.85,
        "trunk_link": 0.80,
        "primary": 0.80,
        "primary_link": 0.75,
        "secondary": 0.75,
        "secondary_link": 0.70,
        "tertiary": 0.70,
        "tertiary_link": 0.65,
        "residential": 0.65,
        "living_street": 0.55,
        "unclassified": 0.60,
        "service": 0.50,
    }
    
    # Lane splitting base scores
    LANE_SPLIT_SCORES = {
        "motorway": 0.95,
        "motorway_link": 0.85,
        "trunk": 0.90,
        "trunk_link": 0.80,
        "primary": 0.85,
        "primary_link": 0.75,
        "secondary": 0.70,
        "tertiary": 0.50,
        "residential": 0.30,
        "living_street": 0.10,
    }
    
    def __init__(
        self,
        weather_assessor: Optional[RoadConditionAssessor] = None,
    ):
        """
        Initialize the segment analyzer.
        
        Args:
            weather_assessor: Optional weather condition assessor
        """
        self.weather_assessor = weather_assessor or RoadConditionAssessor()
    
    def analyze_route(
        self,
        edges: List[dict],
        weather: Optional[WeatherData] = None,
    ) -> List[SegmentAnalysis]:
        """
        Analyze all segments in a route.
        
        Args:
            edges: List of route edge dictionaries from the routing engine
            weather: Optional weather data for the route area
            
        Returns:
            List of segment analyses
        """
        segments = []
        weather_assessment = None
        
        if weather is not None:
            weather_assessment = self.weather_assessor.assess(weather)
        
        for i, edge in enumerate(edges):
            segment = self._analyze_segment(
                segment_id=i,
                edge=edge,
                weather_assessment=weather_assessment,
            )
            segments.append(segment)
        
        return segments
    
    def _analyze_segment(
        self,
        segment_id: int,
        edge: dict,
        weather_assessment=None,
    ) -> SegmentAnalysis:
        """
        Analyze a single route segment.
        
        Args:
            segment_id: Unique identifier for this segment
            edge: Edge dictionary with road properties
            weather_assessment: Optional weather assessment
            
        Returns:
            Complete segment analysis
        """
        # Extract edge properties
        highway_type = edge.get("highway", "unclassified")
        lanes = edge.get("lanes", 2)
        maxspeed = edge.get("maxspeed", 50)
        surface = edge.get("surface", "asphalt")
        is_tunnel = edge.get("tunnel", "no") == "yes"
        is_bridge = edge.get("bridge", "no") == "yes"
        length_m = edge.get("length", 0)
        
        # Get coordinates
        geometry = edge.get("geometry")
        if geometry and hasattr(geometry, "coords"):
            coords = list(geometry.coords)
            start_coord = (coords[0][1], coords[0][0])  # (lat, lng)
            end_coord = (coords[-1][1], coords[-1][0])
        else:
            start_coord = (edge.get("start_lat", 0), edge.get("start_lng", 0))
            end_coord = (edge.get("end_lat", 0), edge.get("end_lng", 0))
        
        # Calculate base safety score
        base_safety = self.BASE_SAFETY_SCORES.get(highway_type, 0.50)
        
        # Adjust for road characteristics
        safety_score = self._adjust_safety_for_characteristics(
            base_safety,
            lanes=lanes,
            maxspeed=maxspeed,
            surface=surface,
            is_tunnel=is_tunnel,
            is_bridge=is_bridge,
        )
        
        # Calculate lane splitting score
        base_lane_split = self.LANE_SPLIT_SCORES.get(highway_type, 0.0)
        lane_split_score = self._calculate_lane_split_score(
            base_lane_split,
            lanes=lanes,
            maxspeed=maxspeed,
            is_tunnel=is_tunnel,
        )
        
        # Apply weather modifiers
        weather_modifier = 1.0
        weather_warnings = []
        
        if weather_assessment is not None:
            weather_modifier = weather_assessment.lane_splitting_modifier
            weather_warnings = weather_assessment.warnings
            
            # Apply weather to scores
            safety_score *= weather_assessment.overall_safety_score
            lane_split_score *= weather_modifier
        
        # Determine safety level
        safety_level = self._get_safety_level(safety_score)
        lane_split_suitable = lane_split_score >= 0.5 and lanes >= 2
        
        # Get visualization properties
        color_hex = self.COLORS[safety_level]
        stroke_width = self._get_stroke_width(highway_type)
        opacity = self._get_opacity(safety_level)
        
        return SegmentAnalysis(
            segment_id=segment_id,
            start_coord=start_coord,
            end_coord=end_coord,
            length_m=length_m,
            highway_type=highway_type,
            lanes=lanes,
            maxspeed=maxspeed,
            surface=surface,
            is_tunnel=is_tunnel,
            is_bridge=is_bridge,
            safety_score=safety_score,
            safety_level=safety_level,
            lane_split_suitable=lane_split_suitable,
            lane_split_score=lane_split_score,
            weather_modifier=weather_modifier,
            weather_warnings=weather_warnings,
            color_hex=color_hex,
            stroke_width=stroke_width,
            opacity=opacity,
        )
    
    def _adjust_safety_for_characteristics(
        self,
        base_score: float,
        lanes: int,
        maxspeed: int,
        surface: str,
        is_tunnel: bool,
        is_bridge: bool,
    ) -> float:
        """Adjust safety score based on road characteristics."""
        score = base_score
        
        # More lanes = generally safer for motorcycles
        if lanes >= 3:
            score *= 1.05
        elif lanes == 1:
            score *= 0.85
        
        # Speed adjustments
        if maxspeed > 100:
            score *= 0.95  # High speed roads slightly more dangerous
        elif maxspeed < 30:
            score *= 0.90  # Very slow roads often have more hazards
        
        # Surface adjustments
        poor_surfaces = ["gravel", "dirt", "sand", "mud", "unpaved"]
        if surface in poor_surfaces:
            score *= 0.70
        elif surface == "cobblestone":
            score *= 0.80
        
        # Tunnel penalty (limited escape routes)
        if is_tunnel:
            score *= 0.90
        
        # Bridge penalty (wind exposure, no shoulder)
        if is_bridge:
            score *= 0.95
        
        return max(0.0, min(1.0, score))
    
    def _calculate_lane_split_score(
        self,
        base_score: float,
        lanes: int,
        maxspeed: int,
        is_tunnel: bool,
    ) -> float:
        """Calculate lane splitting suitability score."""
        score = base_score
        
        # Must have at least 2 lanes
        if lanes < 2:
            return 0.0
        
        # More lanes = better for lane splitting
        if lanes >= 3:
            score *= 1.1
        if lanes >= 4:
            score *= 1.1
        
        # Speed limit affects suitability
        # Optimal: 30-70 km/h (stopped/slow traffic)
        if maxspeed <= 30:
            score *= 0.7  # Very slow, might have pedestrians
        elif maxspeed <= 50:
            score *= 1.0  # Optimal urban
        elif maxspeed <= 70:
            score *= 0.95
        elif maxspeed <= 100:
            score *= 0.80  # High speed, less safe
        else:
            score *= 0.60  # Very high speed
        
        # No lane splitting in tunnels
        if is_tunnel:
            return 0.0
        
        return max(0.0, min(1.0, score))
    
    def _get_safety_level(self, score: float) -> SafetyLevel:
        """Convert safety score to safety level."""
        if score >= 0.80:
            return SafetyLevel.SAFE
        elif score >= 0.60:
            return SafetyLevel.CAUTION
        elif score >= 0.40:
            return SafetyLevel.LIMITED
        else:
            return SafetyLevel.DANGEROUS
    
    def _get_stroke_width(self, highway_type: str) -> int:
        """Get stroke width for map visualization."""
        widths = {
            "motorway": 6,
            "trunk": 5,
            "primary": 5,
            "secondary": 4,
            "tertiary": 4,
            "residential": 3,
            "service": 2,
        }
        return widths.get(highway_type, 3)
    
    def _get_opacity(self, safety_level: SafetyLevel) -> float:
        """Get opacity for map visualization."""
        opacities = {
            SafetyLevel.SAFE: 0.9,
            SafetyLevel.CAUTION: 0.85,
            SafetyLevel.LIMITED: 0.8,
            SafetyLevel.DANGEROUS: 0.95,  # Make dangerous more visible
        }
        return opacities.get(safety_level, 0.8)
    
    def get_route_summary(
        self,
        segments: List[SegmentAnalysis],
    ) -> dict:
        """
        Generate a summary of route safety analysis.
        
        Args:
            segments: List of analyzed segments
            
        Returns:
            Summary dictionary with aggregate statistics
        """
        if not segments:
            return {
                "total_distance_m": 0,
                "average_safety_score": 0,
                "lane_split_distance_m": 0,
                "segment_counts": {},
                "warnings": [],
            }
        
        total_distance = sum(s.length_m for s in segments)
        weighted_safety = sum(s.safety_score * s.length_m for s in segments)
        lane_split_distance = sum(
            s.length_m for s in segments if s.lane_split_suitable
        )
        
        # Count segments by safety level
        segment_counts = {
            "safe": sum(1 for s in segments if s.safety_level == SafetyLevel.SAFE),
            "caution": sum(1 for s in segments if s.safety_level == SafetyLevel.CAUTION),
            "limited": sum(1 for s in segments if s.safety_level == SafetyLevel.LIMITED),
            "dangerous": sum(1 for s in segments if s.safety_level == SafetyLevel.DANGEROUS),
        }
        
        # Collect unique warnings
        all_warnings = set()
        for s in segments:
            all_warnings.update(s.weather_warnings)
        
        return {
            "total_distance_m": total_distance,
            "average_safety_score": weighted_safety / total_distance if total_distance > 0 else 0,
            "lane_split_distance_m": lane_split_distance,
            "lane_split_percentage": (lane_split_distance / total_distance * 100) if total_distance > 0 else 0,
            "segment_counts": segment_counts,
            "warnings": list(all_warnings),
        }
`

**Acceptance Criteria:**
- [ ] Segment analyzer processes all edge types
- [ ] Safety scores are accurate and consistent
- [ ] Lane splitting detection works correctly
- [ ] Weather integration modifies scores appropriately
- [ ] Summary statistics are accurate
- [ ] Unit tests cover all scenarios

---

### TASK 2.3.2: Create Segment API Endpoint
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 1.5 hours
- [ ] **Dependencies:** TASK 2.3.1

**Description:**
Create FastAPI endpoint for retrieving color-coded route segments.

**Files to Create/Modify:**
- api/routes/segments.py
- api/main.py

**Implementation:**

`python
# File: api/routes/segments.py

"""
Route segment analysis API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from motomap.routing.segment_analyzer import (
    RouteSegmentAnalyzer,
    SegmentAnalysis,
    SafetyLevel,
)
from motomap.weather import WeatherService, RoadConditionAssessor

router = APIRouter(prefix="/api/segments", tags=["segments"])

# Initialize services
weather_service = WeatherService()
assessor = RoadConditionAssessor()
analyzer = RouteSegmentAnalyzer(weather_assessor=assessor)


class SegmentResponse(BaseModel):
    """Single segment analysis response."""
    
    segment_id: int
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    length_m: float
    
    highway_type: str
    lanes: int
    maxspeed: int
    
    safety_score: float = Field(..., ge=0, le=1)
    safety_level: str
    lane_split_suitable: bool
    lane_split_score: float = Field(..., ge=0, le=1)
    
    color_hex: str
    stroke_width: int
    opacity: float
    
    weather_warnings: List[str] = []


class RouteSegmentsResponse(BaseModel):
    """Complete route segments response."""
    
    segments: List[SegmentResponse]
    summary: dict
    weather_enabled: bool


@router.post("/analyze", response_model=RouteSegmentsResponse)
async def analyze_route_segments(
    route_data: dict,
    include_weather: bool = Query(True, description="Include weather analysis"),
):
    """
    Analyze route segments for safety visualization.
    
    Accepts route data and returns color-coded segment analysis
    for map visualization.
    """
    try:
        edges = route_data.get("edges", [])
        if not edges:
            raise HTTPException(
                status_code=400,
                detail="No route edges provided"
            )
        
        # Get weather if requested
        weather_data = None
        if include_weather:
            # Get weather at route midpoint
            if edges:
                mid_edge = edges[len(edges) // 2]
                lat = mid_edge.get("lat", 41.0)
                lng = mid_edge.get("lng", 29.0)
                try:
                    weather_data = await weather_service.get_weather(lat, lng)
                except Exception:
                    pass  # Continue without weather
        
        # Analyze segments
        segments = analyzer.analyze_route(edges, weather_data)
        summary = analyzer.get_route_summary(segments)
        
        # Convert to response format
        segment_responses = []
        for seg in segments:
            segment_responses.append(SegmentResponse(
                segment_id=seg.segment_id,
                start_lat=seg.start_coord[0],
                start_lng=seg.start_coord[1],
                end_lat=seg.end_coord[0],
                end_lng=seg.end_coord[1],
                length_m=seg.length_m,
                highway_type=seg.highway_type,
                lanes=seg.lanes,
                maxspeed=seg.maxspeed,
                safety_score=seg.safety_score,
                safety_level=seg.safety_level.value,
                lane_split_suitable=seg.lane_split_suitable,
                lane_split_score=seg.lane_split_score,
                color_hex=seg.color_hex,
                stroke_width=seg.stroke_width,
                opacity=seg.opacity,
                weather_warnings=seg.weather_warnings,
            ))
        
        return RouteSegmentsResponse(
            segments=segment_responses,
            summary=summary,
            weather_enabled=weather_data is not None,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
`

---

### TASK 2.3.3: Create Mobile Colored Polyline Component
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** TASK 2.3.1, TASK 2.3.2

**Description:**
Create React Native component for rendering multi-colored route polylines
on the map based on segment analysis.

**Files to Create:**
- app/mobile/components/ColoredRoute.tsx

**Implementation:**

`	sx
// File: app/mobile/components/ColoredRoute.tsx

import React, { useMemo } from "react";
import { Polyline, Circle, Marker } from "react-native-maps";
import { View, Text, StyleSheet } from "react-native";
import { colors } from "../theme";

export type RouteSegment = {
  segment_id: number;
  start_lat: number;
  start_lng: number;
  end_lat: number;
  end_lng: number;
  safety_level: "safe" | "caution" | "limited" | "dangerous";
  lane_split_suitable: boolean;
  color_hex: string;
  stroke_width: number;
  opacity: number;
};

type ColoredRouteProps = {
  segments: RouteSegment[];
  showLaneSplitMarkers?: boolean;
  showLegend?: boolean;
  onSegmentPress?: (segment: RouteSegment) => void;
};

const SAFETY_COLORS = {
  safe: "#22C55E",
  caution: "#F59E0B",
  limited: "#F97316",
  dangerous: "#EF4444",
};

export function ColoredRoute({
  segments,
  showLaneSplitMarkers = true,
  showLegend = false,
  onSegmentPress,
}: ColoredRouteProps) {
  // Group consecutive segments with same color for smoother rendering
  const groupedSegments = useMemo(() => {
    const groups: {
      color: string;
      coordinates: { latitude: number; longitude: number }[];
      strokeWidth: number;
      opacity: number;
      segments: RouteSegment[];
    }[] = [];
    
    let currentGroup: typeof groups[0] | null = null;
    
    for (const segment of segments) {
      const coord = {
        latitude: segment.start_lat,
        longitude: segment.start_lng,
      };
      
      if (
        currentGroup &&
        currentGroup.color === segment.color_hex
      ) {
        currentGroup.coordinates.push(coord);
        currentGroup.segments.push(segment);
      } else {
        // Start new group
        if (currentGroup) {
          // Add end point of last segment
          const lastSeg = currentGroup.segments[currentGroup.segments.length - 1];
          currentGroup.coordinates.push({
            latitude: lastSeg.end_lat,
            longitude: lastSeg.end_lng,
          });
          groups.push(currentGroup);
        }
        
        currentGroup = {
          color: segment.color_hex,
          coordinates: [coord],
          strokeWidth: segment.stroke_width,
          opacity: segment.opacity,
          segments: [segment],
        };
      }
    }
    
    // Don't forget the last group
    if (currentGroup) {
      const lastSeg = currentGroup.segments[currentGroup.segments.length - 1];
      currentGroup.coordinates.push({
        latitude: lastSeg.end_lat,
        longitude: lastSeg.end_lng,
      });
      groups.push(currentGroup);
    }
    
    return groups;
  }, [segments]);
  
  // Find lane split transition points
  const laneSplitMarkers = useMemo(() => {
    if (!showLaneSplitMarkers) return [];
    
    const markers: {
      coordinate: { latitude: number; longitude: number };
      type: "start" | "end";
    }[] = [];
    
    let wasLaneSplitSuitable = false;
    
    for (const segment of segments) {
      if (segment.lane_split_suitable && !wasLaneSplitSuitable) {
        markers.push({
          coordinate: {
            latitude: segment.start_lat,
            longitude: segment.start_lng,
          },
          type: "start",
        });
      } else if (!segment.lane_split_suitable && wasLaneSplitSuitable) {
        markers.push({
          coordinate: {
            latitude: segment.start_lat,
            longitude: segment.start_lng,
          },
          type: "end",
        });
      }
      wasLaneSplitSuitable = segment.lane_split_suitable;
    }
    
    return markers;
  }, [segments, showLaneSplitMarkers]);
  
  return (
    <>
      {/* Render polylines */}
      {groupedSegments.map((group, index) => (
        <Polyline
          key={oute-}
          coordinates={group.coordinates}
          strokeColor={group.color}
          strokeWidth={group.strokeWidth}
          lineCap="round"
          lineJoin="round"
          tappable={!!onSegmentPress}
          onPress={() => {
            if (onSegmentPress && group.segments.length > 0) {
              onSegmentPress(group.segments[0]);
            }
          }}
        />
      ))}
      
      {/* Lane split markers */}
      {laneSplitMarkers.map((marker, index) => (
        <Marker
          key={lane-marker-}
          coordinate={marker.coordinate}
          anchor={{ x: 0.5, y: 0.5 }}
        >
          <View style={[
            styles.laneMarker,
            marker.type === "start" ? styles.laneStart : styles.laneEnd,
          ]}>
            <Text style={styles.laneMarkerText}>
              {marker.type === "start" ? "✂️" : "🚫"}
            </Text>
          </View>
        </Marker>
      ))}
      
      {/* Legend */}
      {showLegend && <RouteLegend />}
    </>
  );
}

function RouteLegend() {
  return (
    <View style={styles.legend}>
      <View style={styles.legendItem}>
        <View style={[styles.legendColor, { backgroundColor: SAFETY_COLORS.safe }]} />
        <Text style={styles.legendText}>Güvenli</Text>
      </View>
      <View style={styles.legendItem}>
        <View style={[styles.legendColor, { backgroundColor: SAFETY_COLORS.caution }]} />
        <Text style={styles.legendText}>Dikkatli</Text>
      </View>
      <View style={styles.legendItem}>
        <View style={[styles.legendColor, { backgroundColor: SAFETY_COLORS.limited }]} />
        <Text style={styles.legendText}>Sınırlı</Text>
      </View>
      <View style={styles.legendItem}>
        <View style={[styles.legendColor, { backgroundColor: SAFETY_COLORS.dangerous }]} />
        <Text style={styles.legendText}>Tehlikeli</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  laneMarker: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: "center",
    alignItems: "center",
  },
  laneStart: {
    backgroundColor: "#22C55E",
  },
  laneEnd: {
    backgroundColor: "#EF4444",
  },
  laneMarkerText: {
    fontSize: 14,
  },
  legend: {
    position: "absolute",
    bottom: 120,
    left: 16,
    backgroundColor: "rgba(8, 28, 80, 0.9)",
    borderRadius: 12,
    padding: 12,
  },
  legendItem: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 6,
  },
  legendColor: {
    width: 16,
    height: 4,
    borderRadius: 2,
    marginRight: 8,
  },
  legendText: {
    color: colors.textPrimary,
    fontSize: 12,
  },
});

export default ColoredRoute;
`

---

### TASK 2.3.4: Integrate Colored Routes in Map Screen
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** TASK 2.3.3

**Description:**
Update the map screen to use color-coded route visualization instead
of simple polylines.

**Files to Modify:**
- app/mobile/app/(tabs)/map.tsx

**Key Changes:**
1. Add toggle for safety overlay mode
2. Replace single Polyline with ColoredRoute component
3. Add segment analysis API call
4. Show segment details on tap
5. Add legend toggle

---

### TASK 2.3.5: Create Safety Mode Toggle Component
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 1 hour
- [ ] **Dependencies:** TASK 2.3.3

**Files to Create:**
- app/mobile/components/SafetyModeToggle.tsx

**Implementation:**

`	sx
// File: app/mobile/components/SafetyModeToggle.tsx

import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { colors, typography, spacing, radius } from "../theme";

type ViewMode = "standard" | "safety" | "lane-split";

type SafetyModeToggleProps = {
  activeMode: ViewMode;
  onModeChange: (mode: ViewMode) => void;
};

const MODES: { key: ViewMode; icon: string; label: string }[] = [
  { key: "standard", icon: "🗺️", label: "Standart" },
  { key: "safety", icon: "🛡️", label: "Güvenlik" },
  { key: "lane-split", icon: "✂️", label: "Şerit" },
];

export function SafetyModeToggle({
  activeMode,
  onModeChange,
}: SafetyModeToggleProps) {
  return (
    <View style={styles.container}>
      {MODES.map((mode) => (
        <TouchableOpacity
          key={mode.key}
          style={[
            styles.button,
            activeMode === mode.key && styles.buttonActive,
          ]}
          onPress={() => onModeChange(mode.key)}
        >
          <Text style={styles.icon}>{mode.icon}</Text>
          <Text
            style={[
              styles.label,
              activeMode === mode.key && styles.labelActive,
            ]}
          >
            {mode.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    backgroundColor: colors.surfaceGlass,
    borderRadius: radius.lg,
    padding: spacing.xs,
  },
  button: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.md,
  },
  buttonActive: {
    backgroundColor: colors.accentBlue,
  },
  icon: {
    fontSize: 16,
    marginRight: spacing.xs,
  },
  label: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  labelActive: {
    color: colors.textPrimary,
  },
});

export default SafetyModeToggle;
`

---


---

# MODULE 3: USER AUTHENTICATION & DATABASE
# =========================================

## 3.1 Overview

Complete user authentication and database system including registration,
login, JWT tokens, password management, and user profiles.

## 3.2 Architecture

`
┌─────────────────────────────────────────────────────────────────────────────┐
│                      USER AUTHENTICATION ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────────────┐   │
│  │ Mobile App   │───▶│ FastAPI Backend  │───▶│ PostgreSQL Database      │   │
│  │ (React Native)│   │ (JWT Auth)       │    │ (Users, Profiles)        │   │
│  └──────────────┘    └──────────────────┘    └──────────────────────────┘   │
│         │                    │                          │                    │
│         ▼                    ▼                          ▼                    │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────────────┐   │
│  │ Secure       │    │ Password Hashing │    │ User Model               │   │
│  │ Storage      │    │ (bcrypt)         │    │ - id, email, password    │   │
│  │ (expo-secure)│    │                  │    │ - name, avatar           │   │
│  └──────────────┘    └──────────────────┘    │ - motorcycles[]          │   │
│                                              │ - settings               │   │
│                                              └──────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
`

## 3.3 Database Schema

### 3.3.1 Users Table

`sql
-- File: migrations/001_create_users.sql

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Profile information
    username VARCHAR(50) UNIQUE,
    display_name VARCHAR(100),
    avatar_url TEXT,
    bio TEXT,
    
    -- Location
    city VARCHAR(100),
    country VARCHAR(100),
    
    -- Riding experience
    riding_since DATE,
    license_type VARCHAR(50), -- A1, A2, A
    total_km INTEGER DEFAULT 0,
    
    -- Settings
    preferred_language VARCHAR(10) DEFAULT 'tr',
    distance_unit VARCHAR(10) DEFAULT 'km',
    theme VARCHAR(20) DEFAULT 'dark',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    is_premium BOOLEAN DEFAULT FALSE,
    
    -- Indexes
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_city ON users(city);
CREATE INDEX idx_users_created_at ON users(created_at);
`

### 3.3.2 Motorcycles Table

`sql
-- File: migrations/002_create_motorcycles.sql

CREATE TYPE motorcycle_type AS ENUM (
    'naked', 'sport', 'touring', 'adventure', 
    'cruiser', 'scooter', 'classic', 'dual_sport',
    'enduro', 'supermoto', 'cafe_racer', 'bobber'
);

CREATE TABLE motorcycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Basic info
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INTEGER,
    cc INTEGER NOT NULL,
    type motorcycle_type NOT NULL,
    
    -- Additional details
    color VARCHAR(50),
    nickname VARCHAR(100),
    vin VARCHAR(17),
    license_plate VARCHAR(20),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_primary BOOLEAN DEFAULT FALSE,
    
    -- Stats
    total_km INTEGER DEFAULT 0,
    total_routes INTEGER DEFAULT 0,
    
    -- Metadata
    photo_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Only one primary motorcycle per user
    CONSTRAINT unique_primary_per_user 
        EXCLUDE USING btree (user_id WITH =) 
        WHERE (is_primary = TRUE)
);

CREATE INDEX idx_motorcycles_user_id ON motorcycles(user_id);
CREATE INDEX idx_motorcycles_brand ON motorcycles(brand);
CREATE INDEX idx_motorcycles_cc ON motorcycles(cc);
CREATE INDEX idx_motorcycles_type ON motorcycles(type);
`

### 3.3.3 Sessions Table (Refresh Tokens)

`sql
-- File: migrations/003_create_sessions.sql

CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Token info
    refresh_token_hash VARCHAR(255) NOT NULL,
    
    -- Device info
    device_id VARCHAR(255),
    device_name VARCHAR(255),
    device_type VARCHAR(50), -- android, ios, web
    app_version VARCHAR(20),
    
    -- Security
    ip_address INET,
    user_agent TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    CONSTRAINT unique_device_per_user 
        UNIQUE (user_id, device_id)
);

CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_refresh_token ON user_sessions(refresh_token_hash);
CREATE INDEX idx_sessions_expires_at ON user_sessions(expires_at);
`

---

## 3.4 Implementation Tasks

### TASK 3.4.1: Setup PostgreSQL Database
- [ ] **Priority:** CRITICAL
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** None

**Description:**
Setup PostgreSQL database with Docker or managed service, create
initial database and user.

**Docker Compose:**

`yaml
# File: docker-compose.yml

version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: motomap_db
    environment:
      POSTGRES_USER: motomap
      POSTGRES_PASSWORD: 
      POSTGRES_DB: motomap
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U motomap"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: motomap_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
`

---

### TASK 3.4.2: Create Database Models (SQLAlchemy)
- [ ] **Priority:** CRITICAL
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** TASK 3.4.1

**Files to Create:**
- api/models/__init__.py
- api/models/user.py
- api/models/motorcycle.py
- api/models/session.py
- api/database.py

**Implementation:**

`python
# File: api/database.py

"""
Database connection and session management.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://motomap:motomap_secret@localhost:5432/motomap"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_size=20,
    max_overflow=10,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    """FastAPI dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """Context manager for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections."""
    await engine.dispose()
`

`python
# File: api/models/user.py

"""
User database model.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Integer, String, Text, Date,
    ForeignKey, Enum, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.database import Base


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    username = Column(String(50), unique=True, index=True)
    display_name = Column(String(100))
    avatar_url = Column(Text)
    bio = Column(Text)
    
    # Location
    city = Column(String(100), index=True)
    country = Column(String(100))
    
    # Riding info
    riding_since = Column(Date)
    license_type = Column(String(50))
    total_km = Column(Integer, default=0)
    
    # Settings
    preferred_language = Column(String(10), default="tr")
    distance_unit = Column(String(10), default="km")
    theme = Column(String(20), default="dark")
    notifications_enabled = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    
    # Relationships
    motorcycles = relationship("Motorcycle", back_populates="owner", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def primary_motorcycle(self) -> Optional["Motorcycle"]:
        """Get user's primary motorcycle."""
        for moto in self.motorcycles:
            if moto.is_primary:
                return moto
        return self.motorcycles[0] if self.motorcycles else None
`

`python
# File: api/models/motorcycle.py

"""
Motorcycle database model.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean, Column, DateTime, Integer, String, Text,
    ForeignKey, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.database import Base


class MotorcycleType(PyEnum):
    """Motorcycle type enumeration."""
    NAKED = "naked"
    SPORT = "sport"
    TOURING = "touring"
    ADVENTURE = "adventure"
    CRUISER = "cruiser"
    SCOOTER = "scooter"
    CLASSIC = "classic"
    DUAL_SPORT = "dual_sport"
    ENDURO = "enduro"
    SUPERMOTO = "supermoto"
    CAFE_RACER = "cafe_racer"
    BOBBER = "bobber"


class Motorcycle(Base):
    """Motorcycle model."""
    
    __tablename__ = "motorcycles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Basic info
    brand = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    year = Column(Integer)
    cc = Column(Integer, nullable=False, index=True)
    type = Column(
        Enum(MotorcycleType),
        nullable=False,
        index=True
    )
    
    # Additional details
    color = Column(String(50))
    nickname = Column(String(100))
    vin = Column(String(17))
    license_plate = Column(String(20))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)
    
    # Stats
    total_km = Column(Integer, default=0)
    total_routes = Column(Integer, default=0)
    
    # Media
    photo_url = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="motorcycles")
    
    def __repr__(self):
        return f"<Motorcycle {self.brand} {self.model} ({self.cc}cc)>"
    
    @property
    def full_name(self) -> str:
        """Get full motorcycle name."""
        parts = [self.brand, self.model]
        if self.year:
            parts.append(f"({self.year})")
        return " ".join(parts)
`

---

### TASK 3.4.3: Create Authentication Service
- [ ] **Priority:** CRITICAL
- [ ] **Estimated Effort:** 4 hours
- [ ] **Dependencies:** TASK 3.4.2

**Files to Create:**
- api/services/auth.py
- api/core/security.py

**Implementation:**

`python
# File: api/core/security.py

"""
Security utilities for password hashing and JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import os
import secrets

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # user_id
    exp: datetime
    type: str  # "access" or "refresh"
    jti: Optional[str] = None  # JWT ID for refresh tokens


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password
        hashed: Hashed password
        
    Returns:
        True if password matches
    """
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def create_access_token(
    user_id: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User's UUID
        expires_delta: Optional custom expiration
        
    Returns:
        Encoded JWT token
    """
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow(),
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    user_id: str,
    expires_delta: Optional[timedelta] = None,
) -> Tuple[str, str]:
    """
    Create a JWT refresh token.
    
    Args:
        user_id: User's UUID
        expires_delta: Optional custom expiration
        
    Returns:
        Tuple of (encoded token, token ID for storage)
    """
    jti = secrets.token_urlsafe(32)
    expire = datetime.utcnow() + (
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "jti": jti,
        "iat": datetime.utcnow(),
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti


def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: Encoded JWT token
        
    Returns:
        TokenPayload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(
            sub=payload["sub"],
            exp=datetime.fromtimestamp(payload["exp"]),
            type=payload.get("type", "access"),
            jti=payload.get("jti"),
        )
    except JWTError:
        return None


def hash_refresh_token(token: str) -> str:
    """Hash refresh token for storage."""
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()
`

`python
# File: api/services/auth.py

"""
Authentication service for user registration, login, and token management.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.user import User
from api.models.session import UserSession
from api.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_refresh_token,
    REFRESH_TOKEN_EXPIRE_DAYS,
)


class AuthError(Exception):
    """Base authentication error."""
    pass


class InvalidCredentialsError(AuthError):
    """Invalid email or password."""
    pass


class UserExistsError(AuthError):
    """User already exists."""
    pass


class InvalidTokenError(AuthError):
    """Invalid or expired token."""
    pass


class AuthService:
    """
    Authentication service.
    
    Handles user registration, login, logout, and token management.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize auth service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def register(
        self,
        email: str,
        password: str,
        display_name: Optional[str] = None,
    ) -> User:
        """
        Register a new user.
        
        Args:
            email: User's email
            password: Plain text password
            display_name: Optional display name
            
        Returns:
            Created user
            
        Raises:
            UserExistsError: If email already registered
        """
        # Check if user exists
        existing = await self.get_user_by_email(email)
        if existing:
            raise UserExistsError(f"User with email {email} already exists")
        
        # Create user
        user = User(
            email=email.lower().strip(),
            password_hash=hash_password(password),
            display_name=display_name,
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def login(
        self,
        email: str,
        password: str,
        device_info: Optional[dict] = None,
    ) -> Tuple[User, str, str]:
        """
        Authenticate user and create tokens.
        
        Args:
            email: User's email
            password: Plain text password
            device_info: Optional device information
            
        Returns:
            Tuple of (user, access_token, refresh_token)
            
        Raises:
            InvalidCredentialsError: If credentials are invalid
        """
        # Find user
        user = await self.get_user_by_email(email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")
        
        # Check password
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise InvalidCredentialsError("Account is disabled")
        
        # Create tokens
        access_token = create_access_token(str(user.id))
        refresh_token, jti = create_refresh_token(str(user.id))
        
        # Store refresh token session
        session = UserSession(
            user_id=user.id,
            refresh_token_hash=hash_refresh_token(refresh_token),
            device_id=device_info.get("device_id") if device_info else None,
            device_name=device_info.get("device_name") if device_info else None,
            device_type=device_info.get("device_type") if device_info else None,
            app_version=device_info.get("app_version") if device_info else None,
            ip_address=device_info.get("ip_address") if device_info else None,
            user_agent=device_info.get("user_agent") if device_info else None,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
        
        self.db.add(session)
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        
        await self.db.commit()
        
        return user, access_token, refresh_token
    
    async def logout(self, refresh_token: str) -> bool:
        """
        Logout user by invalidating refresh token.
        
        Args:
            refresh_token: Refresh token to invalidate
            
        Returns:
            True if logout successful
        """
        token_hash = hash_refresh_token(refresh_token)
        
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.refresh_token_hash == token_hash,
                UserSession.is_active == True
            )
        )
        session = result.scalar_one_or_none()
        
        if session:
            session.is_active = False
            await self.db.commit()
            return True
        
        return False
    
    async def logout_all(self, user_id: UUID) -> int:
        """
        Logout user from all devices.
        
        Args:
            user_id: User's UUID
            
        Returns:
            Number of sessions invalidated
        """
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        )
        sessions = result.scalars().all()
        
        count = 0
        for session in sessions:
            session.is_active = False
            count += 1
        
        await self.db.commit()
        return count
    
    async def refresh_tokens(
        self,
        refresh_token: str,
    ) -> Tuple[str, str]:
        """
        Refresh access and refresh tokens.
        
        Args:
            refresh_token: Current refresh token
            
        Returns:
            Tuple of (new_access_token, new_refresh_token)
            
        Raises:
            InvalidTokenError: If refresh token is invalid
        """
        # Decode token
        payload = decode_token(refresh_token)
        if not payload or payload.type != "refresh":
            raise InvalidTokenError("Invalid refresh token")
        
        # Find session
        token_hash = hash_refresh_token(refresh_token)
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.refresh_token_hash == token_hash,
                UserSession.is_active == True
            )
        )
        session = result.scalar_one_or_none()
        
        if not session or session.expires_at < datetime.utcnow():
            raise InvalidTokenError("Refresh token expired or invalid")
        
        # Create new tokens
        user_id = payload.sub
        new_access_token = create_access_token(user_id)
        new_refresh_token, new_jti = create_refresh_token(user_id)
        
        # Update session
        session.refresh_token_hash = hash_refresh_token(new_refresh_token)
        session.last_used_at = datetime.utcnow()
        session.expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        await self.db.commit()
        
        return new_access_token, new_refresh_token
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> bool:
        """
        Change user's password.
        
        Args:
            user_id: User's UUID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if password changed
            
        Raises:
            InvalidCredentialsError: If current password is wrong
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise InvalidCredentialsError("User not found")
        
        if not verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError("Current password is incorrect")
        
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        # Invalidate all sessions (force re-login)
        await self.logout_all(user_id)
        
        await self.db.commit()
        return True
`

---

### TASK 3.4.4: Create Auth API Endpoints
- [ ] **Priority:** CRITICAL
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** TASK 3.4.3

**Files to Create:**
- api/routes/auth.py

**Implementation:**

`python
# File: api/routes/auth.py

"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.services.auth import (
    AuthService,
    InvalidCredentialsError,
    UserExistsError,
    InvalidTokenError,
)
from api.core.security import decode_token

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


# Request/Response Models

class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)
    
    @validator("password")
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


class UserResponse(BaseModel):
    """User profile response."""
    id: UUID
    email: str
    username: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]
    city: Optional[str]
    country: Optional[str]
    is_premium: bool
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Full auth response with user and tokens."""
    user: UserResponse
    tokens: TokenResponse


class RefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Change password request."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator("new_password")
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


# Dependency for getting current user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """
    Dependency to get current authenticated user.
    
    Extracts and validates JWT from Authorization header.
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload or payload.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(UUID(payload.sub))
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# Endpoints

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.
    
    Creates a new user and returns authentication tokens.
    """
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.register(
            email=request.email,
            password=request.password,
            display_name=request.display_name,
        )
        
        # Auto-login after registration
        device_info = {
            "ip_address": req.client.host if req.client else None,
            "user_agent": req.headers.get("user-agent"),
        }
        
        user, access_token, refresh_token = await auth_service.login(
            email=request.email,
            password=request.password,
            device_info=device_info,
        )
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
            ),
        )
    
    except UserExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email and password.
    
    Returns authentication tokens for the user.
    """
    auth_service = AuthService(db)
    
    device_info = {
        "device_id": request.device_id,
        "device_name": request.device_name,
        "device_type": request.device_type,
        "ip_address": req.client.host if req.client else None,
        "user_agent": req.headers.get("user-agent"),
    }
    
    try:
        user, access_token, refresh_token = await auth_service.login(
            email=request.email,
            password=request.password,
            device_info=device_info,
        )
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
            ),
        )
    
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Logout and invalidate refresh token.
    """
    auth_service = AuthService(db)
    await auth_service.logout(request.refresh_token)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout from all devices.
    
    Requires authentication.
    """
    auth_service = AuthService(db)
    await auth_service.logout_all(user.id)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access and refresh tokens.
    """
    auth_service = AuthService(db)
    
    try:
        access_token, refresh_token = await auth_service.refresh_tokens(
            request.refresh_token
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    user = Depends(get_current_user),
):
    """
    Get current user's profile.
    
    Requires authentication.
    """
    return UserResponse.model_validate(user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: ChangePasswordRequest,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change user's password.
    
    Requires authentication. Will logout from all devices.
    """
    auth_service = AuthService(db)
    
    try:
        await auth_service.change_password(
            user_id=user.id,
            current_password=request.current_password,
            new_password=request.new_password,
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
`

---


---

# MODULE 4: USER PROFILE & MOTORCYCLE GARAGE
# ===========================================

## 4.1 Overview

User profile management and motorcycle garage system allowing users to
manage their motorcycles, track riding statistics, and customize preferences.

## 4.2 Implementation Tasks

### TASK 4.2.1: Create Profile Service
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2.5 hours
- [ ] **Dependencies:** Module 3 (Authentication)

**Files to Create:**
- api/services/profile.py

**Implementation:**

`python
# File: api/services/profile.py

"""
User profile management service.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.models.user import User
from api.models.motorcycle import Motorcycle, MotorcycleType


class ProfileService:
    """
    User profile management service.
    
    Handles profile updates, statistics, and preferences.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_profile(self, user_id: UUID) -> Optional[User]:
        """Get user profile with motorcycles."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.motorcycles))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_profile(
        self,
        user_id: UUID,
        display_name: Optional[str] = None,
        username: Optional[str] = None,
        bio: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        riding_since: Optional[date] = None,
        license_type: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> User:
        """Update user profile."""
        user = await self.get_profile(user_id)
        if not user:
            raise ValueError("User not found")
        
        if display_name is not None:
            user.display_name = display_name
        if username is not None:
            # Check username uniqueness
            existing = await self.db.execute(
                select(User).where(
                    User.username == username,
                    User.id != user_id
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError("Username already taken")
            user.username = username
        if bio is not None:
            user.bio = bio
        if city is not None:
            user.city = city
        if country is not None:
            user.country = country
        if riding_since is not None:
            user.riding_since = riding_since
        if license_type is not None:
            user.license_type = license_type
        if avatar_url is not None:
            user.avatar_url = avatar_url
        
        user.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_settings(
        self,
        user_id: UUID,
        preferred_language: Optional[str] = None,
        distance_unit: Optional[str] = None,
        theme: Optional[str] = None,
        notifications_enabled: Optional[bool] = None,
    ) -> User:
        """Update user settings."""
        user = await self.get_profile(user_id)
        if not user:
            raise ValueError("User not found")
        
        if preferred_language is not None:
            user.preferred_language = preferred_language
        if distance_unit is not None:
            user.distance_unit = distance_unit
        if theme is not None:
            user.theme = theme
        if notifications_enabled is not None:
            user.notifications_enabled = notifications_enabled
        
        user.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_statistics(self, user_id: UUID) -> dict:
        """Get user riding statistics."""
        user = await self.get_profile(user_id)
        if not user:
            return {}
        
        # Calculate stats
        total_motorcycles = len(user.motorcycles)
        total_km = sum(m.total_km for m in user.motorcycles)
        total_routes = sum(m.total_routes for m in user.motorcycles)
        
        # Experience level
        if user.riding_since:
            years_riding = (date.today() - user.riding_since).days // 365
        else:
            years_riding = 0
        
        return {
            "total_motorcycles": total_motorcycles,
            "total_km": total_km,
            "total_routes": total_routes,
            "years_riding": years_riding,
            "member_since": user.created_at.isoformat(),
            "is_premium": user.is_premium,
        }
`

---

### TASK 4.2.2: Create Motorcycle Service
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** TASK 4.2.1

**Files to Create:**
- api/services/motorcycle.py

**Implementation:**

`python
# File: api/services/motorcycle.py

"""
Motorcycle garage management service.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.motorcycle import Motorcycle, MotorcycleType


class MotorcycleService:
    """
    Motorcycle garage management service.
    """
    
    MAX_MOTORCYCLES_FREE = 3
    MAX_MOTORCYCLES_PREMIUM = 10
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_motorcycles(
        self,
        user_id: UUID,
        active_only: bool = False,
    ) -> List[Motorcycle]:
        """Get all motorcycles for a user."""
        query = select(Motorcycle).where(Motorcycle.user_id == user_id)
        if active_only:
            query = query.where(Motorcycle.is_active == True)
        query = query.order_by(Motorcycle.is_primary.desc(), Motorcycle.created_at)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_motorcycle(
        self,
        motorcycle_id: UUID,
        user_id: UUID,
    ) -> Optional[Motorcycle]:
        """Get a specific motorcycle."""
        result = await self.db.execute(
            select(Motorcycle).where(
                Motorcycle.id == motorcycle_id,
                Motorcycle.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()
    
    async def add_motorcycle(
        self,
        user_id: UUID,
        brand: str,
        model: str,
        cc: int,
        type: MotorcycleType,
        year: Optional[int] = None,
        color: Optional[str] = None,
        nickname: Optional[str] = None,
        is_premium: bool = False,
    ) -> Motorcycle:
        """Add a new motorcycle to user's garage."""
        # Check motorcycle limit
        current_count = len(await self.get_user_motorcycles(user_id))
        max_allowed = self.MAX_MOTORCYCLES_PREMIUM if is_premium else self.MAX_MOTORCYCLES_FREE
        
        if current_count >= max_allowed:
            raise ValueError(
                f"Maximum {max_allowed} motorcycles allowed. "
                "Upgrade to premium for more."
            )
        
        # First motorcycle is primary by default
        is_primary = current_count == 0
        
        motorcycle = Motorcycle(
            user_id=user_id,
            brand=brand,
            model=model,
            cc=cc,
            type=type,
            year=year,
            color=color,
            nickname=nickname,
            is_primary=is_primary,
        )
        
        self.db.add(motorcycle)
        await self.db.commit()
        await self.db.refresh(motorcycle)
        
        return motorcycle
    
    async def update_motorcycle(
        self,
        motorcycle_id: UUID,
        user_id: UUID,
        **updates,
    ) -> Motorcycle:
        """Update motorcycle details."""
        motorcycle = await self.get_motorcycle(motorcycle_id, user_id)
        if not motorcycle:
            raise ValueError("Motorcycle not found")
        
        allowed_fields = {
            "brand", "model", "cc", "type", "year", "color",
            "nickname", "vin", "license_plate", "is_active", "photo_url"
        }
        
        for field, value in updates.items():
            if field in allowed_fields and value is not None:
                setattr(motorcycle, field, value)
        
        motorcycle.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(motorcycle)
        
        return motorcycle
    
    async def set_primary(
        self,
        motorcycle_id: UUID,
        user_id: UUID,
    ) -> Motorcycle:
        """Set a motorcycle as primary."""
        motorcycle = await self.get_motorcycle(motorcycle_id, user_id)
        if not motorcycle:
            raise ValueError("Motorcycle not found")
        
        # Remove primary from others
        await self.db.execute(
            update(Motorcycle)
            .where(Motorcycle.user_id == user_id)
            .values(is_primary=False)
        )
        
        # Set this one as primary
        motorcycle.is_primary = True
        await self.db.commit()
        await self.db.refresh(motorcycle)
        
        return motorcycle
    
    async def delete_motorcycle(
        self,
        motorcycle_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Delete a motorcycle."""
        motorcycle = await self.get_motorcycle(motorcycle_id, user_id)
        if not motorcycle:
            return False
        
        was_primary = motorcycle.is_primary
        
        await self.db.delete(motorcycle)
        await self.db.commit()
        
        # If deleted primary, make another one primary
        if was_primary:
            remaining = await self.get_user_motorcycles(user_id)
            if remaining:
                remaining[0].is_primary = True
                await self.db.commit()
        
        return True
    
    async def add_km(
        self,
        motorcycle_id: UUID,
        user_id: UUID,
        km: int,
    ) -> Motorcycle:
        """Add kilometers to motorcycle."""
        motorcycle = await self.get_motorcycle(motorcycle_id, user_id)
        if not motorcycle:
            raise ValueError("Motorcycle not found")
        
        motorcycle.total_km += km
        motorcycle.total_routes += 1
        await self.db.commit()
        await self.db.refresh(motorcycle)
        
        return motorcycle
`

---

### TASK 4.2.3: Create Profile & Motorcycle API Endpoints
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2.5 hours
- [ ] **Dependencies:** TASK 4.2.1, TASK 4.2.2

**Files to Create:**
- api/routes/profile.py
- api/routes/motorcycles.py

---

### TASK 4.2.4: Mobile Profile Screen
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** TASK 4.2.3

**Files to Create:**
- app/mobile/app/(tabs)/profile.tsx

**Implementation:**

`	sx
// File: app/mobile/app/(tabs)/profile.tsx

import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";
import { router } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";

import { useAuth } from "../../context/AuthContext";
import { GlassCard } from "../../components/GlassCard";
import { StatCard } from "../../components/StatCard";
import { colors, typography, spacing, radius } from "../../theme";

export default function ProfileScreen() {
  const { user, isLoading, logout } = useAuth();
  const [stats, setStats] = useState<any>(null);
  
  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.accentBlue} />
      </View>
    );
  }
  
  if (!user) {
    return (
      <View style={styles.container}>
        <GlassCard style={styles.loginPrompt}>
          <Ionicons name="person-circle-outline" size={64} color={colors.textSecondary} />
          <Text style={styles.loginTitle}>Hesabınıza Giriş Yapın</Text>
          <Text style={styles.loginSubtitle}>
            Profilinizi görüntülemek ve motosikletlerinizi yönetmek için giriş yapın
          </Text>
          <TouchableOpacity
            style={styles.loginButton}
            onPress={() => router.push("/auth/login")}
          >
            <Text style={styles.loginButtonText}>Giriş Yap</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.registerButton}
            onPress={() => router.push("/auth/register")}
          >
            <Text style={styles.registerButtonText}>Kayıt Ol</Text>
          </TouchableOpacity>
        </GlassCard>
      </View>
    );
  }
  
  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <LinearGradient
        colors={[colors.bgSecondary, colors.bgPrimary]}
        style={styles.header}
      >
        <View style={styles.avatarContainer}>
          {user.avatar_url ? (
            <Image source={{ uri: user.avatar_url }} style={styles.avatar} />
          ) : (
            <View style={styles.avatarPlaceholder}>
              <Text style={styles.avatarText}>
                {user.display_name?.[0] || user.email[0].toUpperCase()}
              </Text>
            </View>
          )}
          {user.is_premium && (
            <View style={styles.premiumBadge}>
              <Text style={styles.premiumText}>⭐ PRO</Text>
            </View>
          )}
        </View>
        
        <Text style={styles.displayName}>
          {user.display_name || "Motosikletçi"}
        </Text>
        {user.username && (
          <Text style={styles.username}>@{user.username}</Text>
        )}
        {user.city && (
          <Text style={styles.location}>📍 {user.city}, {user.country}</Text>
        )}
      </LinearGradient>
      
      {/* Stats */}
      <View style={styles.statsRow}>
        <StatCard
          icon="��️"
          value={stats?.total_motorcycles || 0}
          label="Motor"
          compact
        />
        <StatCard
          icon="🛣️"
          value={${((stats?.total_km || 0) / 1000).toFixed(0)}k}
          label="Kilometre"
          compact
        />
        <StatCard
          icon="🗺️"
          value={stats?.total_routes || 0}
          label="Rota"
          compact
        />
        <StatCard
          icon="📅"
          value={stats?.years_riding || 0}
          label="Yıl"
          compact
        />
      </View>
      
      {/* Menu Items */}
      <View style={styles.menuSection}>
        <MenuItem
          icon="bicycle-outline"
          title="Garajım"
          subtitle="Motosikletlerini yönet"
          onPress={() => router.push("/garage")}
        />
        <MenuItem
          icon="bookmark-outline"
          title="Kayıtlı Rotalar"
          subtitle="Favorilerine göz at"
          onPress={() => router.push("/saved-routes")}
        />
        <MenuItem
          icon="people-outline"
          title="Topluluklarım"
          subtitle="Gruplara katıl, sohbet et"
          onPress={() => router.push("/communities")}
        />
        <MenuItem
          icon="trophy-outline"
          title="Başarılar"
          subtitle="Rozetler ve puanlar"
          onPress={() => router.push("/achievements")}
        />
        <MenuItem
          icon="settings-outline"
          title="Ayarlar"
          subtitle="Hesap ve uygulama ayarları"
          onPress={() => router.push("/settings")}
        />
      </View>
      
      {/* Logout */}
      <TouchableOpacity style={styles.logoutButton} onPress={logout}>
        <Ionicons name="log-out-outline" size={20} color={colors.danger} />
        <Text style={styles.logoutText}>Çıkış Yap</Text>
      </TouchableOpacity>
      
      <View style={styles.bottomPadding} />
    </ScrollView>
  );
}

function MenuItem({ icon, title, subtitle, onPress }: {
  icon: string;
  title: string;
  subtitle: string;
  onPress: () => void;
}) {
  return (
    <TouchableOpacity style={styles.menuItem} onPress={onPress}>
      <View style={styles.menuIconContainer}>
        <Ionicons name={icon as any} size={24} color={colors.accentBlue} />
      </View>
      <View style={styles.menuContent}>
        <Text style={styles.menuTitle}>{title}</Text>
        <Text style={styles.menuSubtitle}>{subtitle}</Text>
      </View>
      <Ionicons name="chevron-forward" size={20} color={colors.textTertiary} />
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: colors.bgPrimary,
  },
  header: {
    alignItems: "center",
    paddingTop: 60,
    paddingBottom: spacing.xl,
    borderBottomLeftRadius: radius.xl,
    borderBottomRightRadius: radius.xl,
  },
  avatarContainer: {
    position: "relative",
    marginBottom: spacing.md,
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    borderWidth: 3,
    borderColor: colors.accentBlue,
  },
  avatarPlaceholder: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: colors.surfaceGlass,
    justifyContent: "center",
    alignItems: "center",
    borderWidth: 3,
    borderColor: colors.accentBlue,
  },
  avatarText: {
    ...typography.heroMedium,
    color: colors.textPrimary,
  },
  premiumBadge: {
    position: "absolute",
    bottom: 0,
    right: -10,
    backgroundColor: colors.warning,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
  },
  premiumText: {
    ...typography.caption,
    color: colors.textOnLight,
  },
  displayName: {
    ...typography.h1,
    color: colors.textPrimary,
  },
  username: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  location: {
    ...typography.body,
    color: colors.textTertiary,
    marginTop: spacing.xs,
  },
  statsRow: {
    flexDirection: "row",
    justifyContent: "space-around",
    paddingHorizontal: spacing.md,
    marginTop: -spacing.lg,
    marginBottom: spacing.lg,
  },
  menuSection: {
    paddingHorizontal: spacing.md,
  },
  menuItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceGlass,
    borderRadius: radius.lg,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  menuIconContainer: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.accentBlueGlow,
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.md,
  },
  menuContent: {
    flex: 1,
  },
  menuTitle: {
    ...typography.bodyBold,
    color: colors.textPrimary,
  },
  menuSubtitle: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  logoutButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    marginTop: spacing.xl,
    marginHorizontal: spacing.md,
    padding: spacing.md,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.danger,
  },
  logoutText: {
    ...typography.bodyBold,
    color: colors.danger,
    marginLeft: spacing.sm,
  },
  bottomPadding: {
    height: 100,
  },
  // Login prompt styles
  loginPrompt: {
    margin: spacing.lg,
    padding: spacing.xl,
    alignItems: "center",
  },
  loginTitle: {
    ...typography.h2,
    color: colors.textPrimary,
    marginTop: spacing.lg,
    textAlign: "center",
  },
  loginSubtitle: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: "center",
    marginTop: spacing.sm,
    marginBottom: spacing.lg,
  },
  loginButton: {
    backgroundColor: colors.accentBlue,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xxl,
    borderRadius: radius.pill,
    marginBottom: spacing.sm,
  },
  loginButtonText: {
    ...typography.bodyBold,
    color: colors.textPrimary,
  },
  registerButton: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xxl,
  },
  registerButtonText: {
    ...typography.body,
    color: colors.accentBlue,
  },
});
`

---

### TASK 4.2.5: Mobile Garage Screen Enhancement
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2.5 hours
- [ ] **Dependencies:** TASK 4.2.3

**Description:**
Enhance the existing garage screen to use the backend API and support
full CRUD operations for motorcycles.

---

### TASK 4.2.6: Mobile Auth Context
- [ ] **Priority:** CRITICAL
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** TASK 3.4.4

**Files to Create:**
- app/mobile/context/AuthContext.tsx
- app/mobile/utils/secureStorage.ts

**Implementation:**

`	sx
// File: app/mobile/context/AuthContext.tsx

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import * as SecureStore from "expo-secure-store";
import { router } from "expo-router";
import { API_URL } from "../utils/api";

type User = {
  id: string;
  email: string;
  username?: string;
  display_name?: string;
  avatar_url?: string;
  city?: string;
  country?: string;
  is_premium: boolean;
};

type AuthContextType = {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | null>(null);

const TOKEN_KEYS = {
  ACCESS: "motomap_access_token",
  REFRESH: "motomap_refresh_token",
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Check for existing session on mount
  useEffect(() => {
    checkAuth();
  }, []);
  
  const checkAuth = async () => {
    try {
      const accessToken = await SecureStore.getItemAsync(TOKEN_KEYS.ACCESS);
      if (accessToken) {
        await fetchUser(accessToken);
      }
    } catch (error) {
      console.error("Auth check failed:", error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const fetchUser = async (token: string) => {
    try {
      const response = await fetch(\/api/auth/me, {
        headers: {
          Authorization: Bearer \,
        },
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else if (response.status === 401) {
        // Try refresh
        await refreshTokens();
      }
    } catch (error) {
      console.error("Fetch user failed:", error);
    }
  };
  
  const refreshTokens = async () => {
    try {
      const refreshToken = await SecureStore.getItemAsync(TOKEN_KEYS.REFRESH);
      if (!refreshToken) {
        await logout();
        return;
      }
      
      const response = await fetch(\/api/auth/refresh, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      
      if (response.ok) {
        const { access_token, refresh_token } = await response.json();
        await SecureStore.setItemAsync(TOKEN_KEYS.ACCESS, access_token);
        await SecureStore.setItemAsync(TOKEN_KEYS.REFRESH, refresh_token);
        await fetchUser(access_token);
      } else {
        await logout();
      }
    } catch (error) {
      console.error("Token refresh failed:", error);
      await logout();
    }
  };
  
  const login = async (email: string, password: string) => {
    const response = await fetch(\/api/auth/login, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Giriş başarısız");
    }
    
    const { user: userData, tokens } = await response.json();
    
    await SecureStore.setItemAsync(TOKEN_KEYS.ACCESS, tokens.access_token);
    await SecureStore.setItemAsync(TOKEN_KEYS.REFRESH, tokens.refresh_token);
    
    setUser(userData);
    router.replace("/(tabs)");
  };
  
  const register = async (email: string, password: string, displayName?: string) => {
    const response = await fetch(\/api/auth/register, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, display_name: displayName }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Kayıt başarısız");
    }
    
    const { user: userData, tokens } = await response.json();
    
    await SecureStore.setItemAsync(TOKEN_KEYS.ACCESS, tokens.access_token);
    await SecureStore.setItemAsync(TOKEN_KEYS.REFRESH, tokens.refresh_token);
    
    setUser(userData);
    router.replace("/(tabs)");
  };
  
  const logout = async () => {
    try {
      const refreshToken = await SecureStore.getItemAsync(TOKEN_KEYS.REFRESH);
      if (refreshToken) {
        await fetch(\/api/auth/logout, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      }
    } catch (error) {
      // Ignore logout API errors
    }
    
    await SecureStore.deleteItemAsync(TOKEN_KEYS.ACCESS);
    await SecureStore.deleteItemAsync(TOKEN_KEYS.REFRESH);
    setUser(null);
    router.replace("/");
  };
  
  const refreshUser = async () => {
    const accessToken = await SecureStore.getItemAsync(TOKEN_KEYS.ACCESS);
    if (accessToken) {
      await fetchUser(accessToken);
    }
  };
  
  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
`

---

# MODULE 5: COMMUNITY PLATFORM
# ============================

## 5.1 Overview

Community platform enabling riders to join brand-based or interest-based
groups, chat with other riders, and request/offer help.

## 5.2 Database Schema

### 5.2.1 Communities Table

`sql
-- File: migrations/004_create_communities.sql

CREATE TYPE community_type AS ENUM (
    'brand',      -- Motorcycle brand (Harley, Honda, etc.)
    'style',      -- Riding style (Touring, Sport, etc.)
    'region',     -- Geographic region
    'interest',   -- Special interest (Racing, Restoration, etc.)
    'event'       -- Event-based temporary community
);

CREATE TABLE communities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic info
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    type community_type NOT NULL,
    
    -- Branding
    icon_url TEXT,
    banner_url TEXT,
    color VARCHAR(7), -- Hex color
    
    -- Settings
    is_public BOOLEAN DEFAULT TRUE,
    is_official BOOLEAN DEFAULT FALSE,
    requires_approval BOOLEAN DEFAULT FALSE,
    
    -- Stats (denormalized for performance)
    member_count INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- For brand communities
    brand_name VARCHAR(100),
    
    -- For region communities
    region_country VARCHAR(100),
    region_city VARCHAR(100)
);

CREATE INDEX idx_communities_type ON communities(type);
CREATE INDEX idx_communities_slug ON communities(slug);
CREATE INDEX idx_communities_brand ON communities(brand_name);
`

### 5.2.2 Community Memberships

`sql
-- File: migrations/005_create_community_memberships.sql

CREATE TYPE membership_role AS ENUM (
    'member',
    'moderator',
    'admin',
    'owner'
);

CREATE TABLE community_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    community_id UUID NOT NULL REFERENCES communities(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    role membership_role DEFAULT 'member',
    
    -- Preferences
    notifications_enabled BOOLEAN DEFAULT TRUE,
    is_favorite BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_approved BOOLEAN DEFAULT TRUE,
    is_banned BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(community_id, user_id)
);

CREATE INDEX idx_memberships_user ON community_memberships(user_id);
CREATE INDEX idx_memberships_community ON community_memberships(community_id);
`

### 5.2.3 Community Posts

`sql
-- File: migrations/006_create_community_posts.sql

CREATE TYPE post_type AS ENUM (
    'discussion',   -- General discussion
    'question',     -- Q&A
    'help_request', -- Help needed
    'help_offer',   -- Offering help
    'ride_invite',  -- Ride invitation
    'event',        -- Event announcement
    'photo',        -- Photo share
    'route_share'   -- Route sharing
);

CREATE TABLE community_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    community_id UUID NOT NULL REFERENCES communities(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Content
    type post_type DEFAULT 'discussion',
    title VARCHAR(200),
    content TEXT NOT NULL,
    
    -- Media
    image_urls TEXT[], -- Array of image URLs
    
    -- For route shares
    route_id UUID,
    
    -- For location-based posts
    location_lat FLOAT,
    location_lng FLOAT,
    location_name VARCHAR(200),
    
    -- Stats
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    
    -- Status
    is_pinned BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_posts_community ON community_posts(community_id);
CREATE INDEX idx_posts_author ON community_posts(author_id);
CREATE INDEX idx_posts_type ON community_posts(type);
CREATE INDEX idx_posts_created ON community_posts(created_at DESC);
`

### 5.2.4 Comments

`sql
-- File: migrations/007_create_comments.sql

CREATE TABLE post_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES community_posts(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES post_comments(id) ON DELETE CASCADE,
    
    content TEXT NOT NULL,
    
    like_count INTEGER DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_comments_post ON post_comments(post_id);
CREATE INDEX idx_comments_parent ON post_comments(parent_id);
`

---

## 5.3 Implementation Tasks

### TASK 5.3.1: Create Community Service
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 4 hours
- [ ] **Dependencies:** Module 3

**Files to Create:**
- api/services/community.py
- api/models/community.py

---

### TASK 5.3.2: Create Community API Endpoints
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 4 hours
- [ ] **Dependencies:** TASK 5.3.1

**Files to Create:**
- api/routes/communities.py
- api/routes/posts.py

---

### TASK 5.3.3: Seed Default Communities
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 1 hour
- [ ] **Dependencies:** TASK 5.3.1

**Default Communities to Create:**

`python
DEFAULT_COMMUNITIES = [
    # Brand Communities
    {"name": "Harley-Davidson Türkiye", "slug": "harley-davidson-tr", "type": "brand", "brand_name": "Harley-Davidson", "icon": "🦅"},
    {"name": "Honda Riders Turkey", "slug": "honda-tr", "type": "brand", "brand_name": "Honda", "icon": "🔴"},
    {"name": "Yamaha Türkiye", "slug": "yamaha-tr", "type": "brand", "brand_name": "Yamaha", "icon": "🔵"},
    {"name": "Kawasaki Türkiye", "slug": "kawasaki-tr", "type": "brand", "brand_name": "Kawasaki", "icon": "💚"},
    {"name": "BMW Motorrad Türkiye", "slug": "bmw-tr", "type": "brand", "brand_name": "BMW", "icon": "🔷"},
    {"name": "Ducati Türkiye", "slug": "ducati-tr", "type": "brand", "brand_name": "Ducati", "icon": "❤️"},
    {"name": "KTM Türkiye", "slug": "ktm-tr", "type": "brand", "brand_name": "KTM", "icon": "🧡"},
    {"name": "Triumph Türkiye", "slug": "triumph-tr", "type": "brand", "brand_name": "Triumph", "icon": "🇬🇧"},
    {"name": "Suzuki Türkiye", "slug": "suzuki-tr", "type": "brand", "brand_name": "Suzuki", "icon": "💙"},
    
    # Style Communities  
    {"name": "Sport Bike Türkiye", "slug": "sport-tr", "type": "style", "icon": "🏍️"},
    {"name": "Touring Türkiye", "slug": "touring-tr", "type": "style", "icon": "🛣️"},
    {"name": "Adventure Riders TR", "slug": "adventure-tr", "type": "style", "icon": "🏔️"},
    {"name": "Cafe Racer Türkiye", "slug": "cafe-racer-tr", "type": "style", "icon": "☕"},
    {"name": "Chopper & Cruiser TR", "slug": "cruiser-tr", "type": "style", "icon": "🌴"},
    
    # Regional Communities
    {"name": "İstanbul Motorcuları", "slug": "istanbul", "type": "region", "region_city": "Istanbul", "icon": "🌉"},
    {"name": "Ankara Motorcuları", "slug": "ankara", "type": "region", "region_city": "Ankara", "icon": "🏛️"},
    {"name": "İzmir Motorcuları", "slug": "izmir", "type": "region", "region_city": "Izmir", "icon": "🌊"},
    {"name": "Antalya Motorcuları", "slug": "antalya", "type": "region", "region_city": "Antalya", "icon": "🏖️"},
    
    # Interest Communities
    {"name": "Track Day Türkiye", "slug": "track-day-tr", "type": "interest", "icon": "🏁"},
    {"name": "Motosiklet Tamircileri", "slug": "tamirciler", "type": "interest", "icon": "🔧"},
    {"name": "Yeni Başlayanlar", "slug": "yeni-baslayanlar", "type": "interest", "icon": "🌱"},
]
`

---

### TASK 5.3.4: Mobile Communities List Screen
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** TASK 5.3.2

**Files to Create:**
- app/mobile/app/communities/index.tsx

---

### TASK 5.3.5: Mobile Community Detail Screen
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 4 hours
- [ ] **Dependencies:** TASK 5.3.4

**Files to Create:**
- app/mobile/app/communities/[slug].tsx

---

### TASK 5.3.6: Mobile Post Creation Screen
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2.5 hours
- [ ] **Dependencies:** TASK 5.3.5

**Files to Create:**
- app/mobile/app/communities/create-post.tsx

---

### TASK 5.3.7: Real-time Chat with WebSockets
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 6 hours
- [ ] **Dependencies:** TASK 5.3.2

**Files to Create:**
- api/websocket/chat.py
- app/mobile/hooks/useChat.ts
- app/mobile/components/ChatMessage.tsx

---


---

# MODULE 6: ROAD REPORTS & WARNINGS
# ==================================

## 6.1 Overview

Crowdsourced road reports and warnings system allowing users to submit,
view, and interact with road condition reports on the map.

## 6.2 Report Types

`
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ROAD REPORT TYPES                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ⚠️ HAZARD REPORTS                                                          │
│  ├── 🛢️ Oil Spill (Yağ Döküntüsü)                                          │
│  ├── 🪨 Debris/Rocks (Döküntü/Taş)                                          │
│  ├── 🕳️ Pothole (Çukur)                                                    │
│  ├── 🚧 Construction (İnşaat)                                               │
│  ├── 🚦 Traffic Light Issue (Işık Arızası)                                  │
│  └── ⚡ Electrical Hazard (Elektrik Tehlikesi)                              │
│                                                                              │
│  🌊 SURFACE CONDITIONS                                                       │
│  ├── 💧 Wet/Slippery (Islak/Kaygan)                                         │
│  ├── ❄️ Ice/Frost (Buz/Don)                                                 │
│  ├── 🌫️ Fog (Sis)                                                          │
│  ├── 🏜️ Sand/Gravel (Kum/Çakıl)                                            │
│  └── 🍂 Leaves (Yaprak)                                                     │
│                                                                              │
│  🚗 TRAFFIC CONDITIONS                                                       │
│  ├── 🚙 Heavy Traffic (Yoğun Trafik)                                        │
│  ├── 🚨 Accident (Kaza)                                                     │
│  ├── 👮 Police Checkpoint (Polis Kontrolü)                                  │
│  └── 🛑 Road Closure (Yol Kapalı)                                           │
│                                                                              │
│  📍 POINTS OF INTEREST                                                       │
│  ├── ⛽ Gas Station (Benzinlik)                                             │
│  ├── 🔧 Motorcycle Shop (Motosiklet Dükkanı)                                │
│  ├── 🅿️ Parking (Park Yeri)                                                │
│  ├── 📸 Scenic View (Manzara)                                               │
│  └── ☕ Rider-Friendly Cafe (Motorcu Kafesi)                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
`

## 6.3 Database Schema

`sql
-- File: migrations/008_create_road_reports.sql

CREATE TYPE report_category AS ENUM (
    'hazard',
    'surface',
    'traffic',
    'poi'
);

CREATE TYPE report_type AS ENUM (
    -- Hazards
    'oil_spill', 'debris', 'pothole', 'construction', 
    'traffic_light', 'electrical',
    -- Surface
    'wet', 'ice', 'fog', 'sand', 'leaves',
    -- Traffic
    'heavy_traffic', 'accident', 'police', 'road_closure',
    -- POI
    'gas_station', 'moto_shop', 'parking', 'scenic', 'cafe'
);

CREATE TYPE report_severity AS ENUM (
    'low',      -- Informational
    'medium',   -- Caution advised
    'high',     -- Dangerous
    'critical'  -- Avoid if possible
);

CREATE TABLE road_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reporter
    reporter_id UUID REFERENCES users(id) ON DELETE SET NULL,
    reporter_anonymous BOOLEAN DEFAULT FALSE,
    
    -- Location
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    location_name VARCHAR(200),
    road_name VARCHAR(200),
    
    -- Report details
    category report_category NOT NULL,
    type report_type NOT NULL,
    severity report_severity DEFAULT 'medium',
    
    -- Content
    title VARCHAR(200),
    description TEXT,
    
    -- Media
    photo_urls TEXT[],
    
    -- Direction (which way the hazard affects)
    affects_direction VARCHAR(20), -- 'both', 'north', 'south', 'east', 'west'
    
    -- Verification
    upvote_count INTEGER DEFAULT 0,
    downvote_count INTEGER DEFAULT 0,
    verification_score FLOAT DEFAULT 0, -- Calculated from votes
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id),
    
    -- Expiration (auto-expire certain types)
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Geospatial index
    CONSTRAINT valid_coordinates CHECK (
        latitude BETWEEN -90 AND 90 AND
        longitude BETWEEN -180 AND 180
    )
);

-- Spatial index for location queries
CREATE INDEX idx_reports_location ON road_reports 
    USING gist (point(longitude, latitude));
CREATE INDEX idx_reports_category ON road_reports(category);
CREATE INDEX idx_reports_type ON road_reports(type);
CREATE INDEX idx_reports_active ON road_reports(is_active);
CREATE INDEX idx_reports_expires ON road_reports(expires_at);

-- Report votes
CREATE TABLE report_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES road_reports(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    is_upvote BOOLEAN NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(report_id, user_id)
);

CREATE INDEX idx_votes_report ON report_votes(report_id);
CREATE INDEX idx_votes_user ON report_votes(user_id);

-- Report comments
CREATE TABLE report_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES road_reports(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    content TEXT NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_report_comments ON report_comments(report_id);
`

---

## 6.4 Implementation Tasks

### TASK 6.4.1: Create Road Report Service
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 3.5 hours
- [ ] **Dependencies:** Module 3

**Files to Create:**
- api/services/road_reports.py
- api/models/road_report.py

**Implementation:**

`python
# File: api/services/road_reports.py

"""
Road reports and warnings service.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from uuid import UUID
from math import radians, sin, cos, sqrt, atan2

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.road_report import (
    RoadReport, ReportVote, ReportComment,
    ReportCategory, ReportType, ReportSeverity
)

# Auto-expiration times by report type (in hours)
EXPIRATION_HOURS = {
    # Hazards - shorter duration
    "oil_spill": 24,
    "debris": 12,
    "pothole": 168,  # 1 week
    "construction": 720,  # 30 days
    "traffic_light": 48,
    "electrical": 24,
    # Surface - weather dependent
    "wet": 6,
    "ice": 12,
    "fog": 4,
    "sand": 24,
    "leaves": 24,
    # Traffic - very short
    "heavy_traffic": 2,
    "accident": 4,
    "police": 2,
    "road_closure": 48,
    # POI - long duration
    "gas_station": None,  # No expiration
    "moto_shop": None,
    "parking": None,
    "scenic": None,
    "cafe": None,
}


class RoadReportService:
    """
    Service for managing road reports and warnings.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_report(
        self,
        reporter_id: UUID,
        latitude: float,
        longitude: float,
        category: ReportCategory,
        report_type: ReportType,
        title: Optional[str] = None,
        description: Optional[str] = None,
        severity: ReportSeverity = ReportSeverity.MEDIUM,
        photo_urls: Optional[List[str]] = None,
        location_name: Optional[str] = None,
        road_name: Optional[str] = None,
        affects_direction: str = "both",
        anonymous: bool = False,
    ) -> RoadReport:
        """Create a new road report."""
        
        # Calculate expiration
        exp_hours = EXPIRATION_HOURS.get(report_type.value)
        expires_at = None
        if exp_hours:
            expires_at = datetime.utcnow() + timedelta(hours=exp_hours)
        
        report = RoadReport(
            reporter_id=reporter_id if not anonymous else None,
            reporter_anonymous=anonymous,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            road_name=road_name,
            category=category,
            type=report_type,
            severity=severity,
            title=title,
            description=description,
            photo_urls=photo_urls or [],
            affects_direction=affects_direction,
            expires_at=expires_at,
        )
        
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        
        return report
    
    async def get_reports_in_area(
        self,
        center_lat: float,
        center_lng: float,
        radius_km: float = 10.0,
        categories: Optional[List[ReportCategory]] = None,
        active_only: bool = True,
        limit: int = 100,
    ) -> List[RoadReport]:
        """
        Get reports within a radius of a point.
        
        Uses Haversine formula for distance calculation.
        """
        # Approximate bounding box for initial filter
        lat_delta = radius_km / 111.0  # ~111km per degree latitude
        lng_delta = radius_km / (111.0 * cos(radians(center_lat)))
        
        query = select(RoadReport).where(
            and_(
                RoadReport.latitude.between(
                    center_lat - lat_delta,
                    center_lat + lat_delta
                ),
                RoadReport.longitude.between(
                    center_lng - lng_delta,
                    center_lng + lng_delta
                ),
            )
        )
        
        if active_only:
            query = query.where(
                and_(
                    RoadReport.is_active == True,
                    RoadReport.is_resolved == False,
                    or_(
                        RoadReport.expires_at.is_(None),
                        RoadReport.expires_at > datetime.utcnow()
                    )
                )
            )
        
        if categories:
            query = query.where(RoadReport.category.in_(categories))
        
        query = query.order_by(RoadReport.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        reports = result.scalars().all()
        
        # Filter by actual distance
        filtered = []
        for report in reports:
            dist = self._haversine_distance(
                center_lat, center_lng,
                report.latitude, report.longitude
            )
            if dist <= radius_km:
                filtered.append(report)
        
        return filtered
    
    async def get_reports_along_route(
        self,
        route_coords: List[Tuple[float, float]],
        buffer_km: float = 0.5,
        active_only: bool = True,
    ) -> List[RoadReport]:
        """
        Get reports along a route with a buffer distance.
        """
        if not route_coords:
            return []
        
        # Get bounding box of route
        lats = [c[0] for c in route_coords]
        lngs = [c[1] for c in route_coords]
        
        min_lat, max_lat = min(lats) - buffer_km/111, max(lats) + buffer_km/111
        min_lng, max_lng = min(lngs) - buffer_km/111, max(lngs) + buffer_km/111
        
        query = select(RoadReport).where(
            and_(
                RoadReport.latitude.between(min_lat, max_lat),
                RoadReport.longitude.between(min_lng, max_lng),
            )
        )
        
        if active_only:
            query = query.where(
                and_(
                    RoadReport.is_active == True,
                    RoadReport.is_resolved == False,
                    or_(
                        RoadReport.expires_at.is_(None),
                        RoadReport.expires_at > datetime.utcnow()
                    )
                )
            )
        
        result = await self.db.execute(query)
        reports = result.scalars().all()
        
        # Filter by distance to route
        filtered = []
        for report in reports:
            min_dist = min(
                self._haversine_distance(
                    coord[0], coord[1],
                    report.latitude, report.longitude
                )
                for coord in route_coords[::10]  # Sample every 10th point
            )
            if min_dist <= buffer_km:
                filtered.append(report)
        
        return filtered
    
    async def vote_report(
        self,
        report_id: UUID,
        user_id: UUID,
        is_upvote: bool,
    ) -> RoadReport:
        """Vote on a report (upvote = still there, downvote = gone)."""
        # Check existing vote
        result = await self.db.execute(
            select(ReportVote).where(
                and_(
                    ReportVote.report_id == report_id,
                    ReportVote.user_id == user_id
                )
            )
        )
        existing_vote = result.scalar_one_or_none()
        
        report = await self.get_report(report_id)
        if not report:
            raise ValueError("Report not found")
        
        if existing_vote:
            # Update existing vote
            if existing_vote.is_upvote != is_upvote:
                if is_upvote:
                    report.upvote_count += 1
                    report.downvote_count -= 1
                else:
                    report.upvote_count -= 1
                    report.downvote_count += 1
                existing_vote.is_upvote = is_upvote
        else:
            # New vote
            vote = ReportVote(
                report_id=report_id,
                user_id=user_id,
                is_upvote=is_upvote,
            )
            self.db.add(vote)
            
            if is_upvote:
                report.upvote_count += 1
            else:
                report.downvote_count += 1
        
        # Update verification score
        total_votes = report.upvote_count + report.downvote_count
        if total_votes > 0:
            report.verification_score = report.upvote_count / total_votes
            
            # Auto-verify if high score
            if report.verification_score >= 0.8 and total_votes >= 5:
                report.is_verified = True
            
            # Auto-resolve if too many downvotes
            if report.verification_score < 0.3 and total_votes >= 3:
                report.is_resolved = True
                report.resolved_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(report)
        
        return report
    
    async def resolve_report(
        self,
        report_id: UUID,
        resolved_by: UUID,
    ) -> RoadReport:
        """Mark a report as resolved."""
        report = await self.get_report(report_id)
        if not report:
            raise ValueError("Report not found")
        
        report.is_resolved = True
        report.resolved_at = datetime.utcnow()
        report.resolved_by = resolved_by
        
        await self.db.commit()
        await self.db.refresh(report)
        
        return report
    
    async def get_report(self, report_id: UUID) -> Optional[RoadReport]:
        """Get a single report."""
        result = await self.db.execute(
            select(RoadReport).where(RoadReport.id == report_id)
        )
        return result.scalar_one_or_none()
    
    async def cleanup_expired(self) -> int:
        """Clean up expired reports. Run periodically."""
        result = await self.db.execute(
            select(RoadReport).where(
                and_(
                    RoadReport.is_active == True,
                    RoadReport.expires_at.isnot(None),
                    RoadReport.expires_at < datetime.utcnow()
                )
            )
        )
        expired = result.scalars().all()
        
        count = 0
        for report in expired:
            report.is_active = False
            count += 1
        
        await self.db.commit()
        return count
    
    @staticmethod
    def _haversine_distance(
        lat1: float, lng1: float,
        lat2: float, lng2: float
    ) -> float:
        """Calculate distance between two points in km."""
        R = 6371  # Earth's radius in km
        
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
`

---

### TASK 6.4.2: Create Road Reports API Endpoints
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2.5 hours
- [ ] **Dependencies:** TASK 6.4.1

**Files to Create:**
- api/routes/road_reports.py

---

### TASK 6.4.3: Mobile Report Markers Component
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2.5 hours
- [ ] **Dependencies:** TASK 6.4.2

**Files to Create:**
- app/mobile/components/ReportMarker.tsx
- app/mobile/components/ReportSheet.tsx

**Implementation:**

`	sx
// File: app/mobile/components/ReportMarker.tsx

import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { Marker, Callout } from "react-native-maps";
import { colors, typography, spacing, radius } from "../theme";

export type ReportType = 
  | "oil_spill" | "debris" | "pothole" | "construction"
  | "wet" | "ice" | "fog" | "sand"
  | "heavy_traffic" | "accident" | "police" | "road_closure"
  | "gas_station" | "moto_shop" | "parking" | "scenic" | "cafe";

type RoadReport = {
  id: string;
  latitude: number;
  longitude: number;
  type: ReportType;
  title?: string;
  description?: string;
  severity: "low" | "medium" | "high" | "critical";
  upvote_count: number;
  downvote_count: number;
  is_verified: boolean;
  created_at: string;
};

const REPORT_ICONS: Record<ReportType, string> = {
  oil_spill: "🛢️",
  debris: "🪨",
  pothole: "🕳️",
  construction: "🚧",
  wet: "💧",
  ice: "❄️",
  fog: "🌫️",
  sand: "🏜️",
  heavy_traffic: "🚙",
  accident: "🚨",
  police: "👮",
  road_closure: "🛑",
  gas_station: "⛽",
  moto_shop: "🔧",
  parking: "🅿️",
  scenic: "📸",
  cafe: "☕",
};

const SEVERITY_COLORS = {
  low: colors.info,
  medium: colors.warning,
  high: "#F97316",
  critical: colors.danger,
};

type ReportMarkerProps = {
  report: RoadReport;
  onPress?: (report: RoadReport) => void;
};

export function ReportMarker({ report, onPress }: ReportMarkerProps) {
  const icon = REPORT_ICONS[report.type] || "⚠️";
  const bgColor = SEVERITY_COLORS[report.severity];
  
  return (
    <Marker
      coordinate={{
        latitude: report.latitude,
        longitude: report.longitude,
      }}
      onPress={() => onPress?.(report)}
    >
      <View style={[styles.markerContainer, { backgroundColor: bgColor }]}>
        <Text style={styles.markerIcon}>{icon}</Text>
        {report.is_verified && (
          <View style={styles.verifiedBadge}>
            <Text style={styles.verifiedText}>✓</Text>
          </View>
        )}
      </View>
      
      <Callout tooltip>
        <View style={styles.callout}>
          <Text style={styles.calloutTitle}>
            {icon} {report.title || translateType(report.type)}
          </Text>
          {report.description && (
            <Text style={styles.calloutDescription} numberOfLines={2}>
              {report.description}
            </Text>
          )}
          <View style={styles.calloutStats}>
            <Text style={styles.statText}>👍 {report.upvote_count}</Text>
            <Text style={styles.statText}>👎 {report.downvote_count}</Text>
            <Text style={styles.timeText}>
              {formatTimeAgo(report.created_at)}
            </Text>
          </View>
        </View>
      </Callout>
    </Marker>
  );
}

function translateType(type: ReportType): string {
  const translations: Record<ReportType, string> = {
    oil_spill: "Yağ Döküntüsü",
    debris: "Döküntü/Taş",
    pothole: "Çukur",
    construction: "İnşaat",
    wet: "Islak Yol",
    ice: "Buzlanma",
    fog: "Sis",
    sand: "Kum/Çakıl",
    heavy_traffic: "Yoğun Trafik",
    accident: "Kaza",
    police: "Polis Kontrolü",
    road_closure: "Yol Kapalı",
    gas_station: "Benzinlik",
    moto_shop: "Motosiklet Dükkanı",
    parking: "Park Yeri",
    scenic: "Manzara",
    cafe: "Motorcu Kafesi",
  };
  return translations[type] || type;
}

function formatTimeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 60) return \dk önce;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return \s önce;
  const diffDays = Math.floor(diffHours / 24);
  return \g önce;
}

const styles = StyleSheet.create({
  markerContainer: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: "center",
    alignItems: "center",
    borderWidth: 2,
    borderColor: "white",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  markerIcon: {
    fontSize: 18,
  },
  verifiedBadge: {
    position: "absolute",
    top: -4,
    right: -4,
    width: 14,
    height: 14,
    borderRadius: 7,
    backgroundColor: colors.success,
    justifyContent: "center",
    alignItems: "center",
  },
  verifiedText: {
    fontSize: 8,
    color: "white",
    fontWeight: "bold",
  },
  callout: {
    backgroundColor: colors.bgSecondary,
    borderRadius: radius.md,
    padding: spacing.md,
    minWidth: 200,
    maxWidth: 280,
  },
  calloutTitle: {
    ...typography.bodyBold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  calloutDescription: {
    ...typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  calloutStats: {
    flexDirection: "row",
    alignItems: "center",
  },
  statText: {
    ...typography.caption,
    color: colors.textSecondary,
    marginRight: spacing.md,
  },
  timeText: {
    ...typography.caption,
    color: colors.textTertiary,
    marginLeft: "auto",
  },
});

export default ReportMarker;
`

---

### TASK 6.4.4: Mobile Report Creation Screen
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** TASK 6.4.2

**Files to Create:**
- app/mobile/app/report/create.tsx

---

### TASK 6.4.5: Integrate Reports with Map Screen
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** TASK 6.4.3

**Files to Modify:**
- app/mobile/app/(tabs)/map.tsx

**Key Changes:**
1. Add toggle for report markers visibility
2. Fetch reports in current map region
3. Display report markers on map
4. Add floating action button for quick report
5. Show reports along calculated route

---

# MODULE 7: GAMIFICATION SYSTEM
# ==============================

## 7.1 Overview

Complete gamification system with points, badges, achievements,
leaderboards, and challenges to encourage engagement.

## 7.2 Gamification Elements

`
┌─────────────────────────────────────────────────────────────────────────────┐
│                          GAMIFICATION ELEMENTS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  🎯 POINTS SYSTEM                                                            │
│  ├── Route completed: 10 pts                                                │
│  ├── Road report submitted: 5 pts                                           │
│  ├── Report verified (by community): 10 pts                                 │
│  ├── Helpful report (5+ upvotes): 15 pts                                    │
│  ├── Community post: 3 pts                                                  │
│  ├── Helping another rider: 25 pts                                          │
│  └── Daily streak bonus: 5 pts × days                                       │
│                                                                              │
│  🏆 BADGES                                                                   │
│  ├── 🌟 Yeni Sürücü (New Rider) - First route                              │
│  ├── 🗺️ Kaşif (Explorer) - 10 unique routes                                │
│  ├── 🏔️ Dağcı (Mountain Climber) - 1000m elevation                         │
│  ├── 🌙 Gece Kuşu (Night Owl) - 10 night rides                              │
│  ├── 🦅 Özgür Ruh (Free Spirit) - 500km in one week                         │
│  ├── ⚠️ Koruyucu (Guardian) - 50 road reports                               │
│  ├── 💬 Sosyal (Social) - 100 community posts                               │
│  ├── 🤝 Yardımsever (Helpful) - Help 10 riders                              │
│  ├── 🏁 Viraj Ustası (Corner Master) - 100 curvy routes                     │
│  └── 👑 Efsane (Legend) - 10,000 total km                                   │
│                                                                              │
│  📊 LEVELS                                                                   │
│  ├── Lv.1  Çaylak (Rookie): 0-100 pts                                       │
│  ├── Lv.2  Amatör (Amateur): 100-500 pts                                    │
│  ├── Lv.3  Deneyimli (Experienced): 500-1500 pts                            │
│  ├── Lv.4  Uzman (Expert): 1500-5000 pts                                    │
│  ├── Lv.5  Usta (Master): 5000-15000 pts                                    │
│  └── Lv.6  Efsane (Legend): 15000+ pts                                      │
│                                                                              │
│  🎮 CHALLENGES                                                               │
│  ├── Daily: Complete a route, Submit a report                               │
│  ├── Weekly: 100km total, Visit 3 new roads                                 │
│  └── Monthly: Join a community ride, Earn a badge                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
`

## 7.3 Database Schema

`sql
-- File: migrations/009_create_gamification.sql

-- User points and level
CREATE TABLE user_points (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    total_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    current_streak_days INTEGER DEFAULT 0,
    longest_streak_days INTEGER DEFAULT 0,
    last_activity_date DATE,
    
    -- Category breakdowns
    points_routes INTEGER DEFAULT 0,
    points_reports INTEGER DEFAULT 0,
    points_community INTEGER DEFAULT 0,
    points_helping INTEGER DEFAULT 0,
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Point transactions (audit log)
CREATE TABLE point_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    points INTEGER NOT NULL,
    reason VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    
    -- Reference to source
    reference_type VARCHAR(50), -- 'route', 'report', 'post', 'help'
    reference_id UUID,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_transactions_user ON point_transactions(user_id);
CREATE INDEX idx_transactions_date ON point_transactions(created_at);

-- Badges
CREATE TABLE badges (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    name_tr VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    description_tr TEXT NOT NULL,
    icon VARCHAR(10) NOT NULL,
    category VARCHAR(50) NOT NULL,
    requirement_type VARCHAR(50) NOT NULL,
    requirement_value INTEGER NOT NULL,
    points_reward INTEGER DEFAULT 0,
    is_secret BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User badges (earned)
CREATE TABLE user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_id VARCHAR(50) NOT NULL REFERENCES badges(id),
    
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, badge_id)
);

CREATE INDEX idx_user_badges_user ON user_badges(user_id);

-- Challenges
CREATE TABLE challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    title VARCHAR(100) NOT NULL,
    title_tr VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    description_tr TEXT NOT NULL,
    
    type VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly', 'special'
    category VARCHAR(50) NOT NULL,
    
    requirement_type VARCHAR(50) NOT NULL,
    requirement_value INTEGER NOT NULL,
    
    points_reward INTEGER NOT NULL,
    badge_reward VARCHAR(50) REFERENCES badges(id),
    
    starts_at TIMESTAMP WITH TIME ZONE,
    ends_at TIMESTAMP WITH TIME ZONE,
    
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User challenge progress
CREATE TABLE user_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    challenge_id UUID NOT NULL REFERENCES challenges(id),
    
    progress INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, challenge_id)
);

CREATE INDEX idx_user_challenges_user ON user_challenges(user_id);

-- Leaderboard cache (refreshed periodically)
CREATE TABLE leaderboard_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    period VARCHAR(20) NOT NULL, -- 'all_time', 'monthly', 'weekly'
    category VARCHAR(50) NOT NULL, -- 'total', 'routes', 'reports', 'community'
    
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    points INTEGER NOT NULL,
    
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(period, category, user_id)
);

CREATE INDEX idx_leaderboard_period ON leaderboard_cache(period, category, rank);
`

---

## 7.4 Implementation Tasks

### TASK 7.4.1: Create Gamification Service
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 4 hours
- [ ] **Dependencies:** Module 3

**Files to Create:**
- api/services/gamification.py
- api/models/gamification.py

---

### TASK 7.4.2: Seed Badges
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 1 hour
- [ ] **Dependencies:** TASK 7.4.1

**Default Badges:**

`python
BADGES = [
    # Riding badges
    {"id": "first_route", "name": "New Rider", "name_tr": "Yeni Sürücü", "icon": "🌟", "category": "riding", "requirement_type": "routes_completed", "requirement_value": 1},
    {"id": "explorer_10", "name": "Explorer", "name_tr": "Kaşif", "icon": "🗺️", "category": "riding", "requirement_type": "unique_routes", "requirement_value": 10},
    {"id": "explorer_50", "name": "Great Explorer", "name_tr": "Büyük Kaşif", "icon": "🧭", "category": "riding", "requirement_type": "unique_routes", "requirement_value": 50},
    {"id": "mountain_1000", "name": "Mountain Climber", "name_tr": "Dağcı", "icon": "🏔️", "category": "riding", "requirement_type": "total_elevation_m", "requirement_value": 1000},
    {"id": "night_10", "name": "Night Owl", "name_tr": "Gece Kuşu", "icon": "🌙", "category": "riding", "requirement_type": "night_rides", "requirement_value": 10},
    {"id": "week_500km", "name": "Free Spirit", "name_tr": "Özgür Ruh", "icon": "🦅", "category": "riding", "requirement_type": "km_in_week", "requirement_value": 500},
    {"id": "curves_100", "name": "Corner Master", "name_tr": "Viraj Ustası", "icon": "🏁", "category": "riding", "requirement_type": "curvy_routes", "requirement_value": 100},
    {"id": "km_1000", "name": "Road Warrior", "name_tr": "Yol Savaşçısı", "icon": "⚔️", "category": "riding", "requirement_type": "total_km", "requirement_value": 1000},
    {"id": "km_10000", "name": "Legend", "name_tr": "Efsane", "icon": "👑", "category": "riding", "requirement_type": "total_km", "requirement_value": 10000},
    
    # Report badges
    {"id": "first_report", "name": "Watchful Eye", "name_tr": "Dikkatli Göz", "icon": "👁️", "category": "reports", "requirement_type": "reports_submitted", "requirement_value": 1},
    {"id": "guardian_50", "name": "Guardian", "name_tr": "Koruyucu", "icon": "⚠️", "category": "reports", "requirement_type": "reports_submitted", "requirement_value": 50},
    {"id": "verified_10", "name": "Trusted Reporter", "name_tr": "Güvenilir Muhabir", "icon": "✅", "category": "reports", "requirement_type": "reports_verified", "requirement_value": 10},
    
    # Community badges
    {"id": "social_100", "name": "Social Butterfly", "name_tr": "Sosyal Kelebek", "icon": "💬", "category": "community", "requirement_type": "posts_created", "requirement_value": 100},
    {"id": "helpful_10", "name": "Helpful Rider", "name_tr": "Yardımsever", "icon": "🤝", "category": "community", "requirement_type": "help_given", "requirement_value": 10},
    
    # Streak badges
    {"id": "streak_7", "name": "Consistent", "name_tr": "Tutarlı", "icon": "🔥", "category": "streak", "requirement_type": "streak_days", "requirement_value": 7},
    {"id": "streak_30", "name": "Dedicated", "name_tr": "Adanmış", "icon": "💪", "category": "streak", "requirement_type": "streak_days", "requirement_value": 30},
]
`

---

### TASK 7.4.3: Create Gamification API Endpoints
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2.5 hours
- [ ] **Dependencies:** TASK 7.4.1

**Files to Create:**
- api/routes/gamification.py

---

### TASK 7.4.4: Mobile Achievements Screen
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 3.5 hours
- [ ] **Dependencies:** TASK 7.4.3

**Files to Create:**
- app/mobile/app/achievements/index.tsx
- app/mobile/components/BadgeCard.tsx
- app/mobile/components/ProgressBar.tsx

---

### TASK 7.4.5: Mobile Leaderboard Screen
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 2.5 hours
- [ ] **Dependencies:** TASK 7.4.3

**Files to Create:**
- app/mobile/app/leaderboard/index.tsx

---

### TASK 7.4.6: Points Award Integration
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** TASK 7.4.1

**Description:**
Integrate points awarding into all relevant actions:
- Route completion
- Report submission
- Report verification
- Community posts
- Helping riders

---


---

# MODULE 8: BACKEND API EXTENSIONS
# =================================

## 8.1 Overview

Additional backend API improvements including rate limiting, caching,
monitoring, and extended route functionality.

## 8.2 Implementation Tasks

### TASK 8.2.1: Setup Redis Caching Layer
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** None

**Files to Create:**
- api/core/cache.py

---

### TASK 8.2.2: Implement Rate Limiting
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** TASK 8.2.1

**Files to Create:**
- api/middleware/rate_limit.py

---

### TASK 8.2.3: Add Request Logging & Monitoring
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** None

**Files to Create:**
- api/middleware/logging.py
- api/core/metrics.py

---

### TASK 8.2.4: Dynamic Route Generation API
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 4 hours
- [ ] **Dependencies:** Module 1

**Description:**
Create API endpoint for on-demand route generation with custom
origin/destination instead of pre-generated routes.

**Files to Create:**
- api/routes/routing.py

---

### TASK 8.2.5: Route History & Analytics
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** Module 3

**Files to Create:**
- api/services/route_history.py
- api/routes/history.py

---

### TASK 8.2.6: Push Notifications Service
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** Module 3

**Files to Create:**
- api/services/notifications.py
- api/routes/notifications.py

---

### TASK 8.2.7: File Upload Service (S3/CloudStorage)
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 2.5 hours
- [ ] **Dependencies:** None

**Files to Create:**
- api/services/storage.py
- api/routes/upload.py

---

# MODULE 9: MOBILE APP SCREENS
# =============================

## 9.1 Overview

Complete list of all mobile app screens and components to be
implemented or enhanced.

## 9.2 Screen Inventory

### 9.2.1 Authentication Screens
- [ ] **TASK 9.2.1.1:** Login Screen - app/mobile/app/auth/login.tsx
- [ ] **TASK 9.2.1.2:** Register Screen - app/mobile/app/auth/register.tsx
- [ ] **TASK 9.2.1.3:** Forgot Password Screen - app/mobile/app/auth/forgot-password.tsx
- [ ] **TASK 9.2.1.4:** Reset Password Screen - app/mobile/app/auth/reset-password.tsx

### 9.2.2 Tab Screens (Main Navigation)
- [ ] **TASK 9.2.2.1:** Dashboard (Home) - app/mobile/app/(tabs)/index.tsx
- [ ] **TASK 9.2.2.2:** Map Screen - app/mobile/app/(tabs)/map.tsx
- [ ] **TASK 9.2.2.3:** Garage Screen - app/mobile/app/(tabs)/garage.tsx
- [ ] **TASK 9.2.2.4:** Communities Screen - app/mobile/app/(tabs)/communities.tsx
- [ ] **TASK 9.2.2.5:** Profile Screen - app/mobile/app/(tabs)/profile.tsx

### 9.2.3 Route Screens
- [ ] **TASK 9.2.3.1:** Route Selection - app/mobile/app/route/selection.tsx
- [ ] **TASK 9.2.3.2:** Route Detail - app/mobile/app/route/[id].tsx
- [ ] **TASK 9.2.3.3:** Navigation Mode - app/mobile/app/route/navigation.tsx
- [ ] **TASK 9.2.3.4:** Saved Routes - app/mobile/app/saved-routes.tsx

### 9.2.4 Community Screens
- [ ] **TASK 9.2.4.1:** Community List - app/mobile/app/communities/index.tsx
- [ ] **TASK 9.2.4.2:** Community Detail - app/mobile/app/communities/[slug].tsx
- [ ] **TASK 9.2.4.3:** Create Post - app/mobile/app/communities/create-post.tsx
- [ ] **TASK 9.2.4.4:** Post Detail - app/mobile/app/communities/post/[id].tsx
- [ ] **TASK 9.2.4.5:** Chat Room - app/mobile/app/communities/chat/[id].tsx

### 9.2.5 Gamification Screens
- [ ] **TASK 9.2.5.1:** Achievements - app/mobile/app/achievements/index.tsx
- [ ] **TASK 9.2.5.2:** Leaderboard - app/mobile/app/leaderboard/index.tsx
- [ ] **TASK 9.2.5.3:** Challenges - app/mobile/app/challenges/index.tsx

### 9.2.6 Settings Screens
- [ ] **TASK 9.2.6.1:** Settings Main - app/mobile/app/settings/index.tsx
- [ ] **TASK 9.2.6.2:** Account Settings - app/mobile/app/settings/account.tsx
- [ ] **TASK 9.2.6.3:** Notification Settings - app/mobile/app/settings/notifications.tsx
- [ ] **TASK 9.2.6.4:** Privacy Settings - app/mobile/app/settings/privacy.tsx
- [ ] **TASK 9.2.6.5:** About - app/mobile/app/settings/about.tsx

### 9.2.7 Motorcycle Management
- [ ] **TASK 9.2.7.1:** Motorcycle List - app/mobile/app/garage.tsx
- [ ] **TASK 9.2.7.2:** Add Motorcycle - app/mobile/app/add-motorcycle.tsx
- [ ] **TASK 9.2.7.3:** Edit Motorcycle - app/mobile/app/motorcycle/[id]/edit.tsx
- [ ] **TASK 9.2.7.4:** Motorcycle Stats - app/mobile/app/motorcycle/[id]/stats.tsx

### 9.2.8 Report Screens
- [ ] **TASK 9.2.8.1:** Create Report - app/mobile/app/report/create.tsx
- [ ] **TASK 9.2.8.2:** Report Detail - app/mobile/app/report/[id].tsx
- [ ] **TASK 9.2.8.3:** My Reports - app/mobile/app/my-reports.tsx

---

## 9.3 Component Library

### TASK 9.3.1: Core UI Components
- [ ] GlassCard (existing, enhance)
- [ ] AppButton (existing, enhance)
- [ ] ScreenHeader (existing, enhance)
- [ ] StatCard (existing, enhance)
- [ ] InputField (create)
- [ ] SelectField (create)
- [ ] DatePicker (create)
- [ ] ImagePicker (create)
- [ ] LoadingOverlay (create)
- [ ] EmptyState (create)
- [ ] ErrorBoundary (create)
- [ ] Toast/Snackbar (create)

### TASK 9.3.2: Map Components
- [ ] ColoredRoute (created)
- [ ] ReportMarker (created)
- [ ] UserLocationMarker (create)
- [ ] RouteInfoPanel (create)
- [ ] MapControls (create)
- [ ] MapLegend (create)

### TASK 9.3.3: List Components
- [ ] MotorcycleCard (create)
- [ ] CommunityCard (create)
- [ ] PostCard (create)
- [ ] CommentCard (create)
- [ ] LeaderboardRow (create)
- [ ] BadgeCard (create)
- [ ] ChallengeCard (create)

---

# MODULE 10: TESTING & QUALITY ASSURANCE
# =======================================

## 10.1 Overview

Comprehensive testing strategy covering unit tests, integration tests,
E2E tests, and performance testing.

## 10.2 Implementation Tasks

### TASK 10.2.1: Python Unit Tests Setup
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** None

**Files to Create:**
- tests/conftest.py
- tests/unit/__init__.py
- pytest.ini

---

### TASK 10.2.2: Weather Module Tests
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** Module 1

**Files to Create:**
- tests/unit/weather/test_client.py
- tests/unit/weather/test_assessment.py
- tests/unit/weather/test_cache.py

---

### TASK 10.2.3: Authentication Tests
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2.5 hours
- [ ] **Dependencies:** Module 3

**Files to Create:**
- tests/unit/auth/test_security.py
- tests/unit/auth/test_service.py
- tests/integration/test_auth_flow.py

---

### TASK 10.2.4: API Integration Tests
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 4 hours
- [ ] **Dependencies:** All API modules

**Files to Create:**
- tests/integration/test_routes.py
- tests/integration/test_communities.py
- tests/integration/test_reports.py
- tests/integration/test_gamification.py

---

### TASK 10.2.5: React Native Component Tests
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 4 hours
- [ ] **Dependencies:** Module 9

**Files to Create:**
- app/mobile/__tests__/components/
- app/mobile/__tests__/hooks/
- app/mobile/__tests__/utils/
- jest.config.js

---

### TASK 10.2.6: E2E Tests with Detox
- [ ] **Priority:** LOW
- [ ] **Estimated Effort:** 6 hours
- [ ] **Dependencies:** All mobile screens

**Files to Create:**
- app/mobile/e2e/
- .detoxrc.js

---

### TASK 10.2.7: Performance Testing
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** API modules

**Tools:**
- Locust for API load testing
- React Native Performance Monitor

---

### TASK 10.2.8: Security Audit
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 4 hours
- [ ] **Dependencies:** All modules

**Checks:**
- SQL injection prevention
- XSS protection
- CORS configuration
- Rate limiting effectiveness
- JWT security
- Password hashing strength
- API authentication coverage

---

# MODULE 11: DEVOPS & DEPLOYMENT
# ===============================

## 11.1 Overview

Infrastructure, CI/CD pipelines, and deployment configurations.

## 11.2 Implementation Tasks

### TASK 11.2.1: Docker Configuration
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** None

**Files to Create:**
- Dockerfile (API)
- docker-compose.yml
- docker-compose.prod.yml
- .dockerignore

---

### TASK 11.2.2: GitHub Actions CI Pipeline
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** Testing setup

**Files to Create:**
- .github/workflows/ci.yml
- .github/workflows/deploy.yml

**Pipeline Stages:**
1. Lint (Python + TypeScript)
2. Unit Tests
3. Integration Tests
4. Build Docker Image
5. Push to Registry
6. Deploy to Staging
7. E2E Tests on Staging
8. Deploy to Production (manual approval)

---

### TASK 11.2.3: Kubernetes Manifests
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 4 hours
- [ ] **Dependencies:** Docker config

**Files to Create:**
- k8s/namespace.yaml
- k8s/api-deployment.yaml
- k8s/api-service.yaml
- k8s/ingress.yaml
- k8s/secrets.yaml
- k8s/configmap.yaml
- k8s/redis-deployment.yaml
- k8s/postgres-deployment.yaml

---

### TASK 11.2.4: Environment Configuration
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 1 hour
- [ ] **Dependencies:** None

**Files to Create/Update:**
- .env.example
- .env.development
- .env.staging
- .env.production

---

### TASK 11.2.5: Monitoring & Alerting
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** Deployment

**Setup:**
- Prometheus metrics
- Grafana dashboards
- Error tracking (Sentry)
- Log aggregation (ELK or similar)
- Uptime monitoring

---

### TASK 11.2.6: Database Migrations CI
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** Database setup

**Setup:**
- Alembic for SQLAlchemy migrations
- Migration validation in CI
- Rollback procedures

---

### TASK 11.2.7: Mobile App Build Pipeline
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** None

**Files to Create:**
- .github/workflows/mobile-build.yml
- eas.json

**Pipeline:**
1. TypeScript check
2. ESLint
3. Jest tests
4. EAS Build (Android APK/AAB)
5. Upload to Play Store (beta track)

---

# MODULE 12: DOCUMENTATION
# =========================

## 12.1 Overview

Comprehensive documentation for developers, API consumers, and users.

## 12.2 Implementation Tasks

### TASK 12.2.1: API Documentation (OpenAPI)
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** All API endpoints

**Description:**
FastAPI auto-generates OpenAPI docs. Ensure all endpoints have:
- Detailed descriptions
- Request/response examples
- Error response documentation
- Authentication requirements

---

### TASK 12.2.2: Developer README
- [ ] **Priority:** HIGH
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** None

**Sections:**
- Project overview
- Architecture diagram
- Local development setup
- Environment variables
- Running tests
- Contributing guidelines

---

### TASK 12.2.3: Mobile App README
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 1 hour
- [ ] **Dependencies:** None

**Sections:**
- Expo setup
- Running on device/emulator
- Building for production
- Folder structure
- Component library

---

### TASK 12.2.4: Database Schema Documentation
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 1.5 hours
- [ ] **Dependencies:** All migrations

**Contents:**
- ER diagram
- Table descriptions
- Relationship explanations
- Index documentation

---

### TASK 12.2.5: Algorithm Documentation
- [ ] **Priority:** MEDIUM
- [ ] **Estimated Effort:** 2 hours
- [ ] **Dependencies:** Algorithm modules

**Contents:**
- Routing algorithm explanation
- Lane splitting calculation
- Weather assessment logic
- Safety scoring methodology

---

### TASK 12.2.6: User Guide (Turkish)
- [ ] **Priority:** LOW
- [ ] **Estimated Effort:** 3 hours
- [ ] **Dependencies:** All features

**Contents:**
- App installation
- Account creation
- Using the map
- Submitting reports
- Joining communities
- Understanding badges

---

# IMPLEMENTATION TIMELINE
# =======================

## Phase 1: Foundation (Weeks 1-2)
- [ ] Module 3: User Authentication & Database
- [ ] Module 4: User Profile & Motorcycle Garage
- [ ] TASK 11.2.1: Docker Configuration
- [ ] TASK 11.2.4: Environment Configuration

## Phase 2: Weather & Safety (Weeks 3-4)
- [ ] Module 1: Weather Integration System
- [ ] Module 2: Visual Route Safety Overlay
- [ ] TASK 8.2.4: Dynamic Route Generation API

## Phase 3: Community & Social (Weeks 5-6)
- [ ] Module 5: Community Platform
- [ ] Module 6: Road Reports & Warnings
- [ ] TASK 8.2.6: Push Notifications Service

## Phase 4: Gamification (Week 7)
- [ ] Module 7: Gamification System
- [ ] All badge and achievement integration

## Phase 5: Polish & Testing (Weeks 8-9)
- [ ] Module 9: Complete all mobile screens
- [ ] Module 10: Testing & QA
- [ ] Performance optimization

## Phase 6: Deployment (Week 10)
- [ ] Module 11: DevOps & Deployment
- [ ] Module 12: Documentation
- [ ] Production launch preparation

---

# DEPENDENCY GRAPH
# =================

`
Module 3 (Auth) ─────────────┬──────────────────────────────────────┐
        │                    │                                       │
        ▼                    ▼                                       ▼
Module 4 (Profile)    Module 5 (Community)               Module 7 (Gamification)
        │                    │                                       │
        ▼                    ▼                                       │
Module 1 (Weather) ──► Module 6 (Reports) ◄──────────────────────────┘
        │                    
        ▼                    
Module 2 (Safety Overlay)   
        │
        ▼
Module 9 (Mobile Screens) ──► Module 10 (Testing) ──► Module 11 (Deployment)
                                                              │
                                                              ▼
                                                      Module 12 (Docs)
`

---

# SUMMARY
# =======

## Total Tasks: 150+
## Estimated Total Effort: 200+ hours

## Priority Distribution:
- CRITICAL: 12 tasks
- HIGH: 65 tasks
- MEDIUM: 48 tasks
- LOW: 25+ tasks

## Technology Stack:
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL, Redis
- **Mobile:** React Native 0.81, Expo 54, TypeScript
- **Infrastructure:** Docker, Kubernetes, GitHub Actions
- **External APIs:** OpenWeatherMap, Google Maps (comparison only)

## Key Features Summary:
1. ✅ Weather-aware lane splitting recommendations
2. ✅ Color-coded route safety visualization
3. ✅ Full user authentication & profiles
4. ✅ Motorcycle garage management
5. ✅ Community platform with chat
6. ✅ Crowdsourced road reports
7. ✅ Gamification with badges & leaderboards

---

*Document generated: 2026-04-05*
*Version: 2.0.0*
*Status: Ready for Implementation*

