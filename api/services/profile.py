"""User profile management service."""

from __future__ import annotations

from datetime import datetime, date, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.models.user import User
from api.models.motorcycle import Motorcycle, MotorcycleType


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, user_id: UUID) -> Optional[User]:
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
        user = await self.get_profile(user_id)
        if not user:
            raise ValueError("User not found")

        if display_name is not None:
            user.display_name = display_name
        if username is not None:
            existing = await self.db.execute(
                select(User).where(User.username == username, User.id != user_id)
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

        user.updated_at = datetime.now(timezone.utc)
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

        user.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_statistics(self, user_id: UUID) -> dict:
        user = await self.get_profile(user_id)
        if not user:
            return {}
        total_motorcycles = len(user.motorcycles)
        total_km = sum(m.total_km for m in user.motorcycles)
        total_routes = sum(m.total_routes for m in user.motorcycles)
        return {
            "total_motorcycles": total_motorcycles,
            "total_km": total_km,
            "total_routes": total_routes,
            "member_since": user.created_at.isoformat() if user.created_at else None,
            "is_premium": user.is_premium,
        }
