"""Road report database models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean, Column, DateTime, Integer, String, Text, Float,
    ForeignKey, Enum, UniqueConstraint, ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.database import Base


class ReportCategory(PyEnum):
    HAZARD = "hazard"
    SURFACE = "surface"
    TRAFFIC = "traffic"
    POI = "poi"


class ReportType(PyEnum):
    OIL_SPILL = "oil_spill"
    DEBRIS = "debris"
    POTHOLE = "pothole"
    CONSTRUCTION = "construction"
    TRAFFIC_LIGHT = "traffic_light"
    ELECTRICAL = "electrical"
    WET = "wet"
    ICE = "ice"
    FOG = "fog"
    SAND = "sand"
    LEAVES = "leaves"
    HEAVY_TRAFFIC = "heavy_traffic"
    ACCIDENT = "accident"
    POLICE = "police"
    ROAD_CLOSURE = "road_closure"
    GAS_STATION = "gas_station"
    MOTO_SHOP = "moto_shop"
    PARKING = "parking"
    SCENIC = "scenic"
    CAFE = "cafe"


class ReportSeverity(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RoadReport(Base):
    __tablename__ = "road_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    reporter_anonymous = Column(Boolean, default=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(200))
    road_name = Column(String(200))

    category = Column(Enum(ReportCategory), nullable=False)
    type = Column(Enum(ReportType), nullable=False)
    severity = Column(Enum(ReportSeverity), default=ReportSeverity.MEDIUM)

    title = Column(String(200))
    description = Column(Text)
    photo_urls = Column(ARRAY(Text))
    affects_direction = Column(String(20), default="both")

    upvote_count = Column(Integer, default=0)
    downvote_count = Column(Integer, default=0)
    verification_score = Column(Float, default=0)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    expires_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    votes = relationship("ReportVote", back_populates="report", cascade="all, delete-orphan")


class ReportVote(Base):
    __tablename__ = "report_votes"
    __table_args__ = (UniqueConstraint("report_id", "user_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("road_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    is_upvote = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    report = relationship("RoadReport", back_populates="votes")
