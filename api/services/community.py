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
