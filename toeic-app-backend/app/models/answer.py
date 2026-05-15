from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.user import User
import uuid
import enum
from sqlalchemy import func

class QuestionType(str, enum.Enum):
    LISTENING = "listening"
    GRAMMAR = "grammar"

class AnswerRecord(Base):
    __tablename__ = "answer_records"
    
    record_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    user_answer = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Integer, nullable=False)
    answered_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    user = relationship("User", backref="answer_records")
    
    __table_args__ = (
        Index('idx_answer_user', 'user_id'),
        Index('idx_answer_question', 'question_id'),
        Index('idx_answer_time', 'answered_at'),
    )
