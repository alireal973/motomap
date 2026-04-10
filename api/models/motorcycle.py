"""Motorcycle database model."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.database import Base


class MotorcycleType(PyEnum):
    NAKED = "naked"
    SPORT = "sport"
    TOURING = "touring"
    ADVENTURE = "adventure"
    CRUISER = "cruiser"
    SCOOTER = "scooter"
    CLASSIC = "classic"
    DUAL_SPORT = "dual_sport"
    ENDURO = "enduro"
    SUPERMOTO = "supermoto"
    CAFE_RACER = "cafe_racer"
    BOBBER = "bobber"


class Motorcycle(Base):
    __tablename__ = "motorcycles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    brand = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    year = Column(Integer)
    cc = Column(Integer, nullable=False)
    type = Column(Enum(MotorcycleType), nullable=False)

    color = Column(String(50))
    nickname = Column(String(100))
    vin = Column(String(17))
    license_plate = Column(String(20))

    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)

    total_km = Column(Integer, default=0)
    total_routes = Column(Integer, default=0)

    photo_url = Column(Text)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="motorcycles")

    def __repr__(self):
        return f"<Motorcycle {self.brand} {self.model} ({self.cc}cc)>"

    @property
    def full_name(self) -> str:
        parts = [self.brand, self.model]
        if self.year:
            parts.append(f"({self.year})")
        return " ".join(parts)
