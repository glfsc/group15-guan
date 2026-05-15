import asyncio
import sys

sys.path.insert(0, r"d:\CodeArtsyunxing\CodeArt\toeic-app-backend")

from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.question import ListeningQuestion


async def main():
    async with async_session_maker() as session:
        result = await session.execute(
            select(ListeningQuestion).order_by(ListeningQuestion.created_at.desc()).limit(5)
        )
        rows = result.scalars().all()
        for row in rows:
            print(row.question_id, row.audio_url, row.audio_duration, row.created_at)


if __name__ == '__main__':
    asyncio.run(main())
