from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, Integer
from app.models.progress import Progress, ErrorQuestion
from app.models.answer import AnswerRecord, QuestionType
import logging
import uuid
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class StatsService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_progress(self, user_id: uuid.UUID) -> Progress:
        result = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_error_questions(
        self,
        user_id: uuid.UUID,
        limit: int = 20
    ) -> List[ErrorQuestion]:
        result = await self.db.execute(
            select(ErrorQuestion)
            .where(ErrorQuestion.user_id == user_id)
            .order_by(ErrorQuestion.last_error_time.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_practice_history(
        self,
        user_id: uuid.UUID,
        limit: int = 50
    ) -> List[AnswerRecord]:
        result = await self.db.execute(
            select(AnswerRecord)
            .where(AnswerRecord.user_id == user_id)
            .order_by(AnswerRecord.answered_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_daily_stats(
        self,
        user_id: uuid.UUID,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(
                func.date(AnswerRecord.answered_at).label('date'),
                func.count(AnswerRecord.record_id).label('total'),
                func.sum(func.cast(AnswerRecord.is_correct, Integer)).label('correct')
            )
            .where(
                and_(
                    AnswerRecord.user_id == user_id,
                    AnswerRecord.answered_at >= start_date
                )
            )
            .group_by(func.date(AnswerRecord.answered_at))
            .order_by(func.date(AnswerRecord.answered_at).desc())
        )
        
        daily_stats = []
        for row in result:
            daily_stats.append({
                "date": str(row.date),
                "total_questions": row.total,
                "correct_questions": row.correct,
                "accuracy": (row.correct / row.total * 100) if row.total > 0 else 0.0
            })
        
        return daily_stats
    
    async def delete_error_question(
        self,
        user_id: uuid.UUID,
        question_id: uuid.UUID
    ) -> bool:
        result = await self.db.execute(
            select(ErrorQuestion).where(
                and_(
                    ErrorQuestion.user_id == user_id,
                    ErrorQuestion.question_id == question_id
                )
            )
        )
        error_question = result.scalar_one_or_none()
        if error_question:
            await self.db.delete(error_question)
            await self.db.commit()
            return True
        return False
