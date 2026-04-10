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
