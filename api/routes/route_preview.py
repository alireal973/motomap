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
    mesafe_m: float
    sure_s: float
    viraj_fun: float
    viraj_tehlike: float
    yuksek_risk: float
    ortalama_egim: float
    serit_paylasimi: float
    ucretli: bool


class RouteModeResponse(BaseModel):
    coordinates: list[LatLngResponse]
    stats: ModeStatsResponse


class GoogleStatsResponse(BaseModel):
    mesafe_m: float | None = None
    sure_s: float | None = None
    mesafe_text: str | None = None
    sure_text: str | None = None


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


from fastapi.concurrency import run_in_threadpool

@router.get("", response_model=RoutePreviewResponse)
async def get_route_preview():
    svc = RoutePreviewService()
    try:
        payload = await run_in_threadpool(svc.get_route_payload)
        return RoutePreviewResponse.model_validate(payload)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Route payload not found")
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"Route payload error: {exc}")


@router.get("/info", response_model=RoutePreviewInfoResponse)
async def get_route_preview_info():
    svc = RoutePreviewService()
    return RoutePreviewInfoResponse.model_validate(svc.get_route_info())
