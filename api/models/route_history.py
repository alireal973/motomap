"""Route history database model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, Float, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from api.database import Base


class RouteHistory(Base):
    __tablename__ = "route_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    motorcycle_id = Column(UUID(as_uuid=True), ForeignKey("motorcycles.id", ondelete="SET NULL"))

    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    origin_label = Column(String(200))
    destination_lat = Column(Float, nullable=False)
    destination_lng = Column(Float, nullable=False)
    destination_label = Column(String(200))

    mode = Column(String(50), nullable=False)
    distance_m = Column(Integer, nullable=False)
    duration_s = Column(Integer, nullable=False)

    lane_split_m = Column(Integer, default=0)
    fun_curves = Column(Integer, default=0)
    dangerous_curves = Column(Integer, default=0)
    avg_grade = Column(Float, default=0)
    safety_score = Column(Float)

    weather_condition = Column(String(50))
    road_surface = Column(String(50))
    weather_modifier = Column(Float)

    is_favorite = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
