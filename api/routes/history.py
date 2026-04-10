"""Route history API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.routes.auth import get_current_user
from api.services.route_history import RouteHistoryService
from api.services.gamification import GamificationService

router = APIRouter(prefix="/api/history", tags=["history"])


class RouteHistoryResponse(BaseModel):
    id: UUID
    origin_lat: float
    origin_lng: float
    origin_label: Optional[str] = None
    destination_lat: float
    destination_lng: float
    destination_label: Optional[str] = None
    mode: str
    distance_m: int
    duration_s: int
    lane_split_m: int = 0
    fun_curves: int = 0
    dangerous_curves: int = 0
    safety_score: Optional[float] = None
    weather_condition: Optional[str] = None
    is_favorite: bool = False
    completed: bool = False
    created_at: datetime
    model_config = {"from_attributes": True}


class RecordRouteRequest(BaseModel):
    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lng: float = Field(..., ge=-180, le=180)
    destination_lat: float = Field(..., ge=-90, le=90)
    destination_lng: float = Field(..., ge=-180, le=180)
    origin_label: Optional[str] = None
    destination_label: Optional[str] = None
    mode: str
    distance_m: int = Field(..., gt=0)
    duration_s: int = Field(..., gt=0)
    motorcycle_id: Optional[UUID] = None
    lane_split_m: int = 0
    fun_curves: int = 0
    dangerous_curves: int = 0
    avg_grade: float = 0
    safety_score: Optional[float] = Field(None, ge=0, le=1)
    weather_condition: Optional[str] = None
    road_surface: Optional[str] = None
    weather_modifier: Optional[float] = None


class AnalyticsResponse(BaseModel):
    total_routes: int
    total_distance_km: float
    total_hours: float
    total_lane_split_km: float
    total_fun_curves: int
    avg_safety_score: float


@router.get("", response_model=List[RouteHistoryResponse])
async def get_history(
    favorites_only: bool = Query(False),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = RouteHistoryService(db)
    entries = await svc.get_history(user.id, limit, offset, favorites_only)
    return [RouteHistoryResponse.model_validate(e) for e in entries]


@router.post("", response_model=RouteHistoryResponse, status_code=status.HTTP_201_CREATED)
async def record_route(
    request: RecordRouteRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = RouteHistoryService(db)
    entry = await svc.record_route(user_id=user.id, **request.model_dump())
    return RouteHistoryResponse.model_validate(entry)


@router.post("/{route_id}/complete", response_model=RouteHistoryResponse)
async def complete_route(
    route_id: UUID, user=Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = RouteHistoryService(db)
    entry = await svc.complete_route(route_id, user.id)
    if not entry:
        raise HTTPException(404, "Route not found")

    try:
        gam = GamificationService(db)
        await gam.award_points(user.id, 10, "route_completed", "routes", "route", route_id)
    except Exception:
        pass

    return RouteHistoryResponse.model_validate(entry)


@router.post("/{route_id}/favorite", response_model=RouteHistoryResponse)
async def toggle_favorite(
    route_id: UUID, user=Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = RouteHistoryService(db)
    entry = await svc.toggle_favorite(route_id, user.id)
    if not entry:
        raise HTTPException(404, "Route not found")
    return RouteHistoryResponse.model_validate(entry)


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    route_id: UUID, user=Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = RouteHistoryService(db)
    if not await svc.delete_entry(route_id, user.id):
        raise HTTPException(404, "Route not found")


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = RouteHistoryService(db)
    return await svc.get_analytics(user.id)
