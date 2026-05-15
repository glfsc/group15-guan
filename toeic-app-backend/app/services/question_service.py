from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.question import ListeningQuestion, GrammarQuestion, Difficulty, ListeningQuestionType
from app.clients.maas_client import MaasClient
from app.services.tts_service import TTSService
from app.services.image_service import ImageService
from app.config import settings
import logging
from typing import List, Tuple
import uuid

logger = logging.getLogger(__name__)


class QuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.maas_client = MaasClient()
        self.tts_service = TTSService()
        self.image_service = ImageService()

    @staticmethod
    def _build_batches(total_count: int, base_batch_size: int) -> List[int]:
        if total_count <= 0:
            return []

        batch_size = max(1, base_batch_size)
        batches = [batch_size] * (total_count // batch_size)
        remainder = total_count % batch_size

        if remainder:
            if batches:
                batches[0] += remainder
            else:
                batches = [remainder]

        return batches

    async def _safe_generate_audio(self, narration_text: str) -> Tuple[str, int]:
        try:
            audio_url = await self.tts_service.synthesize_to_local_file(narration_text)
            logger.info(f"TTS returned audio_url={audio_url!r}")
            return audio_url, 30
        except Exception as exc:
            logger.warning(f"TTS generation failed, falling back to empty audio: {exc}")
            return "", 5

    async def _safe_generate_photo_image(self, image_prompt: str) -> str:
        if not image_prompt:
            return ""

        try:
            image_url = await self.image_service.synthesize_photo_prompt_to_image(image_prompt)
            logger.info(f"Image service returned image_url={image_url!r}")
            return image_url
        except Exception as exc:
            logger.warning(f"Image generation failed, falling back to local SVG image: {exc}", exc_info=True)
            try:
                fallback_url = await self.image_service.synthesize_photo_prompt_to_local_svg(image_prompt)
                logger.info(f"Image fallback SVG generated at image_url={fallback_url!r}")
                return fallback_url
            except Exception as fallback_exc:
                logger.error(f"Image SVG fallback also failed: {fallback_exc}", exc_info=True)
                return ""

    async def generate_listening_questions(
        self,
        difficulty: str,
        question_type: str,
        count: int
    ) -> List[ListeningQuestion]:
        try:
            batch_plan = self._build_batches(count, settings.MAAS_BATCH_SIZE)
            logger.info(f"Generating listening questions in batches: {batch_plan}")

            merged_questions_data = []
            for batch_count in batch_plan:
                questions_data = await self.maas_client.generate_listening_question(
                    difficulty=difficulty,
                    question_type=question_type,
                    count=batch_count
                )
                merged_questions_data.extend(questions_data)

            if not merged_questions_data:
                raise ValueError("MaaS returned empty listening question list")

            created_ids: List[uuid.UUID] = []
            for q_data in merged_questions_data[:count]:
                narration_text = q_data.get("audio_content") or q_data.get("question")
                audio_url, audio_duration = await self._safe_generate_audio(narration_text)

                image_prompt = None
                image_url = None
                if question_type == ListeningQuestionType.PHOTO_DESCRIPTION.value:
                    image_prompt = q_data.get("image_prompt") or q_data.get("script_reference") or narration_text or q_data.get("question")
                    image_url = await self._safe_generate_photo_image(image_prompt)
                    logger.info(f"Prepared photo_description image for prompt with image_url={image_url!r}")

                question = ListeningQuestion(
                    question=q_data["question"],
                    audio_url=audio_url,
                    audio_duration=audio_duration,
                    image_url=image_url or None,
                    script_reference=q_data.get("script_reference") or image_prompt or q_data.get("audio_content"),
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    analysis=q_data.get("analysis"),
                    difficulty=Difficulty(difficulty),
                    question_type=ListeningQuestionType(question_type)
                )
                self.db.add(question)
                await self.db.flush()
                created_ids.append(question.question_id)

            await self.db.commit()

            result = await self.db.execute(
                select(ListeningQuestion)
                .where(ListeningQuestion.question_id.in_(created_ids))
            )
            questions_by_id = {question.question_id: question for question in result.scalars().all()}
            return [questions_by_id[qid] for qid in created_ids if qid in questions_by_id]

        except Exception as e:
            logger.error(f"Failed to generate listening questions: {e}")
            await self.db.rollback()
            raise
        finally:
            await self.image_service.close()
            await self.maas_client.close()

    async def generate_grammar_questions(
        self,
        knowledge_point: str,
        difficulty: str,
        count: int
    ) -> List[GrammarQuestion]:
        try:
            batch_plan = self._build_batches(count, settings.MAAS_BATCH_SIZE)
            logger.info(f"Generating grammar questions in batches: {batch_plan}")

            merged_questions_data = []
            for batch_count in batch_plan:
                questions_data = await self.maas_client.generate_grammar_question(
                    knowledge_point=knowledge_point,
                    difficulty=difficulty,
                    count=batch_count
                )
                merged_questions_data.extend(questions_data)

            if not merged_questions_data:
                raise ValueError("MaaS returned empty grammar question list")

            questions = []
            for q_data in merged_questions_data[:count]:
                question = GrammarQuestion(
                    content=q_data["content"],
                    question_mark=q_data["question_mark"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    grammar_rule=q_data.get("grammar_rule"),
                    example=q_data.get("example"),
                    knowledge_point=knowledge_point,
                    difficulty=Difficulty(difficulty)
                )
                self.db.add(question)
                questions.append(question)

            await self.db.commit()
            for q in questions:
                await self.db.refresh(q)

            return questions

        except Exception as e:
            logger.error(f"Failed to generate grammar questions: {e}")
            await self.db.rollback()
            raise
        finally:
            await self.image_service.close()
            await self.maas_client.close()

    async def get_listening_question(self, question_id: uuid.UUID) -> ListeningQuestion:
        result = await self.db.execute(
            select(ListeningQuestion).where(ListeningQuestion.question_id == question_id)
        )
        return result.scalar_one_or_none()

    async def get_grammar_question(self, question_id: uuid.UUID) -> GrammarQuestion:
        result = await self.db.execute(
            select(GrammarQuestion).where(GrammarQuestion.question_id == question_id)
        )
        return result.scalar_one_or_none()
