"""MotoMap API application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import init_db, close_db
from api.core.cache import cache
from api.models import *  # noqa: F401,F403 -- ensure all models register with Base.metadata
from api.routes.auth import router as auth_router
from api.routes.profile import router as profile_router
from api.routes.route_preview import router as route_preview_router
from api.routes.weather import router as weather_router
from api.routes.communities import router as communities_router
from api.routes.road_reports import router as road_reports_router
from api.routes.gamification import router as gamification_router
from api.routes.history import router as history_router
from api.routes.notifications import router as notifications_router
from api.routes.upload import router as upload_router
from api.middleware.rate_limit import RateLimitMiddleware
from api.middleware.logging import RequestLoggingMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await cache.connect()
    await init_db()
    logger.info("MotoMap API started")
    yield
    await close_db()
    await cache.close()
    logger.info("MotoMap API shut down")


app = FastAPI(
    title="MotoMap API",
    description="Motorcycle-aware routing and community platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(route_preview_router)
app.include_router(weather_router)
app.include_router(communities_router)
app.include_router(road_reports_router)
app.include_router(gamification_router)
app.include_router(history_router)
app.include_router(notifications_router)
app.include_router(upload_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
"""Database connection and session management."""

import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
import os

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://motomap:motomap_dev_secret@localhost:5432/motomap"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_size=20,
    max_overflow=10,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")


async def close_db():
    await engine.dispose()
    logger.info("Database connections closed")
"""Database models package."""

from api.models.user import User
from api.models.motorcycle import Motorcycle, MotorcycleType
from api.models.session import UserSession
from api.models.community import (
    Community, CommunityMembership, CommunityPost, PostComment,
    CommunityType, MembershipRole, PostType,
)
from api.models.road_report import (
    RoadReport, ReportVote,
    ReportCategory, ReportType, ReportSeverity,
)
from api.models.gamification import (
    UserPoints, PointTransaction, Badge, UserBadge,
    Challenge, UserChallenge,
)
from api.models.route_history import RouteHistory
from api.models.notification import Notification, PushToken, NotificationType

__all__ = [
    "User", "Motorcycle", "MotorcycleType", "UserSession",
    "Community", "CommunityMembership", "CommunityPost", "PostComment",
    "CommunityType", "MembershipRole", "PostType",
    "RoadReport", "ReportVote", "ReportCategory", "ReportType", "ReportSeverity",
    "UserPoints", "PointTransaction", "Badge", "UserBadge",
    "Challenge", "UserChallenge",
    "RouteHistory",
    "Notification", "PushToken", "NotificationType",
]
"""Community database models."""

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


class CommunityType(PyEnum):
    BRAND = "brand"
    STYLE = "style"
    REGION = "region"
    INTEREST = "interest"
    EVENT = "event"


class MembershipRole(PyEnum):
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"
    OWNER = "owner"


class PostType(PyEnum):
    DISCUSSION = "discussion"
    QUESTION = "question"
    HELP_REQUEST = "help_request"
    HELP_OFFER = "help_offer"
    RIDE_INVITE = "ride_invite"
    EVENT = "event"
    PHOTO = "photo"
    ROUTE_SHARE = "route_share"


class Community(Base):
    __tablename__ = "communities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    type = Column(Enum(CommunityType), nullable=False)

    icon_url = Column(Text)
    banner_url = Column(Text)
    color = Column(String(7))

    is_public = Column(Boolean, default=True)
    is_official = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)

    member_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    brand_name = Column(String(100))
    region_country = Column(String(100))
    region_city = Column(String(100))

    memberships = relationship("CommunityMembership", back_populates="community", cascade="all, delete-orphan")
    posts = relationship("CommunityPost", back_populates="community", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Community {self.name}>"


class CommunityMembership(Base):
    __tablename__ = "community_memberships"
    __table_args__ = (UniqueConstraint("community_id", "user_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id = Column(UUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(MembershipRole), default=MembershipRole.MEMBER)
    notifications_enabled = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_active_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    community = relationship("Community", back_populates="memberships")


class CommunityPost(Base):
    __tablename__ = "community_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id = Column(UUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(PostType), default=PostType.DISCUSSION)
    title = Column(String(200))
    content = Column(Text, nullable=False)
    image_urls = Column(ARRAY(Text))
    route_id = Column(UUID(as_uuid=True))
    location_lat = Column(Float)
    location_lng = Column(Float)
    location_name = Column(String(200))
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    community = relationship("Community", back_populates="posts")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")


class PostComment(Base):
    __tablename__ = "post_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("post_comments.id", ondelete="CASCADE"), index=True)
    content = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    post = relationship("CommunityPost", back_populates="comments")
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
"""Notification database models."""

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB

from api.database import Base


class NotificationType(PyEnum):
    BADGE_EARNED = "badge_earned"
    LEVEL_UP = "level_up"
    STREAK = "streak"
    CHALLENGE_COMPLETE = "challenge_complete"
    REPORT_VERIFIED = "report_verified"
    REPORT_NEAR_ROUTE = "report_near_route"
    COMMUNITY_POST = "community_post"
    COMMUNITY_REPLY = "community_reply"
    COMMUNITY_MENTION = "community_mention"
    HELP_REQUEST_NEARBY = "help_request_nearby"
    SYSTEM = "system"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    data = Column(JSONB)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PushToken(Base):
    __tablename__ = "push_tokens"
    __table_args__ = (UniqueConstraint("user_id", "token"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(500), nullable=False)
    device_type = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
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
"""User session database model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship

from api.database import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    refresh_token_hash = Column(String(255), nullable=False, index=True)

    device_id = Column(String(255))
    device_name = Column(String(255))
    device_type = Column(String(50))
    app_version = Column(String(20))

    ip_address = Column(INET)
    user_agent = Column(Text)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_used_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession user={self.user_id} device={self.device_type}>"
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
"""API routes package."""
"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.services.auth import AuthService, InvalidCredentialsError, UserExistsError, InvalidTokenError, PasswordResetError
from api.core.security import decode_token

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Must contain digit")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    is_premium: bool = False

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Must contain digit")
        return v


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Must contain digit")
        return v


