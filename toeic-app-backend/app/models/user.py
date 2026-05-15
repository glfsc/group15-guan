from sqlalchemy import Column, String, Text, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
import uuid

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    learning_goal = Column(Text, nullable=True)
    
    settings = relationship("PageSettings", back_populates="user", uselist=False)
    progress = relationship("Progress", back_populates="user", uselist=False)
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
    )
