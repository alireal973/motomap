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
