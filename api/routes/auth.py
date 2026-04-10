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
