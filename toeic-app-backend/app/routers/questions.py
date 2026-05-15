from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.question_service import QuestionService
from app.schemas.schemas import ListeningQuestionResponse, GrammarQuestionResponse
from typing import List

router = APIRouter()

@router.post("/listening/generate", response_model=List[ListeningQuestionResponse])
async def generate_listening_questions(
    difficulty: str = Query(...),
    question_type: str = Query(...),
    count: int = Query(3, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = QuestionService(db)
        questions = await service.generate_listening_questions(
            difficulty=difficulty,
            question_type=question_type,
            count=count
        )
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/grammar/generate", response_model=List[GrammarQuestionResponse])
async def generate_grammar_questions(
    knowledge_point: str = Query(...),
    difficulty: str = Query(...),
    count: int = Query(3, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = QuestionService(db)
        questions = await service.generate_grammar_questions(
            knowledge_point=knowledge_point,
            difficulty=difficulty,
            count=count
        )
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/listening/{question_id}", response_model=ListeningQuestionResponse)
async def get_listening_question(
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    import uuid
    try:
        service = QuestionService(db)
        question = await service.get_listening_question(uuid.UUID(question_id))
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return question
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid question ID")

@router.get("/grammar/{question_id}", response_model=GrammarQuestionResponse)
async def get_grammar_question(
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    import uuid
    try:
        service = QuestionService(db)
        question = await service.get_grammar_question(uuid.UUID(question_id))
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return question
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid question ID")
