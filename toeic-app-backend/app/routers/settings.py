from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.settings_service import SettingsService
from app.schemas.schemas import (
    UserCreate, UserUpdate, UserResponse,
    PageSettingsUpdate, PageSettingsResponse
)

router = APIRouter()

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = SettingsService(db)
        user = await service.create_user(user_data)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    import uuid
    try:
        service = SettingsService(db)
        user = await service.get_user(uuid.UUID(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    import uuid
    try:
        service = SettingsService(db)
        user = await service.update_user(uuid.UUID(user_id), user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

@router.get("/page/{user_id}", response_model=PageSettingsResponse)
async def get_page_settings(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    import uuid
    try:
        service = SettingsService(db)
        settings = await service.get_page_settings(uuid.UUID(user_id))
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        return settings
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

@router.put("/page/{user_id}", response_model=PageSettingsResponse)
async def update_page_settings(
    user_id: str,
    settings_data: PageSettingsUpdate,
    db: AsyncSession = Depends(get_db)
):
    import uuid
    try:
        service = SettingsService(db)
        settings = await service.update_page_settings(uuid.UUID(user_id), settings_data)
        return settings
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")
