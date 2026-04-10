"""Route history and analytics service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.route_history import RouteHistory


class RouteHistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_route(
        self,
        user_id: UUID,
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float,
        mode: str,
        distance_m: int,
        duration_s: int,
        origin_label: Optional[str] = None,
        destination_label: Optional[str] = None,
        motorcycle_id: Optional[UUID] = None,
        lane_split_m: int = 0,
        fun_curves: int = 0,
        dangerous_curves: int = 0,
        avg_grade: float = 0,
        safety_score: Optional[float] = None,
        weather_condition: Optional[str] = None,
        road_surface: Optional[str] = None,
        weather_modifier: Optional[float] = None,
    ) -> RouteHistory:
        entry = RouteHistory(
            user_id=user_id, motorcycle_id=motorcycle_id,
            origin_lat=origin_lat, origin_lng=origin_lng,
            origin_label=origin_label,
            destination_lat=destination_lat, destination_lng=destination_lng,
            destination_label=destination_label,
            mode=mode, distance_m=distance_m, duration_s=duration_s,
            lane_split_m=lane_split_m, fun_curves=fun_curves,
            dangerous_curves=dangerous_curves, avg_grade=avg_grade,
            safety_score=safety_score, weather_condition=weather_condition,
            road_surface=road_surface, weather_modifier=weather_modifier,
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def complete_route(self, route_id: UUID, user_id: UUID) -> Optional[RouteHistory]:
        result = await self.db.execute(
            select(RouteHistory).where(RouteHistory.id == route_id, RouteHistory.user_id == user_id)
        )
        entry = result.scalar_one_or_none()
        if not entry:
            return None
        entry.completed = True
        entry.completed_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def get_history(
        self, user_id: UUID, limit: int = 20, offset: int = 0, favorites_only: bool = False,
    ) -> List[RouteHistory]:
        query = select(RouteHistory).where(RouteHistory.user_id == user_id)
        if favorites_only:
            query = query.where(RouteHistory.is_favorite == True)
        query = query.order_by(RouteHistory.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def toggle_favorite(self, route_id: UUID, user_id: UUID) -> Optional[RouteHistory]:
        result = await self.db.execute(
            select(RouteHistory).where(RouteHistory.id == route_id, RouteHistory.user_id == user_id)
        )
        entry = result.scalar_one_or_none()
        if not entry:
            return None
        entry.is_favorite = not entry.is_favorite
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def get_analytics(self, user_id: UUID) -> dict:
        result = await self.db.execute(
            select(
                func.count(RouteHistory.id).label("total_routes"),
                func.sum(RouteHistory.distance_m).label("total_distance_m"),
                func.sum(RouteHistory.duration_s).label("total_duration_s"),
                func.sum(RouteHistory.lane_split_m).label("total_lane_split_m"),
                func.sum(RouteHistory.fun_curves).label("total_fun_curves"),
                func.avg(RouteHistory.safety_score).label("avg_safety_score"),
            ).where(RouteHistory.user_id == user_id, RouteHistory.completed == True)
        )
        row = result.one()
        return {
            "total_routes": row.total_routes or 0,
            "total_distance_km": round((row.total_distance_m or 0) / 1000, 1),
            "total_hours": round((row.total_duration_s or 0) / 3600, 1),
            "total_lane_split_km": round((row.total_lane_split_m or 0) / 1000, 1),
            "total_fun_curves": row.total_fun_curves or 0,
            "avg_safety_score": round(row.avg_safety_score or 0, 2),
        }

    async def delete_entry(self, route_id: UUID, user_id: UUID) -> bool:
        result = await self.db.execute(
            select(RouteHistory).where(RouteHistory.id == route_id, RouteHistory.user_id == user_id)
        )
        entry = result.scalar_one_or_none()
        if not entry:
            return False
        await self.db.delete(entry)
        await self.db.commit()
        return True