class GoogleAuthRequest(BaseModel):
    id_token: str
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    if not payload or payload.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(UUID(payload.sub))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, req: Request, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        user = await auth_service.register(
            email=request.email, password=request.password, display_name=request.display_name,
        )
        device_info = {
            "ip_address": req.client.host if req.client else None,
            "user_agent": req.headers.get("user-agent"),
        }
        user, access_token, refresh_token = await auth_service.login(
            email=request.email, password=request.password, device_info=device_info,
        )
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(access_token=access_token, refresh_token=refresh_token),
        )
    except UserExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, req: Request, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    device_info = {
        "device_id": request.device_id,
        "device_name": request.device_name,
        "device_type": request.device_type,
        "ip_address": req.client.host if req.client else None,
        "user_agent": req.headers.get("user-agent"),
    }
    try:
        user, access_token, refresh_token = await auth_service.login(
            email=request.email, password=request.password, device_info=device_info,
        )
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(access_token=access_token, refresh_token=refresh_token),
        )
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    await auth_service.logout(request.refresh_token)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    await auth_service.logout_all(user.id)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        access_token, refresh_token = await auth_service.refresh_tokens(request.refresh_token)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_current_user)):
    return UserResponse.model_validate(user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(request: ChangePasswordRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        await auth_service.change_password(user.id, request.current_password, request.new_password)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    token = await auth_service.create_password_reset_token(request.email)
    # Always return 200 to prevent email enumeration.
    # In production, send reset email here via SMTP / transactional email service.
    if token:
        import logging
        logging.getLogger(__name__).info(
            "DEV: Password reset link -> /auth/reset-password?token=%s", token
        )
    return {"message": "If an account with that email exists, a reset link has been sent."}


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        await auth_service.reset_password_with_token(request.token, request.new_password)
    except PasswordResetError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest, req: Request, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    device_info = {
        "device_id": request.device_id,
        "device_name": request.device_name,
        "device_type": request.device_type,
        "ip_address": req.client.host if req.client else None,
        "user_agent": req.headers.get("user-agent"),
    }
    try:
        user, access_token, refresh_token = await auth_service.google_login(
            id_token=request.id_token, device_info=device_info,
        )
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(access_token=access_token, refresh_token=refresh_token),
        )
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
"""Community API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.routes.auth import get_current_user
from api.services.community import CommunityService
from api.services.gamification import GamificationService
from api.models.community import CommunityType, PostType

router = APIRouter(prefix="/api/communities", tags=["communities"])


class CommunityResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    type: str
    icon_url: Optional[str] = None
    banner_url: Optional[str] = None
    color: Optional[str] = None
    is_public: bool = True
    is_official: bool = False
    member_count: int = 0
    post_count: int = 0
    brand_name: Optional[str] = None
    region_city: Optional[str] = None
    model_config = {"from_attributes": True}


class CreateCommunityRequest(BaseModel):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None
    type: str
    brand_name: Optional[str] = None
    region_city: Optional[str] = None
    region_country: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7)


class PostResponse(BaseModel):
    id: UUID
    community_id: UUID
    author_id: UUID
    type: str
    title: Optional[str] = None
    content: str
    image_urls: Optional[List[str]] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_name: Optional[str] = None
    like_count: int = 0
    comment_count: int = 0
    is_pinned: bool = False
    created_at: datetime
    model_config = {"from_attributes": True}


class CreatePostRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    type: str = "discussion"
    title: Optional[str] = Field(None, max_length=200)
    image_urls: Optional[List[str]] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_name: Optional[str] = None


class CommentResponse(BaseModel):
    id: UUID
    post_id: UUID
    author_id: UUID
    parent_id: Optional[UUID] = None
    content: str
    like_count: int = 0
    created_at: datetime
    model_config = {"from_attributes": True}


class CreateCommentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    parent_id: Optional[UUID] = None


@router.get("", response_model=List[CommunityResponse])
async def list_communities(
    type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    svc = CommunityService(db)
    ct = CommunityType(type) if type else None
    communities = await svc.list_communities(ct, search, limit, offset)
    return [CommunityResponse.model_validate(c) for c in communities]


@router.get("/my", response_model=List[CommunityResponse])
async def my_communities(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = CommunityService(db)
    communities = await svc.get_user_communities(user.id)
    return [CommunityResponse.model_validate(c) for c in communities]


@router.post("", response_model=CommunityResponse, status_code=status.HTTP_201_CREATED)
async def create_community(
    request: CreateCommunityRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = CommunityService(db)
    try:
        ct = CommunityType(request.type)
    except ValueError:
        raise HTTPException(400, f"Invalid community type: {request.type}")
    try:
        community = await svc.create_community(
            name=request.name, slug=request.slug, community_type=ct,
            created_by=user.id, description=request.description,
            brand_name=request.brand_name, region_city=request.region_city,
            region_country=request.region_country, color=request.color,
        )
        return CommunityResponse.model_validate(community)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/{slug}", response_model=CommunityResponse)
async def get_community(slug: str, db: AsyncSession = Depends(get_db)):
    svc = CommunityService(db)
    community = await svc.get_community(slug)
    if not community:
        raise HTTPException(404, "Community not found")
    return CommunityResponse.model_validate(community)


@router.post("/{slug}/join", status_code=status.HTTP_201_CREATED)
async def join_community(slug: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = CommunityService(db)
    community = await svc.get_community(slug)
    if not community:
        raise HTTPException(404, "Community not found")
    try:
        await svc.join_community(community.id, user.id)
        return {"status": "joined"}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.delete("/{slug}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_community(slug: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = CommunityService(db)
    community = await svc.get_community(slug)
    if not community:
        raise HTTPException(404, "Community not found")
    try:
        await svc.leave_community(community.id, user.id)
    except ValueError as e:
        raise HTTPException(400, str(e))


# Posts
@router.get("/{slug}/posts", response_model=List[PostResponse])
async def get_posts(
    slug: str,
    type: Optional[str] = None,
    limit: int = Query(20, le=50),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    svc = CommunityService(db)
    community = await svc.get_community(slug)
    if not community:
        raise HTTPException(404, "Community not found")
    pt = PostType(type) if type else None
    posts = await svc.get_posts(community.id, pt, limit, offset)
    return [PostResponse.model_validate(p) for p in posts]


@router.post("/{slug}/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    slug: str,
    request: CreatePostRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = CommunityService(db)
    community = await svc.get_community(slug)
    if not community:
        raise HTTPException(404, "Community not found")
    try:
        pt = PostType(request.type)
    except ValueError:
        raise HTTPException(400, f"Invalid post type: {request.type}")
    try:
        post = await svc.create_post(
            community_id=community.id, author_id=user.id,
            content=request.content, post_type=pt, title=request.title,
            image_urls=request.image_urls, location_lat=request.location_lat,
            location_lng=request.location_lng, location_name=request.location_name,
        )

        try:
            gam = GamificationService(db)
            pts = 25 if pt in (PostType.HELP_OFFER, PostType.HELP_REQUEST) else 3
            cat = "helping" if pt == PostType.HELP_OFFER else "community"
            await gam.award_points(user.id, pts, "community_post", cat, "post", post.id)
        except Exception:
            pass

        return PostResponse.model_validate(post)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.delete("/{slug}/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(slug: str, post_id: UUID, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = CommunityService(db)
    try:
        deleted = await svc.delete_post(post_id, user.id)
        if not deleted:
            raise HTTPException(404, "Post not found")
    except ValueError as e:
        raise HTTPException(403, str(e))


# Comments
@router.get("/{slug}/posts/{post_id}/comments", response_model=List[CommentResponse])
async def get_comments(slug: str, post_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = CommunityService(db)
    comments = await svc.get_comments(post_id)
    return [CommentResponse.model_validate(c) for c in comments]


@router.post("/{slug}/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    slug: str, post_id: UUID,
    request: CreateCommentRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = CommunityService(db)
    try:
        comment = await svc.create_comment(
            post_id=post_id, author_id=user.id,
            content=request.content, parent_id=request.parent_id,
        )
        return CommentResponse.model_validate(comment)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/seed", status_code=status.HTTP_200_OK)
async def seed_communities(db: AsyncSession = Depends(get_db)):
    svc = CommunityService(db)
    count = await svc.seed_defaults()
    return {"seeded": count}
"""Gamification API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.routes.auth import get_current_user
from api.services.gamification import GamificationService

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


class PointsResponse(BaseModel):
    total_points: int
    level: int
    current_streak_days: int
    longest_streak_days: int
    points_routes: int
    points_reports: int
    points_community: int
    points_helping: int


class BadgeResponse(BaseModel):
    id: str
    name: str
    name_tr: str
    icon: str
    category: str
    description_tr: str
    requirement_type: str
    requirement_value: int
    points_reward: int = 0
    model_config = {"from_attributes": True}


class UserBadgeResponse(BaseModel):
    badge_id: str
    earned_at: str
    name: str
    name_tr: str
    icon: str
    category: str
    description_tr: str


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    points: int
    level: int
    streak: int


@router.get("/points", response_model=PointsResponse)
async def get_my_points(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = GamificationService(db)
    points = await svc.get_user_points(user.id)
    return PointsResponse(
        total_points=points.total_points, level=points.level,
        current_streak_days=points.current_streak_days,
        longest_streak_days=points.longest_streak_days,
        points_routes=points.points_routes, points_reports=points.points_reports,
        points_community=points.points_community, points_helping=points.points_helping,
    )


@router.get("/badges", response_model=List[BadgeResponse])
async def get_all_badges(db: AsyncSession = Depends(get_db)):
    svc = GamificationService(db)
    badges = await svc.get_all_badges()
    return [BadgeResponse.model_validate(b) for b in badges]


@router.get("/badges/my", response_model=List[UserBadgeResponse])
async def get_my_badges(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = GamificationService(db)
    return await svc.get_user_badges(user.id)


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    period: str = Query("all_time"),
    category: str = Query("total"),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    svc = GamificationService(db)
    return await svc.get_leaderboard(period, category, limit)


@router.post("/seed-badges")
async def seed_badges(db: AsyncSession = Depends(get_db)):
    svc = GamificationService(db)
    count = await svc.seed_badges()
    return {"seeded": count}
"""Route history API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.routes.auth import get_current_user
from api.services.route_history import RouteHistoryService
from api.services.gamification import GamificationService

router = APIRouter(prefix="/api/history", tags=["history"])


class RouteHistoryResponse(BaseModel):
    id: UUID
    origin_lat: float
    origin_lng: float
    origin_label: Optional[str] = None
    destination_lat: float
    destination_lng: float
    destination_label: Optional[str] = None
    mode: str
    distance_m: int
    duration_s: int
    lane_split_m: int = 0
    fun_curves: int = 0
    dangerous_curves: int = 0
    safety_score: Optional[float] = None
    weather_condition: Optional[str] = None
    is_favorite: bool = False
    completed: bool = False
    created_at: datetime
    model_config = {"from_attributes": True}


class RecordRouteRequest(BaseModel):
    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lng: float = Field(..., ge=-180, le=180)
    destination_lat: float = Field(..., ge=-90, le=90)
    destination_lng: float = Field(..., ge=-180, le=180)
    origin_label: Optional[str] = None
    destination_label: Optional[str] = None
    mode: str
    distance_m: int = Field(..., gt=0)
    duration_s: int = Field(..., gt=0)
    motorcycle_id: Optional[UUID] = None
    lane_split_m: int = 0
    fun_curves: int = 0
    dangerous_curves: int = 0
    avg_grade: float = 0
    safety_score: Optional[float] = Field(None, ge=0, le=1)
    weather_condition: Optional[str] = None
    road_surface: Optional[str] = None
    weather_modifier: Optional[float] = None


class AnalyticsResponse(BaseModel):
    total_routes: int
    total_distance_km: float
    total_hours: float
    total_lane_split_km: float
    total_fun_curves: int
    avg_safety_score: float


@router.get("", response_model=List[RouteHistoryResponse])
async def get_history(
    favorites_only: bool = Query(False),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = RouteHistoryService(db)
    entries = await svc.get_history(user.id, limit, offset, favorites_only)
    return [RouteHistoryResponse.model_validate(e) for e in entries]


@router.post("", response_model=RouteHistoryResponse, status_code=status.HTTP_201_CREATED)
async def record_route(
    request: RecordRouteRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = RouteHistoryService(db)
    entry = await svc.record_route(user_id=user.id, **request.model_dump())
    return RouteHistoryResponse.model_validate(entry)


@router.post("/{route_id}/complete", response_model=RouteHistoryResponse)
async def complete_route(
    route_id: UUID, user=Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = RouteHistoryService(db)
    entry = await svc.complete_route(route_id, user.id)
    if not entry:
        raise HTTPException(404, "Route not found")

    try:
        gam = GamificationService(db)
        await gam.award_points(user.id, 10, "route_completed", "routes", "route", route_id)
    except Exception:
        pass

    return RouteHistoryResponse.model_validate(entry)


@router.post("/{route_id}/favorite", response_model=RouteHistoryResponse)
async def toggle_favorite(
    route_id: UUID, user=Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = RouteHistoryService(db)
    entry = await svc.toggle_favorite(route_id, user.id)
    if not entry:
        raise HTTPException(404, "Route not found")
    return RouteHistoryResponse.model_validate(entry)


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    route_id: UUID, user=Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = RouteHistoryService(db)
    if not await svc.delete_entry(route_id, user.id):
        raise HTTPException(404, "Route not found")


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = RouteHistoryService(db)
    return await svc.get_analytics(user.id)
"""Notification API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.routes.auth import get_current_user
from api.services.notifications import NotificationService

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    id: UUID
    type: str
    title: str
    body: str
    data: Optional[Any] = None
    is_read: bool = False
    created_at: datetime
    model_config = {"from_attributes": True}


class RegisterTokenRequest(BaseModel):
    token: str = Field(..., max_length=500)
    device_type: str = Field(..., max_length=20)


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = NotificationService(db)
    notifs = await svc.get_notifications(user.id, unread_only, limit, offset)
    return [NotificationResponse.model_validate(n) for n in notifs]


@router.get("/unread-count")
async def get_unread_count(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = NotificationService(db)
    count = await svc.get_unread_count(user.id)
    return {"count": count}


@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(
    notification_id: UUID, user=Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = NotificationService(db)
    if not await svc.mark_read(notification_id, user.id):
        raise HTTPException(404, "Notification not found")


@router.post("/read-all", status_code=status.HTTP_200_OK)
async def mark_all_read(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    svc = NotificationService(db)
    count = await svc.mark_all_read(user.id)
    return {"marked": count}


@router.post("/push-token", status_code=status.HTTP_201_CREATED)
async def register_push_token(
    request: RegisterTokenRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = NotificationService(db)
    await svc.register_push_token(user.id, request.token, request.device_type)
    return {"status": "registered"}


@router.delete("/push-token/{token}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_push_token(
    token: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = NotificationService(db)
    await svc.unregister_push_token(user.id, token)
"""Profile and motorcycle API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.routes.auth import get_current_user, UserResponse
from api.services.profile import ProfileService
from api.services.motorcycle import MotorcycleService
from api.models.motorcycle import MotorcycleType

router = APIRouter(prefix="/api/profile", tags=["profile"])


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    username: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    riding_since: Optional[date] = None
    license_type: Optional[str] = Field(None, max_length=50)


class UpdateSettingsRequest(BaseModel):
    preferred_language: Optional[str] = None
    distance_unit: Optional[str] = None
    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None


class MotorcycleResponse(BaseModel):
    id: UUID
    brand: str
    model: str
    year: Optional[int] = None
    cc: int
    type: str
    color: Optional[str] = None
    nickname: Optional[str] = None
    is_active: bool = True
    is_primary: bool = False
    total_km: int = 0
    total_routes: int = 0

    model_config = {"from_attributes": True}


class CreateMotorcycleRequest(BaseModel):
    brand: str = Field(..., max_length=100)
    model: str = Field(..., max_length=100)
    cc: int = Field(..., gt=0, le=3000)
    type: str
    year: Optional[int] = Field(None, ge=1900, le=2030)
    color: Optional[str] = Field(None, max_length=50)
    nickname: Optional[str] = Field(None, max_length=100)
    license_plate: Optional[str] = Field(None, max_length=20)
    is_primary: bool = False


class UpdateMotorcycleRequest(BaseModel):
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    cc: Optional[int] = Field(None, gt=0, le=3000)
    type: Optional[str] = None
    year: Optional[int] = Field(None, ge=1900, le=2030)
    color: Optional[str] = Field(None, max_length=50)
    nickname: Optional[str] = Field(None, max_length=100)
    is_primary: Optional[bool] = None


class ProfileResponse(BaseModel):
    user: UserResponse
    motorcycles: List[MotorcycleResponse]
    statistics: dict


@router.get("", response_model=ProfileResponse)
async def get_profile(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile_service = ProfileService(db)
    moto_service = MotorcycleService(db)
    profile = await profile_service.get_profile(user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    motorcycles = await moto_service.get_motorcycles(user.id)
    stats = await profile_service.get_statistics(user.id)
    return ProfileResponse(
        user=UserResponse.model_validate(profile),
        motorcycles=[MotorcycleResponse.model_validate(m) for m in motorcycles],
        statistics=stats,
    )


@router.patch("", response_model=UserResponse)
async def update_profile(request: UpdateProfileRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile_service = ProfileService(db)
    try:
        updated = await profile_service.update_profile(user.id, **request.model_dump(exclude_none=True))
        return UserResponse.model_validate(updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/settings", response_model=UserResponse)
async def update_settings(request: UpdateSettingsRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile_service = ProfileService(db)
    try:
        updated = await profile_service.update_settings(user.id, **request.model_dump(exclude_none=True))
        return UserResponse.model_validate(updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/motorcycles", response_model=List[MotorcycleResponse])
async def get_motorcycles(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    moto_service = MotorcycleService(db)
    motorcycles = await moto_service.get_motorcycles(user.id)
    return [MotorcycleResponse.model_validate(m) for m in motorcycles]


@router.post("/motorcycles", response_model=MotorcycleResponse, status_code=status.HTTP_201_CREATED)
async def create_motorcycle(request: CreateMotorcycleRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    moto_service = MotorcycleService(db)
    try:
        moto_type = MotorcycleType(request.type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid motorcycle type: {request.type}")
    motorcycle = await moto_service.create_motorcycle(
        user_id=user.id,
        brand=request.brand,
        model=request.model,
        cc=request.cc,
        type=moto_type,
        year=request.year,
        color=request.color,
        nickname=request.nickname,
        license_plate=request.license_plate,
        is_primary=request.is_primary,
    )
    return MotorcycleResponse.model_validate(motorcycle)


@router.patch("/motorcycles/{motorcycle_id}", response_model=MotorcycleResponse)
async def update_motorcycle(motorcycle_id: UUID, request: UpdateMotorcycleRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    moto_service = MotorcycleService(db)
    kwargs = request.model_dump(exclude_none=True)
    if "type" in kwargs:
        try:
            kwargs["type"] = MotorcycleType(kwargs["type"])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid motorcycle type")
    motorcycle = await moto_service.update_motorcycle(motorcycle_id, user.id, **kwargs)
    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    return MotorcycleResponse.model_validate(motorcycle)


@router.delete("/motorcycles/{motorcycle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_motorcycle(motorcycle_id: UUID, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    moto_service = MotorcycleService(db)
    deleted = await moto_service.delete_motorcycle(motorcycle_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Motorcycle not found")


@router.post("/motorcycles/{motorcycle_id}/set-primary", response_model=MotorcycleResponse)
async def set_primary(motorcycle_id: UUID, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    moto_service = MotorcycleService(db)
    motorcycle = await moto_service.set_primary(motorcycle_id, user.id)
    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    return MotorcycleResponse.model_validate(motorcycle)
"""Road reports API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.routes.auth import get_current_user
from api.services.road_reports import RoadReportService
from api.services.gamification import GamificationService
from api.models.road_report import ReportCategory, ReportType, ReportSeverity

router = APIRouter(prefix="/api/reports", tags=["road-reports"])


class ReportResponse(BaseModel):
    id: UUID
    reporter_id: Optional[UUID] = None
    latitude: float
    longitude: float
    location_name: Optional[str] = None
    road_name: Optional[str] = None
    category: str
    type: str
    severity: str
    title: Optional[str] = None
    description: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    affects_direction: str = "both"
    upvote_count: int = 0
    downvote_count: int = 0
    verification_score: float = 0
    is_verified: bool = False
    is_resolved: bool = False
    created_at: datetime
    model_config = {"from_attributes": True}


class CreateReportRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    category: str
    type: str
    severity: str = "medium"
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    photo_urls: Optional[List[str]] = None
    location_name: Optional[str] = None
    road_name: Optional[str] = None
    affects_direction: str = "both"
    anonymous: bool = False


class VoteRequest(BaseModel):
    is_upvote: bool


@router.get("", response_model=List[ReportResponse])
async def get_reports_in_area(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, ge=0.1, le=50),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    svc = RoadReportService(db)
    categories = [ReportCategory(category)] if category else None
    reports = await svc.get_reports_in_area(lat, lng, radius_km, categories)
    return [ReportResponse.model_validate(r) for r in reports]


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    request: CreateReportRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = RoadReportService(db)
    try:
        cat = ReportCategory(request.category)
        rt = ReportType(request.type)
        sev = ReportSeverity(request.severity)
    except ValueError as e:
        raise HTTPException(400, str(e))

    report = await svc.create_report(
        reporter_id=user.id, latitude=request.latitude, longitude=request.longitude,
        category=cat, report_type=rt, severity=sev,
        title=request.title, description=request.description,
        photo_urls=request.photo_urls, location_name=request.location_name,
        road_name=request.road_name, affects_direction=request.affects_direction,
        anonymous=request.anonymous,
    )

    try:
        gam = GamificationService(db)
        await gam.award_points(user.id, 5, "report_submitted", "reports", "report", report.id)
    except Exception:
        pass

    return ReportResponse.model_validate(report)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = RoadReportService(db)
    report = await svc.get_report(report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    return ReportResponse.model_validate(report)


@router.post("/{report_id}/vote", response_model=ReportResponse)
async def vote_report(
    report_id: UUID,
    request: VoteRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = RoadReportService(db)
    try:
        report = await svc.vote_report(report_id, user.id, request.is_upvote)
        return ReportResponse.model_validate(report)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/{report_id}/resolve", response_model=ReportResponse)
async def resolve_report(
    report_id: UUID,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = RoadReportService(db)
    try:
        report = await svc.resolve_report(report_id, user.id)
        return ReportResponse.model_validate(report)
    except ValueError as e:
        raise HTTPException(404, str(e))
"""Route preview compatibility endpoints."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.services.route_preview import RoutePreviewService

router = APIRouter(prefix="/api/route", tags=["route"])


class LatLngResponse(BaseModel):
    lat: float
    lng: float


class ModeStatsResponse(BaseModel):
    mesafe_m: int
    sure_s: int
    viraj_fun: int
    viraj_tehlike: int
    yuksek_risk: int
    ortalama_egim: float
    serit_paylasimi: int
    ucretli: bool


class RouteModeResponse(BaseModel):
    coordinates: list[LatLngResponse]
    stats: ModeStatsResponse


class GoogleStatsResponse(BaseModel):
    mesafe_m: int
    sure_s: int
    mesafe_text: str
    sure_text: str


class RoutePreviewResponse(BaseModel):
    origin: LatLngResponse
    destination: LatLngResponse
    origin_label: str
    destination_label: str
    google_route: list[LatLngResponse]
    google_stats: GoogleStatsResponse
    modes: Dict[str, RouteModeResponse]
    feature_overlays: Dict[str, Any] | None = None


class RoutePreviewInfoResponse(BaseModel):
    has_real_data: bool
    source: str
    path: Optional[str] = None
    note: str


@router.get("", response_model=RoutePreviewResponse)
async def get_route_preview():
    svc = RoutePreviewService()
    try:
        return RoutePreviewResponse.model_validate(svc.get_route_payload())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Route payload not found")
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"Route payload error: {exc}")


@router.get("/info", response_model=RoutePreviewInfoResponse)
async def get_route_preview_info():
    svc = RoutePreviewService()
    return RoutePreviewInfoResponse.model_validate(svc.get_route_info())
"""File upload API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List

from api.routes.auth import get_current_user
from api.services.storage import storage

router = APIRouter(prefix="/api/upload", tags=["upload"])


class UploadResponse:
    def __init__(self, url: str):
        self.url = url


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = "general",
    user=Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    contents = await file.read()
    try:
        url = await storage.upload(
            file_bytes=contents,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            user_id=str(user.id),
            folder=folder,
        )
        return {"url": url}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/multiple")
async def upload_multiple(
    files: List[UploadFile] = File(...),
    folder: str = "general",
    user=Depends(get_current_user),
):
    if len(files) > 10:
        raise HTTPException(400, "Maximum 10 files per upload")

    urls = []
    for f in files:
        if not f.filename:
            continue
        contents = await f.read()
        try:
            url = await storage.upload(
                file_bytes=contents,
                filename=f.filename,
                content_type=f.content_type or "application/octet-stream",
                user_id=str(user.id),
                folder=folder,
            )
            urls.append(url)
        except ValueError:
            continue

    return {"urls": urls, "count": len(urls)}
"""Weather API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter(prefix="/api/weather", tags=["weather"])


class WeatherResponse(BaseModel):
    condition: str
    temperature_celsius: float
    humidity_percent: float
    wind_speed_ms: float
    wind_gust_ms: Optional[float] = None
    visibility_meters: int
    precipitation_mm: float


class RoadConditionResponse(BaseModel):
    surface_condition: str
    overall_safety_score: float = Field(..., ge=0, le=1)
    lane_splitting_modifier: float = Field(..., ge=0, le=1)
    grip_factor: float = Field(..., ge=0, le=1)
    visibility_factor: float = Field(..., ge=0, le=1)
    wind_risk_factor: float = Field(..., ge=0, le=1)
    warnings: List[str] = []
    weather: WeatherResponse


@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
):
    try:
        from motomap.weather import WeatherService, WeatherConfig
        config = WeatherConfig.from_env()
        async with WeatherService(config) as service:
            weather = await service.get_weather(lat, lng)
            return WeatherResponse(
                condition=weather.condition.value,
                temperature_celsius=weather.temperature_celsius,
                humidity_percent=weather.humidity_percent,
                wind_speed_ms=weather.wind_speed_ms,
                wind_gust_ms=weather.wind_gust_ms,
                visibility_meters=weather.visibility_meters,
                precipitation_mm=weather.precipitation_mm,
            )
    except ImportError:
        raise HTTPException(status_code=501, detail="Weather module not available")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Weather service error: {str(e)}")


@router.get("/road-conditions", response_model=RoadConditionResponse)
async def get_road_conditions(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
):
    try:
        from motomap.weather import WeatherService, RoadConditionAssessor, WeatherConfig
        config = WeatherConfig.from_env()
        async with WeatherService(config) as service:
            weather = await service.get_weather(lat, lng)
            assessor = RoadConditionAssessor(config)
            assessment = assessor.assess(weather)
            return RoadConditionResponse(
                surface_condition=assessment.surface_condition.value,
                overall_safety_score=assessment.overall_safety_score,
                lane_splitting_modifier=assessment.lane_splitting_modifier,
                grip_factor=assessment.grip_factor,
                visibility_factor=assessment.visibility_factor,
                wind_risk_factor=assessment.wind_risk_factor,
                warnings=assessment.warnings,
                weather=WeatherResponse(
                    condition=weather.condition.value,
                    temperature_celsius=weather.temperature_celsius,
                    humidity_percent=weather.humidity_percent,
                    wind_speed_ms=weather.wind_speed_ms,
                    wind_gust_ms=weather.wind_gust_ms,
                    visibility_meters=weather.visibility_meters,
                    precipitation_mm=weather.precipitation_mm,
                ),
            )
    except ImportError:
        raise HTTPException(status_code=501, detail="Weather module not available")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Weather service error: {str(e)}")
"""Core utilities package."""
"""Redis cache layer with in-memory fallback."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


class CacheBackend:
    def __init__(self, url: str = REDIS_URL, prefix: str = "motomap:"):
        self._url = url
        self._prefix = prefix
        self._redis: Optional[Any] = None
        self._use_redis = REDIS_AVAILABLE
        self._memory: dict[str, tuple[str, float]] = {}

    async def connect(self) -> None:
        if not self._use_redis:
            logger.info("Redis not available, using in-memory cache")
            return
        try:
            self._redis = aioredis.from_url(self._url, decode_responses=True)
            await self._redis.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning("Redis connect failed, falling back to memory: %s", e)
            self._use_redis = False
            self._redis = None

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()
            self._redis = None

    def _key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    async def get(self, key: str) -> Optional[str]:
        fk = self._key(key)
        if self._redis:
            try:
                return await self._redis.get(fk)
            except Exception:
                pass
        if fk in self._memory:
            val, exp = self._memory[fk]
            if datetime.now(timezone.utc).timestamp() < exp:
                return val
            del self._memory[fk]
        return None

    async def set(self, key: str, value: str, ttl: int = 300) -> None:
        fk = self._key(key)
        if self._redis:
            try:
                await self._redis.setex(fk, ttl, value)
                return
            except Exception:
                pass
        self._memory[fk] = (value, datetime.now(timezone.utc).timestamp() + ttl)
        if len(self._memory) > 5000:
            self._evict()

    async def delete(self, key: str) -> None:
        fk = self._key(key)
        if self._redis:
            try:
                await self._redis.delete(fk)
            except Exception:
                pass
        self._memory.pop(fk, None)

    async def get_json(self, key: str) -> Optional[Any]:
        raw = await self.get(key)
        return json.loads(raw) if raw else None

    async def set_json(self, key: str, value: Any, ttl: int = 300) -> None:
        await self.set(key, json.dumps(value, default=str), ttl)

    def _evict(self) -> None:
        now = datetime.now(timezone.utc).timestamp()
        expired = [k for k, (_, exp) in self._memory.items() if exp < now]
        for k in expired:
            del self._memory[k]
        if len(self._memory) > 5000:
            oldest = sorted(self._memory, key=lambda k: self._memory[k][1])
            for k in oldest[:1000]:
                del self._memory[k]


cache = CacheBackend()
"""Security utilities for password hashing and JWT tokens."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import os
import secrets
import hashlib

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel

SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    type: str
    jti: Optional[str] = None


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def create_access_token(
    user_id: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    user_id: str,
    expires_delta: Optional[timedelta] = None,
) -> Tuple[str, str]:
    jti = secrets.token_urlsafe(32)
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "jti": jti,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti


def decode_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(
            sub=payload["sub"],
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            type=payload.get("type", "access"),
            jti=payload.get("jti"),
        )
    except JWTError:
        return None


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
"""Middleware package."""
"""Request logging middleware with timing."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("api.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if not client_ip and request.client:
            client_ip = request.client.host

        try:
            response = await call_next(request)
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            logger.error(
                "[%s] %s %s %s -> 500 (%.1fms)",
                request_id, client_ip, request.method, request.url.path, elapsed,
            )
            raise

        elapsed = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id

        log_fn = logger.info if response.status_code < 400 else logger.warning
        if response.status_code >= 500:
            log_fn = logger.error

        log_fn(
            "[%s] %s %s %s -> %d (%.1fms)",
            request_id, client_ip, request.method, request.url.path,
            response.status_code, elapsed,
        )

        return response
"""Token-bucket rate limiting middleware."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

DEFAULT_RATE = 60       # requests
DEFAULT_WINDOW = 60     # seconds
AUTH_RATE = 10          # login/register attempts
AUTH_WINDOW = 60

ROUTE_LIMITS: dict[str, tuple[int, int]] = {
    "/api/auth/login": (AUTH_RATE, AUTH_WINDOW),
    "/api/auth/register": (AUTH_RATE, AUTH_WINDOW),
    "/api/auth/refresh": (20, 60),
    "/api/weather/current": (30, 60),
    "/api/weather/road-conditions": (30, 60),
    "/api/reports": (30, 60),
}


class _TokenBucket:
    __slots__ = ("rate", "window", "tokens", "last_refill")

    def __init__(self, rate: int, window: int):
        self.rate = rate
        self.window = window
        self.tokens = float(rate)
        self.last_refill = time.monotonic()

    def consume(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.rate, self.tokens + elapsed * (self.rate / self.window))
        self.last_refill = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    @property
    def retry_after(self) -> int:
        return max(1, int((1 - self.tokens) * (self.window / self.rate)))


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, default_rate: int = DEFAULT_RATE, default_window: int = DEFAULT_WINDOW):
        super().__init__(app)
        self._default_rate = default_rate
        self._default_window = default_window
        self._buckets: dict[str, _TokenBucket] = {}
        self._last_cleanup = time.monotonic()

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _get_bucket_key(self, ip: str, path: str) -> str:
        for prefix, _ in ROUTE_LIMITS.items():
            if path.startswith(prefix):
                return f"{ip}:{prefix}"
        return f"{ip}:default"

    def _get_limits(self, path: str) -> tuple[int, int]:
        for prefix, limits in ROUTE_LIMITS.items():
            if path.startswith(prefix):
                return limits
        return self._default_rate, self._default_window

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        ip = self._get_client_ip(request)
        key = self._get_bucket_key(ip, request.url.path)
        rate, window = self._get_limits(request.url.path)

        if key not in self._buckets:
            self._buckets[key] = _TokenBucket(rate, window)

        bucket = self._buckets[key]
        if not bucket.consume():
            logger.warning("Rate limit hit: %s on %s", ip, request.url.path)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(bucket.retry_after)},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate)
        response.headers["X-RateLimit-Remaining"] = str(int(bucket.tokens))

        if time.monotonic() - self._last_cleanup > 300:
            self._cleanup()

        return response

    def _cleanup(self) -> None:
        now = time.monotonic()
        stale = [k for k, b in self._buckets.items() if now - b.last_refill > b.window * 2]
        for k in stale:
            del self._buckets[k]
        self._last_cleanup = now
"""Services package."""
"""Authentication service."""

from __future__ import annotations

import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.user import User
from api.models.session import UserSession
from api.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_refresh_token,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

logger = logging.getLogger(__name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
PASSWORD_RESET_EXPIRE_HOURS = 1


class AuthError(Exception):
    pass


class InvalidCredentialsError(AuthError):
    pass


class UserExistsError(AuthError):
    pass


class InvalidTokenError(AuthError):
    pass


class PasswordResetError(AuthError):
    pass


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(
        self,
        email: str,
        password: str,
        display_name: Optional[str] = None,
    ) -> User:
        existing = await self.get_user_by_email(email)
        if existing:
            raise UserExistsError(f"User with email {email} already exists")

        user = User(
            email=email.lower().strip(),
            password_hash=hash_password(password),
            display_name=display_name,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def login(
        self,
        email: str,
        password: str,
        device_info: Optional[dict] = None,
    ) -> Tuple[User, str, str]:
        user = await self.get_user_by_email(email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_active:
            raise InvalidCredentialsError("Account is disabled")

        access_token = create_access_token(str(user.id))
        refresh_token, jti = create_refresh_token(str(user.id))

        session = UserSession(
            user_id=user.id,
            refresh_token_hash=hash_refresh_token(refresh_token),
            device_id=device_info.get("device_id") if device_info else None,
            device_name=device_info.get("device_name") if device_info else None,
            device_type=device_info.get("device_type") if device_info else None,
            app_version=device_info.get("app_version") if device_info else None,
            ip_address=device_info.get("ip_address") if device_info else None,
            user_agent=device_info.get("user_agent") if device_info else None,
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(session)
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.commit()
        return user, access_token, refresh_token

    async def logout(self, refresh_token: str) -> bool:
        token_hash = hash_refresh_token(refresh_token)
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.refresh_token_hash == token_hash,
                UserSession.is_active == True,
            )
        )
        session = result.scalar_one_or_none()
        if session:
            session.is_active = False
            await self.db.commit()
            return True
        return False

    async def logout_all(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
            )
        )
        sessions = result.scalars().all()
        count = 0
        for session in sessions:
            session.is_active = False
            count += 1
        await self.db.commit()
        return count

    async def refresh_tokens(self, refresh_token: str) -> Tuple[str, str]:
        payload = decode_token(refresh_token)
        if not payload or payload.type != "refresh":
            raise InvalidTokenError("Invalid refresh token")

        token_hash = hash_refresh_token(refresh_token)
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.refresh_token_hash == token_hash,
                UserSession.is_active == True,
            )
        )
        session = result.scalar_one_or_none()
        if not session or session.expires_at < datetime.now(timezone.utc):
            raise InvalidTokenError("Refresh token expired or invalid")

        user_id = payload.sub
        new_access_token = create_access_token(user_id)
        new_refresh_token, new_jti = create_refresh_token(user_id)

        session.refresh_token_hash = hash_refresh_token(new_refresh_token)
        session.last_used_at = datetime.now(timezone.utc)
        session.expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        await self.db.commit()
        return new_access_token, new_refresh_token

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> bool:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise InvalidCredentialsError("User not found")
        if not verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError("Current password is incorrect")
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        await self.logout_all(user_id)
        await self.db.commit()
        return True

    # ---- Forgot / Reset Password ----

    async def create_password_reset_token(self, email: str) -> Optional[str]:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        token = secrets.token_urlsafe(48)
        user.password_reset_token = token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(
            hours=PASSWORD_RESET_EXPIRE_HOURS
        )
        await self.db.commit()
        logger.info("Password reset token created for %s: %s", email, token)
        return token

    async def reset_password_with_token(self, token: str, new_password: str) -> bool:
        result = await self.db.execute(
            select(User).where(User.password_reset_token == token)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise PasswordResetError("Invalid or expired reset token")
        if (
            not user.password_reset_expires
            or user.password_reset_expires < datetime.now(timezone.utc)
        ):
            user.password_reset_token = None
            user.password_reset_expires = None
            await self.db.commit()
            raise PasswordResetError("Reset token has expired")

        user.password_hash = hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.updated_at = datetime.now(timezone.utc)
        await self.logout_all(user.id)
        await self.db.commit()
        return True

    # ---- Google OAuth ----

    async def google_login(
        self, id_token: str, device_info: Optional[dict] = None
    ) -> Tuple[User, str, str]:
        google_user = await self._verify_google_token(id_token)
        if not google_user:
            raise InvalidCredentialsError("Invalid Google token")

        google_id = google_user["sub"]
        email = google_user.get("email", "").lower().strip()
        display_name = google_user.get("name")

        result = await self.db.execute(
            select(User).where(User.google_id == google_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            user = await self.get_user_by_email(email)
            if user:
                user.google_id = google_id
                if not user.display_name and display_name:
                    user.display_name = display_name
                if not user.avatar_url and google_user.get("picture"):
                    user.avatar_url = google_user["picture"]
                await self.db.commit()
            else:
                user = User(
                    email=email,
                    password_hash=hash_password(secrets.token_urlsafe(32)),
                    display_name=display_name,
                    avatar_url=google_user.get("picture"),
                    google_id=google_id,
                    auth_provider="google",
                    email_verified=True,
                )
                self.db.add(user)
                await self.db.commit()
                await self.db.refresh(user)

        if not user.is_active:
            raise InvalidCredentialsError("Account is disabled")

        access_token = create_access_token(str(user.id))
        refresh_token, _jti = create_refresh_token(str(user.id))

        session = UserSession(
            user_id=user.id,
            refresh_token_hash=hash_refresh_token(refresh_token),
            device_id=device_info.get("device_id") if device_info else None,
            device_name=device_info.get("device_name") if device_info else None,
            device_type=device_info.get("device_type") if device_info else None,
            ip_address=device_info.get("ip_address") if device_info else None,
            user_agent=device_info.get("user_agent") if device_info else None,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(session)
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.commit()
        return user, access_token, refresh_token

    @staticmethod
    async def _verify_google_token(id_token: str) -> Optional[dict]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    GOOGLE_TOKENINFO_URL, params={"id_token": id_token}
                )
                if resp.status_code != 200:
                    return None
                data = resp.json()
                if GOOGLE_CLIENT_ID and data.get("aud") != GOOGLE_CLIENT_ID:
                    logger.warning("Google token aud mismatch")
                    return None
                if data.get("email_verified") != "true":
                    return None
                return data
        except Exception as exc:
            logger.error("Google token verification failed: %s", exc)
            return None
"""Community management service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.models.community import (
    Community, CommunityMembership, CommunityPost, PostComment,
    CommunityType, MembershipRole, PostType,
)


class CommunityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_communities(
        self,
        community_type: Optional[CommunityType] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Community]:
        query = select(Community)
        if community_type:
            query = query.where(Community.type == community_type)
        if search:
            query = query.where(Community.name.ilike(f"%{search}%"))
        query = query.order_by(Community.member_count.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_community(self, slug: str) -> Optional[Community]:
        result = await self.db.execute(
            select(Community).where(Community.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_community_by_id(self, community_id: UUID) -> Optional[Community]:
        result = await self.db.execute(
            select(Community).where(Community.id == community_id)
        )
        return result.scalar_one_or_none()

    async def create_community(
        self,
        name: str,
        slug: str,
        community_type: CommunityType,
        created_by: UUID,
        description: Optional[str] = None,
        brand_name: Optional[str] = None,
        region_city: Optional[str] = None,
        region_country: Optional[str] = None,
        color: Optional[str] = None,
    ) -> Community:
        community = Community(
            name=name, slug=slug, type=community_type,
            created_by=created_by, description=description,
            brand_name=brand_name, region_city=region_city,
            region_country=region_country, color=color,
            member_count=1,
        )
        self.db.add(community)
        await self.db.flush()

        membership = CommunityMembership(
            community_id=community.id, user_id=created_by, role=MembershipRole.OWNER,
        )
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(community)
        return community

    async def join_community(self, community_id: UUID, user_id: UUID) -> CommunityMembership:
        existing = await self.db.execute(
            select(CommunityMembership).where(
                CommunityMembership.community_id == community_id,
                CommunityMembership.user_id == user_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Already a member")

        community = await self.get_community_by_id(community_id)
        if not community:
            raise ValueError("Community not found")

        membership = CommunityMembership(
            community_id=community_id, user_id=user_id,
            is_approved=not community.requires_approval,
        )
        self.db.add(membership)
        community.member_count += 1
        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    async def leave_community(self, community_id: UUID, user_id: UUID) -> bool:
        result = await self.db.execute(
            select(CommunityMembership).where(
                CommunityMembership.community_id == community_id,
                CommunityMembership.user_id == user_id,
            )
        )
        membership = result.scalar_one_or_none()
        if not membership:
            return False
        if membership.role == MembershipRole.OWNER:
            raise ValueError("Owner cannot leave. Transfer ownership first.")

        await self.db.delete(membership)
        community = await self.get_community_by_id(community_id)
        if community:
            community.member_count = max(0, community.member_count - 1)
        await self.db.commit()
        return True

    async def get_user_communities(self, user_id: UUID) -> List[Community]:
        result = await self.db.execute(
            select(Community)
            .join(CommunityMembership)
            .where(CommunityMembership.user_id == user_id, CommunityMembership.is_banned == False)
            .order_by(CommunityMembership.is_favorite.desc(), CommunityMembership.joined_at.desc())
        )
        return list(result.scalars().all())

    async def get_membership(self, community_id: UUID, user_id: UUID) -> Optional[CommunityMembership]:
        result = await self.db.execute(
            select(CommunityMembership).where(
                CommunityMembership.community_id == community_id,
                CommunityMembership.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    # Posts
    async def create_post(
        self,
        community_id: UUID,
        author_id: UUID,
        content: str,
        post_type: PostType = PostType.DISCUSSION,
        title: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
        location_lat: Optional[float] = None,
        location_lng: Optional[float] = None,
        location_name: Optional[str] = None,
    ) -> CommunityPost:
        membership = await self.get_membership(community_id, author_id)
        if not membership or membership.is_banned:
            raise ValueError("Not a member or banned")

        post = CommunityPost(
            community_id=community_id, author_id=author_id,
            type=post_type, title=title, content=content,
            image_urls=image_urls or [], location_lat=location_lat,
            location_lng=location_lng, location_name=location_name,
        )
        self.db.add(post)

        community = await self.get_community_by_id(community_id)
        if community:
            community.post_count += 1

        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def get_posts(
        self,
        community_id: UUID,
        post_type: Optional[PostType] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[CommunityPost]:
        query = (
            select(CommunityPost)
            .where(CommunityPost.community_id == community_id, CommunityPost.is_deleted == False)
        )
        if post_type:
            query = query.where(CommunityPost.type == post_type)
        query = query.order_by(CommunityPost.is_pinned.desc(), CommunityPost.created_at.desc())
        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_post(self, post_id: UUID) -> Optional[CommunityPost]:
        result = await self.db.execute(
            select(CommunityPost).where(CommunityPost.id == post_id)
        )
        return result.scalar_one_or_none()

    async def delete_post(self, post_id: UUID, user_id: UUID) -> bool:
        post = await self.get_post(post_id)
        if not post:
            return False
        if post.author_id != user_id:
            membership = await self.get_membership(post.community_id, user_id)
            if not membership or membership.role not in (MembershipRole.ADMIN, MembershipRole.OWNER, MembershipRole.MODERATOR):
                raise ValueError("Not authorized")
        post.is_deleted = True
        await self.db.commit()
        return True

    # Comments
    async def create_comment(
        self,
        post_id: UUID,
        author_id: UUID,
        content: str,
        parent_id: Optional[UUID] = None,
    ) -> PostComment:
        post = await self.get_post(post_id)
        if not post or post.is_deleted or post.is_locked:
            raise ValueError("Post not found or locked")

        comment = PostComment(
            post_id=post_id, author_id=author_id,
            content=content, parent_id=parent_id,
        )
        self.db.add(comment)
        post.comment_count += 1
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def get_comments(self, post_id: UUID, limit: int = 50) -> List[PostComment]:
        result = await self.db.execute(
            select(PostComment)
            .where(PostComment.post_id == post_id, PostComment.is_deleted == False)
            .order_by(PostComment.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def seed_defaults(self) -> int:
        defaults = [
            {"name": "Harley-Davidson Turkiye", "slug": "harley-davidson-tr", "type": CommunityType.BRAND, "brand_name": "Harley-Davidson", "is_official": True},
            {"name": "Honda Riders Turkey", "slug": "honda-tr", "type": CommunityType.BRAND, "brand_name": "Honda", "is_official": True},
            {"name": "Yamaha Turkiye", "slug": "yamaha-tr", "type": CommunityType.BRAND, "brand_name": "Yamaha", "is_official": True},
            {"name": "Kawasaki Turkiye", "slug": "kawasaki-tr", "type": CommunityType.BRAND, "brand_name": "Kawasaki", "is_official": True},
            {"name": "BMW Motorrad Turkiye", "slug": "bmw-tr", "type": CommunityType.BRAND, "brand_name": "BMW", "is_official": True},
            {"name": "Ducati Turkiye", "slug": "ducati-tr", "type": CommunityType.BRAND, "brand_name": "Ducati", "is_official": True},
            {"name": "KTM Turkiye", "slug": "ktm-tr", "type": CommunityType.BRAND, "brand_name": "KTM", "is_official": True},
            {"name": "Suzuki Turkiye", "slug": "suzuki-tr", "type": CommunityType.BRAND, "brand_name": "Suzuki", "is_official": True},
            {"name": "Sport Bike Turkiye", "slug": "sport-tr", "type": CommunityType.STYLE, "description": "Sport motosiklet tutkunlari"},
            {"name": "Touring Turkiye", "slug": "touring-tr", "type": CommunityType.STYLE, "description": "Uzun yol ve tur motosikletcileri"},
            {"name": "Adventure Riders TR", "slug": "adventure-tr", "type": CommunityType.STYLE, "description": "Macera ve arazi motosikletcileri"},
            {"name": "Cafe Racer Turkiye", "slug": "cafe-racer-tr", "type": CommunityType.STYLE, "description": "Cafe racer tutkunlari"},
            {"name": "Istanbul Motorculari", "slug": "istanbul", "type": CommunityType.REGION, "region_city": "Istanbul", "region_country": "Turkey"},
            {"name": "Ankara Motorculari", "slug": "ankara", "type": CommunityType.REGION, "region_city": "Ankara", "region_country": "Turkey"},
            {"name": "Izmir Motorculari", "slug": "izmir", "type": CommunityType.REGION, "region_city": "Izmir", "region_country": "Turkey"},
            {"name": "Antalya Motorculari", "slug": "antalya", "type": CommunityType.REGION, "region_city": "Antalya", "region_country": "Turkey"},
            {"name": "Yeni Baslayanlar", "slug": "yeni-baslayanlar", "type": CommunityType.INTEREST, "description": "Motosiklete yeni baslayanlar icin"},
            {"name": "Track Day Turkiye", "slug": "track-day-tr", "type": CommunityType.INTEREST, "description": "Pist gunu etkinlikleri"},
        ]
        count = 0
        for d in defaults:
            existing = await self.db.execute(select(Community).where(Community.slug == d["slug"]))
            if not existing.scalar_one_or_none():
                self.db.add(Community(**d, is_public=True))
                count += 1
        await self.db.commit()
        return count
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
"""Notification service."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional, List, Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.notification import Notification, PushToken, NotificationType

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Optional[dict] = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id, type=notification_type,
            title=title, body=body, data=data,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)

        # Fire-and-forget push (best effort)
        try:
            await self._send_push(user_id, title, body, data)
        except Exception as e:
            logger.warning("Push send failed for user %s: %s", user_id, e)

        return notification

    async def get_notifications(
        self, user_id: UUID, unread_only: bool = False, limit: int = 50, offset: int = 0,
    ) -> List[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.is_read == False)
        query = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
        )
        return len(result.scalars().all())

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> bool:
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id, Notification.user_id == user_id,
            )
        )
        notif = result.scalar_one_or_none()
        if not notif:
            return False
        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
        await self.db.commit()
        return True

    async def mark_all_read(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id, Notification.is_read == False,
            )
        )
        notifs = result.scalars().all()
        for n in notifs:
            n.is_read = True
            n.read_at = datetime.now(timezone.utc)
        await self.db.commit()
        return len(notifs)

    async def register_push_token(
        self, user_id: UUID, token: str, device_type: str,
    ) -> PushToken:
        existing = await self.db.execute(
            select(PushToken).where(PushToken.user_id == user_id, PushToken.token == token)
        )
        pt = existing.scalar_one_or_none()
        if pt:
            pt.is_active = True
            await self.db.commit()
            return pt

        pt = PushToken(user_id=user_id, token=token, device_type=device_type)
        self.db.add(pt)
        await self.db.commit()
        await self.db.refresh(pt)
        return pt

    async def unregister_push_token(self, user_id: UUID, token: str) -> bool:
        result = await self.db.execute(
            select(PushToken).where(PushToken.user_id == user_id, PushToken.token == token)
        )
        pt = result.scalar_one_or_none()
        if not pt:
            return False
        pt.is_active = False
        await self.db.commit()
        return True

    async def _send_push(
        self, user_id: UUID, title: str, body: str, data: Optional[dict] = None,
    ) -> None:
        """Send push notification via Expo Push API. Best-effort, no retry."""
        result = await self.db.execute(
            select(PushToken).where(PushToken.user_id == user_id, PushToken.is_active == True)
        )
        tokens = [pt.token for pt in result.scalars().all()]
        if not tokens:
            return

        import httpx
        messages = [
            {"to": t, "title": title, "body": body, "data": data or {}}
            for t in tokens
        ]
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    "https://exp.host/--/api/v2/push/send",
                    json=messages,
                    headers={"Content-Type": "application/json"},
                )
        except Exception as e:
            logger.debug("Expo push failed: %s", e)
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
"""Canonical route preview payload service.

This keeps `/api/route` on the main backend while the live route-generation
API is being integrated. It prefers generated route JSON when available and
falls back to a bundled demo payload otherwise.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

DEMO_ROUTE: dict[str, Any] = {
    "origin": {"lat": 40.9923, "lng": 29.0239},
    "destination": {"lat": 40.9700, "lng": 29.0380},
    "origin_label": "Kadikoy Iskele",
    "destination_label": "Kalamis Parki",
    "google_route": [
        {"lat": 40.9923, "lng": 29.0239},
        {"lat": 40.9915, "lng": 29.0260},
        {"lat": 40.9905, "lng": 29.0280},
        {"lat": 40.9890, "lng": 29.0295},
        {"lat": 40.9875, "lng": 29.0305},
        {"lat": 40.9860, "lng": 29.0315},
        {"lat": 40.9840, "lng": 29.0330},
        {"lat": 40.9820, "lng": 29.0345},
        {"lat": 40.9800, "lng": 29.0360},
        {"lat": 40.9780, "lng": 29.0368},
        {"lat": 40.9760, "lng": 29.0372},
        {"lat": 40.9740, "lng": 29.0376},
        {"lat": 40.9720, "lng": 29.0378},
        {"lat": 40.9700, "lng": 29.0380},
    ],
    "google_stats": {
        "mesafe_m": 2850,
        "mesafe_text": "2.9 km",
        "sure_s": 540,
        "sure_text": "9 dk",
    },
    "modes": {
        "standart": {
            "coordinates": [
                {"lat": 40.9923, "lng": 29.0239},
                {"lat": 40.9912, "lng": 29.0252},
                {"lat": 40.9900, "lng": 29.0268},
                {"lat": 40.9888, "lng": 29.0282},
                {"lat": 40.9875, "lng": 29.0298},
                {"lat": 40.9860, "lng": 29.0310},
                {"lat": 40.9845, "lng": 29.0322},
                {"lat": 40.9828, "lng": 29.0335},
                {"lat": 40.9810, "lng": 29.0348},
                {"lat": 40.9790, "lng": 29.0358},
                {"lat": 40.9770, "lng": 29.0366},
                {"lat": 40.9748, "lng": 29.0372},
                {"lat": 40.9724, "lng": 29.0377},
                {"lat": 40.9700, "lng": 29.0380},
            ],
            "stats": {
                "mesafe_m": 2780,
                "sure_s": 420,
                "viraj_fun": 4,
                "viraj_tehlike": 1,
                "yuksek_risk": 0,
                "serit_paylasimi": 1200,
                "ortalama_egim": 0.018,
                "ucretli": False,
            },
        },
        "viraj_keyfi": {
            "coordinates": [
                {"lat": 40.9923, "lng": 29.0239},
                {"lat": 40.9915, "lng": 29.0248},
                {"lat": 40.9905, "lng": 29.0255},
                {"lat": 40.9895, "lng": 29.0265},
                {"lat": 40.9882, "lng": 29.0278},
                {"lat": 40.9868, "lng": 29.0292},
                {"lat": 40.9852, "lng": 29.0305},
                {"lat": 40.9835, "lng": 29.0318},
                {"lat": 40.9818, "lng": 29.0330},
                {"lat": 40.9800, "lng": 29.0342},
                {"lat": 40.9780, "lng": 29.0352},
                {"lat": 40.9760, "lng": 29.0362},
                {"lat": 40.9738, "lng": 29.0370},
                {"lat": 40.9718, "lng": 29.0376},
                {"lat": 40.9700, "lng": 29.0380},
            ],
            "stats": {
                "mesafe_m": 3100,
                "sure_s": 510,
                "viraj_fun": 11,
                "viraj_tehlike": 2,
                "yuksek_risk": 0,
                "serit_paylasimi": 1200,
                "ortalama_egim": 0.024,
                "ucretli": False,
            },
        },
        "guvenli": {
            "coordinates": [
                {"lat": 40.9923, "lng": 29.0239},
                {"lat": 40.9910, "lng": 29.0258},
                {"lat": 40.9895, "lng": 29.0274},
                {"lat": 40.9878, "lng": 29.0288},
                {"lat": 40.9862, "lng": 29.0302},
                {"lat": 40.9845, "lng": 29.0316},
                {"lat": 40.9825, "lng": 29.0328},
                {"lat": 40.9805, "lng": 29.0340},
                {"lat": 40.9784, "lng": 29.0350},
                {"lat": 40.9762, "lng": 29.0360},
                {"lat": 40.9740, "lng": 29.0368},
                {"lat": 40.9720, "lng": 29.0374},
                {"lat": 40.9700, "lng": 29.0380},
            ],
            "stats": {
                "mesafe_m": 2680,
                "sure_s": 480,
                "viraj_fun": 2,
                "viraj_tehlike": 0,
                "yuksek_risk": 0,
                "serit_paylasimi": 1200,
                "ortalama_egim": 0.012,
                "ucretli": False,
            },
        },
    },
}


class RoutePreviewService:
    """Serve the canonical route preview payload from the main backend."""

    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]

    def iter_candidate_paths(self) -> tuple[Path, ...]:
        return (
            self.repo_root / "website" / "routes" / "motomap_route.json",
            self.repo_root / "website" / "public" / "routes" / "motomap_route.json",
            self.repo_root / "app" / "website" / "routes" / "motomap_route.json",
            self.repo_root / "app" / "website" / "public" / "routes" / "motomap_route.json",
        )

    def get_generated_route_path(self) -> Path | None:
        for candidate in self.iter_candidate_paths():
            if candidate.exists():
                return candidate
        return None

    def load_generated_route(self) -> dict[str, Any]:
        route_path = self.get_generated_route_path()
        if not route_path:
            raise FileNotFoundError("Generated route payload not found")

        with route_path.open(encoding="utf-8") as handle:
            return json.load(handle)

    def get_route_payload(self) -> dict[str, Any]:
        route_path = self.get_generated_route_path()
        if route_path:
            return self.load_generated_route()
        return deepcopy(DEMO_ROUTE)

    def get_route_info(self) -> dict[str, Any]:
        route_path = self.get_generated_route_path()
        relative_path = (
            route_path.relative_to(self.repo_root).as_posix()
            if route_path is not None
            else None
        )
        return {
            "has_real_data": route_path is not None,
            "source": "generated" if route_path is not None else "demo",
            "path": relative_path,
            "note": (
                "Run website/generate_route.py or app/website/generate_route.py "
                "to produce a generated route payload for compatibility mode."
            ),
        }
"""File upload service with local + S3 support."""

from __future__ import annotations

import hashlib
import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
S3_BUCKET = os.getenv("S3_BUCKET", "")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


class StorageService:
    def __init__(self):
        self._use_s3 = bool(S3_BUCKET)
        if not self._use_s3:
            Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    async def upload(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        user_id: str,
        folder: str = "general",
    ) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type not allowed: {ext}")
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError(f"Content type not allowed: {content_type}")
        if len(file_bytes) > MAX_FILE_SIZE:
            raise ValueError(f"File too large (max {MAX_FILE_SIZE // 1024 // 1024}MB)")

        file_hash = hashlib.md5(file_bytes).hexdigest()[:12]
        unique_name = f"{user_id}/{folder}/{file_hash}_{uuid.uuid4().hex[:8]}{ext}"

        if self._use_s3:
            return await self._upload_s3(file_bytes, unique_name, content_type)
        return await self._upload_local(file_bytes, unique_name)

    async def _upload_local(self, file_bytes: bytes, path: str) -> str:
        full_path = Path(UPLOAD_DIR) / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(file_bytes)
        return f"/uploads/{path}"

    async def _upload_s3(self, file_bytes: bytes, key: str, content_type: str) -> str:
        try:
            import boto3
            s3 = boto3.client("s3")
            s3.put_object(
                Bucket=S3_BUCKET, Key=key, Body=file_bytes,
                ContentType=content_type, ACL="public-read",
            )
            region = s3.meta.region_name or "eu-central-1"
            return f"https://{S3_BUCKET}.s3.{region}.amazonaws.com/{key}"
        except ImportError:
            logger.warning("boto3 not installed, falling back to local storage")
            return await self._upload_local(file_bytes, key)

    async def delete(self, url: str) -> bool:
        if url.startswith("/uploads/"):
            path = Path(UPLOAD_DIR) / url.replace("/uploads/", "")
            if path.exists():
                path.unlink()
                return True
        elif self._use_s3 and S3_BUCKET in url:
            try:
                import boto3
                key = url.split(f"{S3_BUCKET}.s3.")[1].split("/", 1)[1] if ".s3." in url else ""
                if key:
                    s3 = boto3.client("s3")
                    s3.delete_object(Bucket=S3_BUCKET, Key=key)
                    return True
            except Exception as e:
                logger.warning("S3 delete failed: %s", e)
        return False


storage = StorageService()
