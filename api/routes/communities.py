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
