"""Road reports API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.routes.auth import get_current_user
from api.services.road_reports import RoadReportService
from api.services.gamification import GamificationService
from api.models.road_report import ReportCategory, ReportType, ReportSeverity

router = APIRouter(prefix="/api/reports", tags=["road-reports"])


class ReportResponse(BaseModel):
    id: UUID
    reporter_id: Optional[UUID] = None
    latitude: float
    longitude: float
    location_name: Optional[str] = None
    road_name: Optional[str] = None
    category: str
    type: str
    severity: str
    title: Optional[str] = None
    description: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    affects_direction: str = "both"
    upvote_count: int = 0
    downvote_count: int = 0
    verification_score: float = 0
    is_verified: bool = False
    is_resolved: bool = False
    created_at: datetime
    model_config = {"from_attributes": True}


class CreateReportRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    category: str
    type: str
    severity: str = "medium"
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    photo_urls: Optional[List[str]] = None
    location_name: Optional[str] = None
    road_name: Optional[str] = None
    affects_direction: str = "both"
    anonymous: bool = False


class VoteRequest(BaseModel):
    is_upvote: bool


@router.get("", response_model=List[ReportResponse])
async def get_reports_in_area(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, ge=0.1, le=50),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    svc = RoadReportService(db)
    categories = [ReportCategory(category)] if category else None
    reports = await svc.get_reports_in_area(lat, lng, radius_km, categories)
    return [ReportResponse.model_validate(r) for r in reports]


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    request: CreateReportRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = RoadReportService(db)
    try:
        cat = ReportCategory(request.category)
        rt = ReportType(request.type)
        sev = ReportSeverity(request.severity)
    except ValueError as e:
        raise HTTPException(400, str(e))

    report = await svc.create_report(
        reporter_id=user.id, latitude=request.latitude, longitude=request.longitude,
        category=cat, report_type=rt, severity=sev,
        title=request.title, description=request.description,
        photo_urls=request.photo_urls, location_name=request.location_name,
        road_name=request.road_name, affects_direction=request.affects_direction,
        anonymous=request.anonymous,
    )

    try:
        gam = GamificationService(db)
        await gam.award_points(user.id, 5, "report_submitted", "reports", "report", report.id)
    except Exception:
        pass

    return ReportResponse.model_validate(report)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = RoadReportService(db)
    report = await svc.get_report(report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    return ReportResponse.model_validate(report)


@router.post("/{report_id}/vote", response_model=ReportResponse)
async def vote_report(
    report_id: UUID,
    request: VoteRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = RoadReportService(db)
    try:
        report = await svc.vote_report(report_id, user.id, request.is_upvote)
        return ReportResponse.model_validate(report)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/{report_id}/resolve", response_model=ReportResponse)
async def resolve_report(
    report_id: UUID,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = RoadReportService(db)
    try:
        report = await svc.resolve_report(report_id, user.id)
        return ReportResponse.model_validate(report)
    except ValueError as e:
        raise HTTPException(404, str(e))
