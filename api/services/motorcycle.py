"""Motorcycle management service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.motorcycle import Motorcycle, MotorcycleType


class MotorcycleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_motorcycles(self, user_id: UUID) -> List[Motorcycle]:
        result = await self.db.execute(
            select(Motorcycle)
            .where(Motorcycle.user_id == user_id)
            .order_by(Motorcycle.is_primary.desc(), Motorcycle.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_motorcycle(self, motorcycle_id: UUID, user_id: UUID) -> Optional[Motorcycle]:
        result = await self.db.execute(
            select(Motorcycle).where(
                Motorcycle.id == motorcycle_id,
                Motorcycle.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_motorcycle(
        self,
        user_id: UUID,
        brand: str,
        model: str,
        cc: int,
        type: MotorcycleType,
        weight_kg: Optional[int] = None,
        torque_nm: Optional[int] = None,
        tire_type: Optional[str] = None,
        year: Optional[int] = None,
        color: Optional[str] = None,
        nickname: Optional[str] = None,
        license_plate: Optional[str] = None,
        is_primary: bool = False,
    ) -> Motorcycle:
        if is_primary:
            await self.db.execute(
                update(Motorcycle)
                .where(Motorcycle.user_id == user_id, Motorcycle.is_primary == True)
                .values(is_primary=False)
            )

        motorcycle = Motorcycle(
            user_id=user_id,
            brand=brand,
            model=model,
            cc=cc,
            type=type,
            weight_kg=weight_kg,
            torque_nm=torque_nm,
            tire_type=tire_type,
            year=year,
            color=color,
            nickname=nickname,
            license_plate=license_plate,
            is_primary=is_primary,
        )
        self.db.add(motorcycle)
        await self.db.commit()
        await self.db.refresh(motorcycle)
        return motorcycle

    async def update_motorcycle(
        self,
        motorcycle_id: UUID,
        user_id: UUID,
        **kwargs,
    ) -> Optional[Motorcycle]:
        motorcycle = await self.get_motorcycle(motorcycle_id, user_id)
        if not motorcycle:
            return None

        if kwargs.get("is_primary"):
            await self.db.execute(
                update(Motorcycle)
                .where(Motorcycle.user_id == user_id, Motorcycle.is_primary == True)
                .values(is_primary=False)
            )

        for key, value in kwargs.items():
            if value is not None and hasattr(motorcycle, key):
                setattr(motorcycle, key, value)

        motorcycle.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(motorcycle)
        return motorcycle

    async def delete_motorcycle(self, motorcycle_id: UUID, user_id: UUID) -> bool:
        motorcycle = await self.get_motorcycle(motorcycle_id, user_id)
        if not motorcycle:
            return False
        await self.db.delete(motorcycle)
        await self.db.commit()
        return True

    async def set_primary(self, motorcycle_id: UUID, user_id: UUID) -> Optional[Motorcycle]:
        return await self.update_motorcycle(motorcycle_id, user_id, is_primary=True)
