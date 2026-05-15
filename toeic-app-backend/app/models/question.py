from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
import uuid
import enum

class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class ListeningQuestionType(str, enum.Enum):
    CONVERSATION = "conversation"
    SHORT_TALK = "short_talk"
    PHOTO_DESCRIPTION = "photo_description"

class ListeningQuestion(Base, TimestampMixin):
    __tablename__ = "listening_questions"
    
    question_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(Text, nullable=False)
    audio_url = Column(String(500), nullable=False)
    audio_duration = Column(Integer, nullable=False)
    image_url = Column(String(500), nullable=True)
    script_reference = Column(Text, nullable=True)
    options = Column(JSONB, nullable=False)
    correct_answer = Column(Integer, nullable=False)
    analysis = Column(Text, nullable=True)
    difficulty = Column(Enum(Difficulty), nullable=False)
    question_type = Column(Enum(ListeningQuestionType), nullable=False)
    
    __table_args__ = (
        CheckConstraint('audio_duration >= 5 AND audio_duration <= 120', name='check_audio_duration'),
        CheckConstraint('correct_answer >= 0 AND correct_answer <= 3', name='check_correct_answer'),
        Index('idx_listening_difficulty', 'difficulty'),
        Index('idx_listening_type', 'question_type'),
    )

class GrammarQuestion(Base, TimestampMixin):
    __tablename__ = "grammar_questions"
    
    question_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    question_mark = Column(String(200), nullable=False)
    options = Column(JSONB, nullable=False)
    correct_answer = Column(Integer, nullable=False)
    grammar_rule = Column(Text, nullable=True)
    example = Column(String(300), nullable=True)
    knowledge_point = Column(String(50), nullable=False)
    difficulty = Column(Enum(Difficulty), nullable=False)
    
    __table_args__ = (
        CheckConstraint('correct_answer >= 0 AND correct_answer <= 3', name='check_correct_answer'),
        Index('idx_grammar_difficulty', 'difficulty'),
        Index('idx_grammar_knowledge', 'knowledge_point'),
    )
