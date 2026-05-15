import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.tts_service import TTSService


async def main():
    service = TTSService()
    path = await service.synthesize_to_local_file("Hello, this is a TOEIC listening audio test.")
    print(path)


if __name__ == '__main__':
    asyncio.run(main())
