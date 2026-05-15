from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.user import User
from app.models.answer import QuestionType
import uuid
import enum

class AbilityLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Progress(Base):
    __tablename__ = "progress"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    total_questions = Column(Integer, default=0, nullable=False)
    listening_questions = Column(Integer, default=0, nullable=False)
    grammar_questions = Column(Integer, default=0, nullable=False)
    overall_accuracy = Column(Float, default=0.0, nullable=False)
    listening_accuracy = Column(Float, default=0.0, nullable=False)
    grammar_accuracy = Column(Float, default=0.0, nullable=False)
    total_practice_time = Column(Integer, default=0, nullable=False)
    listening_level = Column(Enum(AbilityLevel), default=AbilityLevel.BEGINNER, nullable=False)
    grammar_level = Column(Enum(AbilityLevel), default=AbilityLevel.BEGINNER, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", back_populates="progress")

class ErrorQuestion(Base):
    __tablename__ = "error_questions"
    
    record_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    user_answer = Column(Integer, nullable=False)
    correct_answer = Column(Integer, nullable=False)
    error_count = Column(Integer, default=1, nullable=False)
    first_error_time = Column(DateTime, server_default=func.now(), nullable=False)
    last_error_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", backref="error_questions")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'question_id', name='uq_user_question'),
        Index('idx_error_user', 'user_id'),
    )
