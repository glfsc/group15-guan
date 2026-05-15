from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.stats_service import StatsService
from app.schemas.schemas import ProgressResponse
from typing import List, Dict, Any

router = APIRouter()

@router.get("/progress/{user_id}", response_model=ProgressResponse)
async def get_progress(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    import uuid
    try:
        service = StatsService(db)
        progress = await service.get_progress(uuid.UUID(user_id))
        if not progress:
            raise HTTPException(status_code=404, detail="Progress not found")
        return progress
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

@router.get("/errors/{user_id}")
async def get_error_questions(
    user_id: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    import uuid
    try:
        service = StatsService(db)
        errors = await service.get_error_questions(uuid.UUID(user_id), limit)
        return [
            {
                "record_id": str(e.record_id),
                "question_id": str(e.question_id),
                "question_type": e.question_type.value,
                "user_answer": e.user_answer,
                "correct_answer": e.correct_answer,
                "error_count": e.error_count,
                "first_error_time": e.first_error_time.isoformat(),
                "last_error_time": e.last_error_time.isoformat()
            }
            for e in errors
        ]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

@router.get("/history/{user_id}")
async def get_practice_history(
    user_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    import uuid
    try:
        service = StatsService(db)
        history = await service.get_practice_history(uuid.UUID(user_id), limit)
        return [
            {
                "record_id": str(h.record_id),
                "question_id": str(h.question_id),
                "question_type": h.question_type.value,
                "user_answer": h.user_answer,
                "is_correct": h.is_correct,
                "time_spent": h.time_spent,
                "answered_at": h.answered_at.isoformat()
            }
            for h in history
        ]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

@router.get("/daily/{user_id}")
async def get_daily_stats(
    user_id: str,
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    import uuid
    try:
        service = StatsService(db)
        stats = await service.get_daily_stats(uuid.UUID(user_id), days)
        return stats
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

@router.delete("/errors/{user_id}/{question_id}")
async def delete_error_question(
    user_id: str,
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    import uuid
    try:
        service = StatsService(db)
        deleted = await service.delete_error_question(uuid.UUID(user_id), uuid.UUID(question_id))
        if not deleted:
            raise HTTPException(status_code=404, detail="Error question not found")
        return {"message": "Error question deleted successfully"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID")
