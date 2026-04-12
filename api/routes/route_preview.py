"""Route preview compatibility endpoints."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.services.route_preview import RoutePreviewService

router = APIRouter(prefix="/api/route", tags=["route"])


class LatLngResponse(BaseModel):
    lat: float
    lng: float


class ModeStatsResponse(BaseModel):
    mesafe_m: int
    sure_s: int
    viraj_fun: int
    viraj_tehlike: int
    yuksek_risk: int
    ortalama_egim: float
    serit_paylasimi: int
    ucretli: bool


class RouteModeResponse(BaseModel):
    coordinates: list[LatLngResponse]
    stats: ModeStatsResponse


class GoogleStatsResponse(BaseModel):
    mesafe_m: int
    sure_s: int
    mesafe_text: str
    sure_text: str


class RoutePreviewResponse(BaseModel):
    origin: LatLngResponse
    destination: LatLngResponse
    origin_label: str
    destination_label: str
    google_route: list[LatLngResponse]
    google_stats: GoogleStatsResponse
    modes: Dict[str, RouteModeResponse]
    feature_overlays: Dict[str, Any] | None = None


class RoutePreviewInfoResponse(BaseModel):
    has_real_data: bool
    source: str
    path: Optional[str] = None
    note: str


@router.get("", response_model=RoutePreviewResponse)
async def get_route_preview():
    svc = RoutePreviewService()
    try:
        return RoutePreviewResponse.model_validate(svc.get_route_payload())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Route payload not found")
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"Route payload error: {exc}")


@router.get("/info", response_model=RoutePreviewInfoResponse)
async def get_route_preview_info():
    svc = RoutePreviewService()
    return RoutePreviewInfoResponse.model_validate(svc.get_route_info())
