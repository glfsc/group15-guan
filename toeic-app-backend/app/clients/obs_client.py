import httpx
from app.config import settings
import logging
from typing import Optional
import hashlib
import hmac
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class OBSClient:
    def __init__(self):
        self.bucket = settings.OBS_BUCKET
        self.region = settings.OBS_REGION
        self.endpoint = settings.OBS_ENDPOINT
        self.ak = settings.OBS_AK
        self.sk = settings.OBS_SK
        self.client = httpx.AsyncClient(timeout=30.0)

    def _generate_signature(self, method: str, object_key: str, timestamp: str) -> str:
        string_to_sign = f"{method}\n\n\n{timestamp}\n/{self.bucket}/{object_key}"
        signature = hmac.new(
            self.sk.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        ).digest()
        return base64.b64encode(signature).decode('utf-8')

    async def _upload_bytes(
        self,
        file_data: bytes,
        file_name: str,
        content_type: str
    ) -> Optional[str]:
        timestamp = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        signature = self._generate_signature("PUT", file_name, timestamp)

        try:
            response = await self.client.put(
                f"{self.endpoint}/{self.bucket}/{file_name}",
                headers={
                    "Content-Type": content_type,
                    "Date": timestamp,
                    "Authorization": f"OBS {self.ak}:{signature}"
                },
                content=file_data
            )
            response.raise_for_status()

            file_url = f"{self.endpoint}/{self.bucket}/{file_name}"
            logger.info(f"File uploaded successfully: {file_url}")
            return file_url

        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return None

    async def upload_audio(
        self,
        audio_data: bytes,
        file_name: str,
        content_type: str = "audio/mpeg"
    ) -> Optional[str]:
        return await self._upload_bytes(audio_data, file_name, content_type)

    async def upload_image(
        self,
        image_data: bytes,
        file_name: str,
        content_type: str = "image/png"
    ) -> Optional[str]:
        return await self._upload_bytes(image_data, file_name, content_type)

    async def delete_audio(self, file_name: str) -> bool:
        timestamp = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        signature = self._generate_signature("DELETE", file_name, timestamp)

        try:
            response = await self.client.delete(
                f"{self.endpoint}/{self.bucket}/{file_name}",
                headers={
                    "Date": timestamp,
                    "Authorization": f"OBS {self.ak}:{signature}"
                }
            )
            response.raise_for_status()
            logger.info(f"Audio deleted successfully: {file_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete audio: {e}")
            return False

    async def close(self):
        await self.client.aclose()
