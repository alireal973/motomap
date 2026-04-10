"""Weather data models."""

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
    grip_factor: float
    visibility_factor: float
    wind_risk_factor: float
    overall_safety_score: float
    lane_splitting_modifier: float
    warnings: list[str]
