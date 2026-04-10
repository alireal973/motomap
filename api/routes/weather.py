"""Weather API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter(prefix="/api/weather", tags=["weather"])


class WeatherResponse(BaseModel):
    condition: str
    temperature_celsius: float
    humidity_percent: float
    wind_speed_ms: float
    wind_gust_ms: Optional[float] = None
    visibility_meters: int
    precipitation_mm: float


class RoadConditionResponse(BaseModel):
    surface_condition: str
    overall_safety_score: float = Field(..., ge=0, le=1)
    lane_splitting_modifier: float = Field(..., ge=0, le=1)
    grip_factor: float = Field(..., ge=0, le=1)
    visibility_factor: float = Field(..., ge=0, le=1)
    wind_risk_factor: float = Field(..., ge=0, le=1)
    warnings: List[str] = []
    weather: WeatherResponse


@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
):
    try:
        from motomap.weather import WeatherService, WeatherConfig
        config = WeatherConfig.from_env()
        async with WeatherService(config) as service:
            weather = await service.get_weather(lat, lng)
            return WeatherResponse(
                condition=weather.condition.value,
                temperature_celsius=weather.temperature_celsius,
                humidity_percent=weather.humidity_percent,
                wind_speed_ms=weather.wind_speed_ms,
                wind_gust_ms=weather.wind_gust_ms,
                visibility_meters=weather.visibility_meters,
                precipitation_mm=weather.precipitation_mm,
            )
    except ImportError:
        raise HTTPException(status_code=501, detail="Weather module not available")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Weather service error: {str(e)}")


@router.get("/road-conditions", response_model=RoadConditionResponse)
async def get_road_conditions(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
):
    try:
        from motomap.weather import WeatherService, RoadConditionAssessor, WeatherConfig
        config = WeatherConfig.from_env()
        async with WeatherService(config) as service:
            weather = await service.get_weather(lat, lng)
            assessor = RoadConditionAssessor(config)
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
    except ImportError:
        raise HTTPException(status_code=501, detail="Weather module not available")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Weather service error: {str(e)}")
