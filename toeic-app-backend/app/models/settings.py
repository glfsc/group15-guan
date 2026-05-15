from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.user import User
import uuid
import enum

class FontSize(str, enum.Enum):
    P80 = "80"
    P90 = "90"
    P100 = "100"
    P110 = "110"
    P120 = "120"
    P130 = "130"
    P150 = "150"

class BackgroundColor(str, enum.Enum):
    LIGHT = "light"
    DARK = "dark"
    EYE_CARE = "eye_care"

class PageSettings(Base):
    __tablename__ = "page_settings"
    
    setting_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    font_size = Column(String(10), default="100", nullable=False)
    background_color = Column(Enum(BackgroundColor), default=BackgroundColor.LIGHT, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", back_populates="settings")
