"""User database model."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False)
    password_hash = Column(String(255), nullable=False)

    username = Column(String(50), unique=True, index=True)
    display_name = Column(String(100))
    avatar_url = Column(Text)
    bio = Column(Text)

    city = Column(String(100), index=True)
    country = Column(String(100))

    riding_since = Column(Date)
    license_type = Column(String(50))
    total_km = Column(Integer, default=0)

    preferred_language = Column(String(10), default="tr")
    distance_unit = Column(String(10), default="km")
    theme = Column(String(20), default="dark")
    notifications_enabled = Column(Boolean, default=True)

    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime(timezone=True))

    google_id = Column(String(255), unique=True, index=True, nullable=True)
    auth_provider = Column(String(20), default="local")

    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)

    motorcycles = relationship("Motorcycle", back_populates="owner", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def primary_motorcycle(self) -> Optional["Motorcycle"]:
        for moto in self.motorcycles:
            if moto.is_primary:
                return moto
        return self.motorcycles[0] if self.motorcycles else None
