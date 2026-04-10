"""Road reports and warnings service."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple
from uuid import UUID
from math import radians, sin, cos, sqrt, atan2

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.road_report import (
    RoadReport, ReportVote,
    ReportCategory, ReportType, ReportSeverity,
)

EXPIRATION_HOURS = {
    "oil_spill": 24, "debris": 12, "pothole": 168, "construction": 720,
    "traffic_light": 48, "electrical": 24,
    "wet": 6, "ice": 12, "fog": 4, "sand": 24, "leaves": 24,
    "heavy_traffic": 2, "accident": 4, "police": 2, "road_closure": 48,
    "gas_station": None, "moto_shop": None, "parking": None, "scenic": None, "cafe": None,
}


class RoadReportService:
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
        exp_hours = EXPIRATION_HOURS.get(report_type.value)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=exp_hours) if exp_hours else None

        report = RoadReport(
            reporter_id=reporter_id if not anonymous else None,
            reporter_anonymous=anonymous,
            latitude=latitude, longitude=longitude,
            location_name=location_name, road_name=road_name,
            category=category, type=report_type, severity=severity,
            title=title, description=description,
            photo_urls=photo_urls or [], affects_direction=affects_direction,
            expires_at=expires_at,
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_report(self, report_id: UUID) -> Optional[RoadReport]:
        result = await self.db.execute(select(RoadReport).where(RoadReport.id == report_id))
        return result.scalar_one_or_none()

    async def get_reports_in_area(
        self,
        center_lat: float,
        center_lng: float,
        radius_km: float = 10.0,
        categories: Optional[List[ReportCategory]] = None,
        active_only: bool = True,
        limit: int = 100,
    ) -> List[RoadReport]:
        lat_delta = radius_km / 111.0
        lng_delta = radius_km / (111.0 * cos(radians(center_lat)))

        query = select(RoadReport).where(and_(
            RoadReport.latitude.between(center_lat - lat_delta, center_lat + lat_delta),
            RoadReport.longitude.between(center_lng - lng_delta, center_lng + lng_delta),
        ))
        if active_only:
            query = query.where(and_(
                RoadReport.is_active == True,
                RoadReport.is_resolved == False,
                or_(RoadReport.expires_at.is_(None), RoadReport.expires_at > datetime.now(timezone.utc)),
            ))
        if categories:
            query = query.where(RoadReport.category.in_(categories))
        query = query.order_by(RoadReport.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        reports = list(result.scalars().all())

        return [r for r in reports if self._haversine(center_lat, center_lng, r.latitude, r.longitude) <= radius_km]

    async def vote_report(self, report_id: UUID, user_id: UUID, is_upvote: bool) -> RoadReport:
        report = await self.get_report(report_id)
        if not report:
            raise ValueError("Report not found")

        result = await self.db.execute(
            select(ReportVote).where(ReportVote.report_id == report_id, ReportVote.user_id == user_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            if existing.is_upvote != is_upvote:
                if is_upvote:
                    report.upvote_count += 1
                    report.downvote_count -= 1
                else:
                    report.upvote_count -= 1
                    report.downvote_count += 1
                existing.is_upvote = is_upvote
        else:
            self.db.add(ReportVote(report_id=report_id, user_id=user_id, is_upvote=is_upvote))
            if is_upvote:
                report.upvote_count += 1
            else:
                report.downvote_count += 1

        total = report.upvote_count + report.downvote_count
        if total > 0:
            report.verification_score = report.upvote_count / total
            if report.verification_score >= 0.8 and total >= 5:
                report.is_verified = True
            if report.verification_score < 0.3 and total >= 3:
                report.is_resolved = True
                report.resolved_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def resolve_report(self, report_id: UUID, resolved_by: UUID) -> RoadReport:
        report = await self.get_report(report_id)
        if not report:
            raise ValueError("Report not found")
        report.is_resolved = True
        report.resolved_at = datetime.now(timezone.utc)
        report.resolved_by = resolved_by
        await self.db.commit()
        await self.db.refresh(report)
        return report

    @staticmethod
    def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        R = 6371
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat, dlng = lat2 - lat1, lng2 - lng1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
        return R * 2 * atan2(sqrt(a), sqrt(1 - a))
