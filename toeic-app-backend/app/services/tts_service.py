import asyncio
import logging
from pathlib import Path
import uuid

import edge_tts
import pythoncom
import pyttsx3
from gtts import gTTS

from app.config import settings

logger = logging.getLogger(__name__)


class TTSService:
    def __init__(self):
        self.audio_dir = Path(settings.STATIC_AUDIO_DIR)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.voice = self._resolve_voice(settings.TTS_LANGUAGE)

    @staticmethod
    def _resolve_voice(language: str) -> str:
        voice_map = {
            'en': 'en-US-AriaNeural',
            'en-us': 'en-US-AriaNeural',
            'en-gb': 'en-GB-SoniaNeural',
            'zh': 'zh-CN-XiaoxiaoNeural',
            'zh-cn': 'zh-CN-XiaoxiaoNeural'
        }
        return voice_map.get(language.lower(), 'en-US-AriaNeural')

    async def synthesize_to_local_file(self, text: str) -> str:
        file_stem = str(uuid.uuid4())
        wav_path = self.audio_dir / f"{file_stem}.wav"
        mp3_path = self.audio_dir / f"{file_stem}.mp3"

        try:
            output_path = await self._generate_with_windows_tts(text, wav_path)
            logger.info("Generated audio with Windows TTS: %s", output_path.name)
            return f"/static/audio/{output_path.name}"
        except Exception as exc:
            logger.exception("Windows TTS failed")
            self._cleanup_temp_files(wav_path, mp3_path)

        try:
            await self._generate_with_edge_tts(text, mp3_path)
            logger.info("Generated audio with edge-tts: %s", mp3_path.name)
            return f"/static/audio/{mp3_path.name}"
        except Exception as exc:
            logger.exception("edge-tts failed")
            self._cleanup_temp_files(wav_path, mp3_path)

        await self._generate_with_gtts(text, mp3_path)
        logger.info("Generated audio with gTTS: %s", mp3_path.name)
        return f"/static/audio/{mp3_path.name}"

    async def _generate_with_windows_tts(self, text: str, wav_path: Path) -> Path:
        def _generate() -> Path:
            pythoncom.CoInitialize()
            engine = pyttsx3.init()
            try:
                for voice in engine.getProperty('voices'):
                    voice_name = getattr(voice, 'name', '').lower()
                    voice_id = getattr(voice, 'id', '').lower()
                    if settings.TTS_LANGUAGE.lower().startswith('en') and 'english' in voice_name:
                        engine.setProperty('voice', voice.id)
                        break
                    if settings.TTS_LANGUAGE.lower().startswith('zh') and ('chinese' in voice_name or 'huihui' in voice_id):
                        engine.setProperty('voice', voice.id)
                        break

                engine.save_to_file(text, str(wav_path))
                engine.runAndWait()
            finally:
                engine.stop()
                pythoncom.CoUninitialize()

            if not wav_path.exists() or wav_path.stat().st_size == 0:
                raise RuntimeError('Windows TTS did not produce a valid wav file')

            return wav_path

        return await asyncio.to_thread(_generate)

    async def _generate_with_edge_tts(self, text: str, file_path: Path) -> None:
        communicate = edge_tts.Communicate(text=text, voice=self.voice)
        await communicate.save(str(file_path))

        if not file_path.exists() or file_path.stat().st_size == 0:
            raise RuntimeError('edge-tts did not produce a valid audio file')

    async def _generate_with_gtts(self, text: str, file_path: Path) -> None:
        def _generate() -> None:
            tts = gTTS(text=text, lang=settings.TTS_LANGUAGE)
            tts.save(str(file_path))

        await asyncio.to_thread(_generate)

        if not file_path.exists() or file_path.stat().st_size == 0:
            raise RuntimeError('gTTS did not produce a valid audio file')

    @staticmethod
    def _cleanup_temp_files(*paths: Path) -> None:
        for path in paths:
            if path.exists():
                path.unlink()
