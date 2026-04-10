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
