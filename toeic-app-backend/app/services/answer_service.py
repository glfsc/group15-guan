from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.answer import AnswerRecord, QuestionType
from app.models.question import ListeningQuestion, GrammarQuestion
from app.models.progress import Progress, ErrorQuestion, AbilityLevel
import logging
from typing import Optional
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class AnswerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit_answer(
        self,
        user_id: uuid.UUID,
        question_id: uuid.UUID,
        question_type: str,
        user_answer: int,
        time_spent: int
    ) -> dict:
        is_correct = False
        correct_answer = None
        analysis = None
        grammar_rule = None
        example = None

        if question_type == "listening":
            question = await self._get_listening_question(question_id)
            if question:
                is_correct = user_answer == question.correct_answer
                correct_answer = question.correct_answer
                analysis = question.analysis
        else:
            question = await self._get_grammar_question(question_id)
            if question:
                is_correct = user_answer == question.correct_answer
                correct_answer = question.correct_answer
                grammar_rule = question.grammar_rule
                example = question.example

        answer_record = AnswerRecord(
            user_id=user_id,
            question_id=question_id,
            question_type=QuestionType(question_type),
            user_answer=user_answer,
            is_correct=is_correct,
            time_spent=time_spent
        )
        self.db.add(answer_record)

        if not is_correct and correct_answer is not None:
            await self._add_to_error_questions(
                user_id=user_id,
                question_id=question_id,
                question_type=question_type,
                user_answer=user_answer,
                correct_answer=correct_answer
            )

        await self._update_progress(
            user_id=user_id,
            question_type=question_type,
            is_correct=is_correct,
            time_spent=time_spent
        )

        await self.db.commit()

        return {
            "is_correct": is_correct,
            "correct_answer": correct_answer if correct_answer is not None else -1,
            "analysis": analysis,
            "grammar_rule": grammar_rule,
            "example": example
        }

    async def _get_listening_question(self, question_id: uuid.UUID) -> Optional[ListeningQuestion]:
        result = await self.db.execute(
            select(ListeningQuestion).where(ListeningQuestion.question_id == question_id)
        )
        return result.scalar_one_or_none()

    async def _get_grammar_question(self, question_id: uuid.UUID) -> Optional[GrammarQuestion]:
        result = await self.db.execute(
            select(GrammarQuestion).where(GrammarQuestion.question_id == question_id)
        )
        return result.scalar_one_or_none()

    async def _add_to_error_questions(
        self,
        user_id: uuid.UUID,
        question_id: uuid.UUID,
        question_type: str,
        user_answer: int,
        correct_answer: int
    ):
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
            error_question.error_count = (error_question.error_count or 0) + 1
            error_question.user_answer = user_answer
            error_question.correct_answer = correct_answer
            error_question.last_error_time = datetime.utcnow()
        else:
            error_question = ErrorQuestion(
                user_id=user_id,
                question_id=question_id,
                question_type=QuestionType(question_type),
                user_answer=user_answer,
                correct_answer=correct_answer,
                error_count=1
            )
            self.db.add(error_question)

    async def _update_progress(
        self,
        user_id: uuid.UUID,
        question_type: str,
        is_correct: bool,
        time_spent: int
    ):
        result = await self.db.execute(
            select(Progress).where(Progress.user_id == user_id)
        )
        progress = result.scalar_one_or_none()

        if not progress:
            progress = Progress(
                user_id=user_id,
                total_questions=0,
                listening_questions=0,
                grammar_questions=0,
                overall_accuracy=0.0,
                listening_accuracy=0.0,
                grammar_accuracy=0.0,
                total_practice_time=0,
                listening_level=AbilityLevel.BEGINNER,
                grammar_level=AbilityLevel.BEGINNER
            )
            self.db.add(progress)
            await self.db.flush()

        self._normalize_progress(progress)
        logger.info(
            "Progress before increment: total=%r listening=%r grammar=%r practice_time=%r",
            progress.total_questions,
            progress.listening_questions,
            progress.grammar_questions,
            progress.total_practice_time,
        )

        progress.total_questions = (progress.total_questions or 0) + 1
        progress.total_practice_time = (progress.total_practice_time or 0) + max(time_spent or 0, 0)

        if question_type == "listening":
            progress.listening_questions = (progress.listening_questions or 0) + 1
        else:
            progress.grammar_questions = (progress.grammar_questions or 0) + 1

        await self.db.flush()
        await self._recalculate_accuracy(progress)
        await self._update_ability_level(progress)

    def _normalize_progress(self, progress: Progress):
        progress.total_questions = progress.total_questions or 0
        progress.listening_questions = progress.listening_questions or 0
        progress.grammar_questions = progress.grammar_questions or 0
        progress.overall_accuracy = progress.overall_accuracy or 0.0
        progress.listening_accuracy = progress.listening_accuracy or 0.0
        progress.grammar_accuracy = progress.grammar_accuracy or 0.0
        progress.total_practice_time = progress.total_practice_time or 0
        progress.listening_level = progress.listening_level or AbilityLevel.BEGINNER
        progress.grammar_level = progress.grammar_level or AbilityLevel.BEGINNER

    async def _recalculate_accuracy(self, progress: Progress):
        total_listening = progress.listening_questions or 0
        total_grammar = progress.grammar_questions or 0
        total = progress.total_questions or 0

        if total > 0:
            correct_listening = await self._get_correct_count(
                progress.user_id, "listening"
            )
            correct_grammar = await self._get_correct_count(
                progress.user_id, "grammar"
            )

            progress.listening_accuracy = (correct_listening / total_listening * 100) if total_listening > 0 else 0.0
            progress.grammar_accuracy = (correct_grammar / total_grammar * 100) if total_grammar > 0 else 0.0
            progress.overall_accuracy = ((correct_listening + correct_grammar) / total * 100) if total > 0 else 0.0
        else:
            progress.listening_accuracy = 0.0
            progress.grammar_accuracy = 0.0
            progress.overall_accuracy = 0.0

    async def _get_correct_count(self, user_id: uuid.UUID, question_type: str) -> int:
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count()).where(
                and_(
                    AnswerRecord.user_id == user_id,
                    AnswerRecord.question_type == QuestionType(question_type),
                    AnswerRecord.is_correct == True
                )
            )
        )
        return result.scalar() or 0

    async def _update_ability_level(self, progress: Progress):
        if (progress.listening_accuracy or 0) >= 80:
            progress.listening_level = AbilityLevel.ADVANCED
        elif (progress.listening_accuracy or 0) >= 60:
            progress.listening_level = AbilityLevel.INTERMEDIATE
        else:
            progress.listening_level = AbilityLevel.BEGINNER

        if (progress.grammar_accuracy or 0) >= 80:
            progress.grammar_level = AbilityLevel.ADVANCED
        elif (progress.grammar_accuracy or 0) >= 60:
            progress.grammar_level = AbilityLevel.INTERMEDIATE
        else:
            progress.grammar_level = AbilityLevel.BEGINNER
