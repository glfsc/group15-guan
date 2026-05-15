from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.answer_service import AnswerService
from app.schemas.schemas import AnswerSubmit, AnswerResult
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/submit", response_model=AnswerResult)
async def submit_answer(
    answer_data: AnswerSubmit,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AnswerService(db)
        result = await service.submit_answer(
            user_id=answer_data.user_id,
            question_id=answer_data.question_id,
            question_type=answer_data.question_type,
            user_answer=answer_data.user_answer,
            time_spent=answer_data.time_spent
        )
        return result
    except Exception as e:
        logger.exception("Failed to submit answer")
        raise HTTPException(status_code=500, detail=str(e))
