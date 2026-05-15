from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings
from app.models.base import Base
from app.models.user import User
from app.models.settings import PageSettings
from app.models.question import ListeningQuestion, GrammarQuestion
from app.models.answer import AnswerRecord
from app.models.progress import Progress, ErrorQuestion
import asyncio
import logging

logger = logging.getLogger(__name__)


async def ensure_schema_updates(conn):
    await conn.execute(text("ALTER TABLE listening_questions ADD COLUMN IF NOT EXISTS image_url VARCHAR(500)"))
    await conn.execute(text("ALTER TABLE listening_questions ADD COLUMN IF NOT EXISTS script_reference TEXT"))

    await conn.execute(text("UPDATE progress SET total_questions = 0 WHERE total_questions IS NULL"))
    await conn.execute(text("UPDATE progress SET listening_questions = 0 WHERE listening_questions IS NULL"))
    await conn.execute(text("UPDATE progress SET grammar_questions = 0 WHERE grammar_questions IS NULL"))
    await conn.execute(text("UPDATE progress SET total_practice_time = 0 WHERE total_practice_time IS NULL"))
    await conn.execute(text("UPDATE progress SET overall_accuracy = 0 WHERE overall_accuracy IS NULL"))
    await conn.execute(text("UPDATE progress SET listening_accuracy = 0 WHERE listening_accuracy IS NULL"))
    await conn.execute(text("UPDATE progress SET grammar_accuracy = 0 WHERE grammar_accuracy IS NULL"))
    await conn.execute(text("UPDATE error_questions SET error_count = 1 WHERE error_count IS NULL"))

    await conn.execute(text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'page_settings' AND column_name = 'font_size'
                AND data_type = 'USER-DEFINED'
            ) THEN
                ALTER TABLE page_settings ALTER COLUMN font_size TYPE VARCHAR(10) USING font_size::text;
                ALTER TABLE page_settings ALTER COLUMN font_size SET DEFAULT '100';
                UPDATE page_settings SET font_size = '100' WHERE font_size IN ('small', 'medium');
                UPDATE page_settings SET font_size = '130' WHERE font_size = 'large';
            END IF;
        END
        $$
    """))


async def init_database():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await ensure_schema_updates(conn)

    logger.info("Database tables created successfully")
    await engine.dispose()


async def test_connection():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
