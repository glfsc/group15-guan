from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.settings import PageSettings, BackgroundColor
from app.schemas.schemas import UserCreate, UserUpdate, PageSettingsUpdate
import logging
import uuid

logger = logging.getLogger(__name__)

class SettingsService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        user = User(
            user_name=user_data.user_name,
            email=user_data.email,
            learning_goal=user_data.learning_goal
        )
        self.db.add(user)
        await self.db.flush()
        
        page_settings = PageSettings(user_id=user.user_id)
        self.db.add(page_settings)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_user(self, user_id: uuid.UUID) -> User:
        result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> User:
        result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if user_data.user_name is not None:
            user.user_name = user_data.user_name
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.learning_goal is not None:
            user.learning_goal = user_data.learning_goal
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_page_settings(self, user_id: uuid.UUID) -> PageSettings:
        result = await self.db.execute(
            select(PageSettings).where(PageSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_page_settings(
        self,
        user_id: uuid.UUID,
        settings_data: PageSettingsUpdate
    ) -> PageSettings:
        result = await self.db.execute(
            select(PageSettings).where(PageSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = PageSettings(
                user_id=user_id,
                font_size=settings_data.font_size,
                background_color=BackgroundColor(settings_data.background_color)
            )
            self.db.add(settings)
        else:
            settings.font_size = settings_data.font_size
            settings.background_color = BackgroundColor(settings_data.background_color)
        
        await self.db.commit()
        await self.db.refresh(settings)
        
        return settings
