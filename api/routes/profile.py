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
    weight_kg: Optional[int] = None
    torque_nm: Optional[int] = None
    tire_type: Optional[str] = None
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
    weight_kg: Optional[int] = Field(None, gt=0, le=1000)
    torque_nm: Optional[int] = Field(None, gt=0, le=500)
    tire_type: Optional[str] = Field(None, max_length=50)
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
    weight_kg: Optional[int] = Field(None, gt=0, le=1000)
    torque_nm: Optional[int] = Field(None, gt=0, le=500)
    tire_type: Optional[str] = Field(None, max_length=50)
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
        weight_kg=request.weight_kg,
        torque_nm=request.torque_nm,
        tire_type=request.tire_type,
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
