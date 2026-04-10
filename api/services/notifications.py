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
