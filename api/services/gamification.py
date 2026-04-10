"""Gamification service for points, badges, and leaderboards."""

from __future__ import annotations

from datetime import datetime, date, timezone
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.gamification import (
    UserPoints, PointTransaction, Badge, UserBadge,
    Challenge, UserChallenge,
)

LEVEL_THRESHOLDS = [
    (1, 0), (2, 100), (3, 500), (4, 1500), (5, 5000), (6, 15000),
]

POINT_VALUES = {
    "route_completed": 10,
    "report_submitted": 5,
    "report_verified": 10,
    "report_helpful": 15,
    "community_post": 3,
    "help_given": 25,
    "daily_streak": 5,
}

DEFAULT_BADGES = [
    {"id": "first_route", "name": "New Rider", "name_tr": "Yeni Surucu", "icon": "S", "category": "riding", "description": "Complete your first route", "description_tr": "Ilk rotani tamamla", "requirement_type": "routes_completed", "requirement_value": 1, "points_reward": 50},
    {"id": "explorer_10", "name": "Explorer", "name_tr": "Kasif", "icon": "K", "category": "riding", "description": "Complete 10 unique routes", "description_tr": "10 farkli rota tamamla", "requirement_type": "unique_routes", "requirement_value": 10, "points_reward": 100},
    {"id": "km_1000", "name": "Road Warrior", "name_tr": "Yol Savascisi", "icon": "W", "category": "riding", "description": "Ride 1000 km total", "description_tr": "Toplam 1000 km sur", "requirement_type": "total_km", "requirement_value": 1000, "points_reward": 200},
    {"id": "km_10000", "name": "Legend", "name_tr": "Efsane", "icon": "L", "category": "riding", "description": "Ride 10000 km total", "description_tr": "Toplam 10000 km sur", "requirement_type": "total_km", "requirement_value": 10000, "points_reward": 1000},
    {"id": "first_report", "name": "Watchful Eye", "name_tr": "Dikkatli Goz", "icon": "G", "category": "reports", "description": "Submit your first report", "description_tr": "Ilk raporunu gonder", "requirement_type": "reports_submitted", "requirement_value": 1, "points_reward": 25},
    {"id": "guardian_50", "name": "Guardian", "name_tr": "Koruyucu", "icon": "U", "category": "reports", "description": "Submit 50 reports", "description_tr": "50 rapor gonder", "requirement_type": "reports_submitted", "requirement_value": 50, "points_reward": 500},
    {"id": "social_100", "name": "Social Butterfly", "name_tr": "Sosyal Kelebek", "icon": "B", "category": "community", "description": "Create 100 posts", "description_tr": "100 gonderi olustur", "requirement_type": "posts_created", "requirement_value": 100, "points_reward": 300},
    {"id": "helpful_10", "name": "Helpful Rider", "name_tr": "Yardimsever", "icon": "Y", "category": "community", "description": "Help 10 riders", "description_tr": "10 motorcuya yardim et", "requirement_type": "help_given", "requirement_value": 10, "points_reward": 250},
    {"id": "streak_7", "name": "Consistent", "name_tr": "Tutarli", "icon": "T", "category": "streak", "description": "7-day activity streak", "description_tr": "7 gun ust uste aktif ol", "requirement_type": "streak_days", "requirement_value": 7, "points_reward": 100},
    {"id": "streak_30", "name": "Dedicated", "name_tr": "Adanmis", "icon": "A", "category": "streak", "description": "30-day activity streak", "description_tr": "30 gun ust uste aktif ol", "requirement_type": "streak_days", "requirement_value": 30, "points_reward": 500},
]


class GamificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_points(self, user_id: UUID) -> UserPoints:
        result = await self.db.execute(
            select(UserPoints).where(UserPoints.user_id == user_id)
        )
        points = result.scalar_one_or_none()
        if not points:
            points = UserPoints(user_id=user_id)
            self.db.add(points)
            await self.db.commit()
            await self.db.refresh(points)
        return points

    async def award_points(
        self,
        user_id: UUID,
        points: int,
        reason: str,
        category: str,
        reference_type: Optional[str] = None,
        reference_id: Optional[UUID] = None,
    ) -> UserPoints:
        user_points = await self.get_user_points(user_id)

        transaction = PointTransaction(
            user_id=user_id, points=points, reason=reason,
            category=category, reference_type=reference_type,
            reference_id=reference_id,
        )
        self.db.add(transaction)

        user_points.total_points += points
        cat_field = f"points_{category}"
        if hasattr(user_points, cat_field):
            setattr(user_points, cat_field, getattr(user_points, cat_field) + points)

        # Update streak
        today = date.today()
        if user_points.last_activity_date:
            delta = (today - user_points.last_activity_date).days
            if delta == 1:
                user_points.current_streak_days += 1
            elif delta > 1:
                user_points.current_streak_days = 1
        else:
            user_points.current_streak_days = 1
        user_points.last_activity_date = today
        user_points.longest_streak_days = max(user_points.longest_streak_days, user_points.current_streak_days)

        # Update level
        for level, threshold in reversed(LEVEL_THRESHOLDS):
            if user_points.total_points >= threshold:
                user_points.level = level
                break

        user_points.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(user_points)
        return user_points

    async def get_user_badges(self, user_id: UUID) -> List[dict]:
        result = await self.db.execute(
            select(UserBadge, Badge)
            .join(Badge, UserBadge.badge_id == Badge.id)
            .where(UserBadge.user_id == user_id)
            .order_by(UserBadge.earned_at.desc())
        )
        return [
            {
                "badge_id": ub.badge_id, "earned_at": ub.earned_at.isoformat(),
                "name": b.name, "name_tr": b.name_tr, "icon": b.icon,
                "category": b.category, "description_tr": b.description_tr,
            }
            for ub, b in result.all()
        ]

    async def award_badge(self, user_id: UUID, badge_id: str) -> Optional[UserBadge]:
        existing = await self.db.execute(
            select(UserBadge).where(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id)
        )
        if existing.scalar_one_or_none():
            return None

        badge = await self.db.execute(select(Badge).where(Badge.id == badge_id))
        badge_obj = badge.scalar_one_or_none()
        if not badge_obj:
            return None

        user_badge = UserBadge(user_id=user_id, badge_id=badge_id)
        self.db.add(user_badge)

        if badge_obj.points_reward > 0:
            await self.award_points(user_id, badge_obj.points_reward, f"Badge: {badge_id}", "badges")

        await self.db.commit()
        await self.db.refresh(user_badge)
        return user_badge

    async def get_all_badges(self) -> List[Badge]:
        result = await self.db.execute(
            select(Badge).where(Badge.is_secret == False).order_by(Badge.category, Badge.requirement_value)
        )
        return list(result.scalars().all())

    async def get_leaderboard(self, period: str = "all_time", category: str = "total", limit: int = 20) -> List[dict]:
        if category == "total":
            order_col = UserPoints.total_points
        elif category == "routes":
            order_col = UserPoints.points_routes
        elif category == "reports":
            order_col = UserPoints.points_reports
        elif category == "community":
            order_col = UserPoints.points_community
        else:
            order_col = UserPoints.total_points

        result = await self.db.execute(
            select(UserPoints).order_by(order_col.desc()).limit(limit)
        )
        entries = result.scalars().all()
        return [
            {"rank": i + 1, "user_id": str(e.user_id), "points": e.total_points, "level": e.level, "streak": e.current_streak_days}
            for i, e in enumerate(entries)
        ]

    async def seed_badges(self) -> int:
        count = 0
        for b in DEFAULT_BADGES:
            existing = await self.db.execute(select(Badge).where(Badge.id == b["id"]))
            if not existing.scalar_one_or_none():
                self.db.add(Badge(**b))
                count += 1
        await self.db.commit()
        return count
