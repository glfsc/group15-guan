from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    user_name: str
    email: EmailStr
    learning_goal: Optional[str] = None

class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    email: Optional[EmailStr] = None
    learning_goal: Optional[str] = None

class UserResponse(BaseModel):
    user_id: UUID
    user_name: str
    email: str
    learning_goal: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PageSettingsUpdate(BaseModel):
    font_size: str
    background_color: str

class PageSettingsResponse(BaseModel):
    setting_id: UUID
    user_id: UUID
    font_size: str
    background_color: str
    updated_at: datetime
    
    class Config:
        from_attributes = True

class QuestionOption(BaseModel):
    option_0: str
    option_1: str
    option_2: str
    option_3: str

class ListeningQuestionCreate(BaseModel):
    question: str
    audio_url: str
    audio_duration: int
    image_url: Optional[str] = None
    script_reference: Optional[str] = None
    options: QuestionOption
    correct_answer: int
    analysis: Optional[str] = None
    difficulty: str
    question_type: str

class ListeningQuestionResponse(BaseModel):
    question_id: UUID
    question: str
    audio_url: str
    audio_duration: int
    image_url: Optional[str] = None
    script_reference: Optional[str] = None
    options: dict
    correct_answer: int
    analysis: Optional[str]
    difficulty: str
    question_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class GrammarQuestionCreate(BaseModel):
    content: str
    question_mark: str
    options: QuestionOption
    correct_answer: int
    grammar_rule: Optional[str] = None
    example: Optional[str] = None
    knowledge_point: str
    difficulty: str

class GrammarQuestionResponse(BaseModel):
    question_id: UUID
    content: str
    question_mark: str
    options: dict
    correct_answer: int
    grammar_rule: Optional[str]
    example: Optional[str]
    knowledge_point: str
    difficulty: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    user_id: UUID
    question_id: UUID
    question_type: str
    user_answer: int
    time_spent: int

class AnswerResult(BaseModel):
    is_correct: bool
    correct_answer: int
    analysis: Optional[str]
    grammar_rule: Optional[str] = None
    example: Optional[str] = None

class ProgressResponse(BaseModel):
    user_id: UUID
    total_questions: int
    listening_questions: int
    grammar_questions: int
    overall_accuracy: float
    listening_accuracy: float
    grammar_accuracy: float
    total_practice_time: int
    listening_level: str
    grammar_level: str
    updated_at: datetime
    
    class Config:
        from_attributes = True
