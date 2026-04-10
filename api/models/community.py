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
