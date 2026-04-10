"""Gamification database models."""

from __future__ import annotations

import uuid
from datetime import datetime, date, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Integer, String, Text, Date,
    ForeignKey, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.database import Base


class UserPoints(Base):
    __tablename__ = "user_points"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    current_streak_days = Column(Integer, default=0)
    longest_streak_days = Column(Integer, default=0)
    last_activity_date = Column(Date)
    points_routes = Column(Integer, default=0)
    points_reports = Column(Integer, default=0)
    points_community = Column(Integer, default=0)
    points_helping = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PointTransaction(Base):
    __tablename__ = "point_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    points = Column(Integer, nullable=False)
    reason = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    reference_type = Column(String(50))
    reference_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Badge(Base):
    __tablename__ = "badges"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    name_tr = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    description_tr = Column(Text, nullable=False)
    icon = Column(String(10), nullable=False)
    category = Column(String(50), nullable=False)
    requirement_type = Column(String(50), nullable=False)
    requirement_value = Column(Integer, nullable=False)
    points_reward = Column(Integer, default=0)
    is_secret = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UserBadge(Base):
    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    badge_id = Column(String(50), ForeignKey("badges.id"), nullable=False)
    earned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)
    title_tr = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    description_tr = Column(Text, nullable=False)
    type = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    requirement_type = Column(String(50), nullable=False)
    requirement_value = Column(Integer, nullable=False)
    points_reward = Column(Integer, nullable=False)
    badge_reward = Column(String(50), ForeignKey("badges.id"))
    starts_at = Column(DateTime(timezone=True))
    ends_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UserChallenge(Base):
    __tablename__ = "user_challenges"
    __table_args__ = (UniqueConstraint("user_id", "challenge_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("challenges.id"), nullable=False)
    progress = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
