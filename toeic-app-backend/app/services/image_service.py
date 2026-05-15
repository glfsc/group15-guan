from __future__ import annotations

import base64
import binascii
import html
import logging
import textwrap
import uuid
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx

from app.clients.obs_client import OBSClient
from app.config import settings

logger = logging.getLogger(__name__)


class ImageService:
    def __init__(self):
        image_dir = getattr(settings, 'STATIC_IMAGE_DIR', 'app/static/images')
        self.image_dir = Path(image_dir)
        self.image_dir.mkdir(parents=True, exist_ok=True)

        self.endpoint = (settings.MAAS_IMAGE_ENDPOINT or '').rstrip('/')
        self.api_key = (settings.MAAS_IMAGE_API_KEY or settings.MAAS_API_KEY or '').strip()
        self.model = (settings.MAAS_IMAGE_MODEL or '').strip()
        self.image_size = settings.MAAS_IMAGE_SIZE
        self.image_quality = settings.MAAS_IMAGE_QUALITY
        self.response_format = settings.MAAS_IMAGE_RESPONSE_FORMAT
        self.image_seed = settings.MAAS_IMAGE_SEED
        self.obs_client = OBSClient()

        request_timeout = max(float(settings.MAAS_TIMEOUT_SECONDS), 240.0)
        timeout = httpx.Timeout(connect=20.0, read=request_timeout, write=120.0, pool=60.0)
        self.http_client = httpx.AsyncClient(timeout=timeout, verify=False)

    def is_real_image_generation_enabled(self) -> bool:
        return bool(self.endpoint and self.api_key and self.model)

    async def synthesize_photo_prompt_to_image(self, prompt: str) -> str:
        normalized_prompt = (prompt or 'TOEIC photo description').strip()

        if self.is_real_image_generation_enabled():
            try:
                image_bytes, content_type, extension = await self._generate_real_image_bytes(normalized_prompt)
                file_name = f"{uuid.uuid4()}.{extension}"

                obs_url = await self.obs_client.upload_image(image_bytes, file_name, content_type)
                if obs_url:
                    logger.info(f"Uploaded generated image to OBS: {obs_url}")
                    return obs_url

                file_path = self.image_dir / file_name
                file_path.write_bytes(image_bytes)
                local_url = f"/static/images/{file_name}"
                logger.info(f"Stored generated image locally: {local_url}")
                return local_url
            except Exception as exc:
                logger.warning(f"Real image generation failed, falling back to SVG scene card: {exc}", exc_info=True)

        return await self.synthesize_photo_prompt_to_local_svg(normalized_prompt)

    async def synthesize_photo_prompt_to_local_svg(self, prompt: str) -> str:
        file_name = f"{uuid.uuid4()}.svg"
        file_path = self.image_dir / file_name
        file_path.write_text(self._build_svg(prompt), encoding='utf-8')
        return f"/static/images/{file_name}"

    async def _generate_real_image_bytes(self, prompt: str) -> tuple[bytes, str, str]:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }
        payload = {
            'model': self.model,
            'prompt': prompt,
            'size': self.image_size,
            'response_format': self.response_format,
        }
        if self.image_quality:
            payload['quality'] = self.image_quality
        if self.image_seed is not None:
            payload['seed'] = self.image_seed

        response = await self.http_client.post(self.endpoint, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Image generated via model={self.model}, size={self.image_size}, response_format={self.response_format}")

        image_bytes = self._extract_image_bytes(result)
        if not image_bytes:
            raise ValueError('Image API returned no usable image data')

        content_type = self._detect_content_type(image_bytes)
        extension = self._detect_extension(content_type)
        return image_bytes, content_type, extension

    def _extract_image_bytes(self, payload: dict) -> Optional[bytes]:
        candidates = []

        if isinstance(payload, dict):
            data = payload.get('data')
            if isinstance(data, list) and data:
                candidates.extend(item for item in data if isinstance(item, dict))
            candidates.append(payload)

        for item in candidates:
            b64_data = item.get('b64_json') or item.get('image_base64') or item.get('base64')
            if isinstance(b64_data, str) and b64_data.strip():
                decoded = self._decode_base64_image_data(b64_data)
                if decoded:
                    return decoded

            image_url = item.get('url') or item.get('image_url')
            if isinstance(image_url, str) and image_url.strip():
                downloaded = self._download_image_bytes_sync_safe(image_url)
                if downloaded:
                    return downloaded

        return None

    def _decode_base64_image_data(self, raw_data: str) -> Optional[bytes]:
        normalized_data = raw_data.strip()
        if not normalized_data:
            return None

        if normalized_data.startswith('data:'):
            _, _, normalized_data = normalized_data.partition(',')
            normalized_data = normalized_data.strip()

        if not normalized_data:
            return None

        try:
            return base64.b64decode(normalized_data, validate=False)
        except (ValueError, binascii.Error) as exc:
            logger.warning(f"Failed to decode generated image base64 payload: {exc}")
            return None

    def _download_image_bytes_sync_safe(self, image_url: str) -> Optional[bytes]:
        parsed_url = urlparse(image_url)
        if parsed_url.scheme not in {'http', 'https'}:
            logger.warning(f"Skipping unsupported generated image URL: {image_url}")
            return None

        try:
            response = httpx.get(image_url, timeout=120.0, verify=False)
            response.raise_for_status()
            return response.content
        except Exception as exc:
            logger.warning(f"Failed to download generated image from URL response: {exc}")
            return None

    def _detect_content_type(self, image_bytes: bytes) -> str:
        if image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'image/png'
        if image_bytes.startswith(b'\xff\xd8\xff'):
            return 'image/jpeg'
        if image_bytes.startswith(b'GIF87a') or image_bytes.startswith(b'GIF89a'):
            return 'image/gif'
        if image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:16]:
            return 'image/webp'
        return 'image/png'

    def _detect_extension(self, content_type: str) -> str:
        return {
            'image/png': 'png',
            'image/jpeg': 'jpg',
            'image/gif': 'gif',
            'image/webp': 'webp',
        }.get(content_type, 'png')

    def _build_svg(self, prompt: str) -> str:
        safe_prompt = html.escape((prompt or 'TOEIC photo description').strip())
        wrapped_lines = textwrap.wrap(safe_prompt, width=28)[:5]
        text_nodes = []
        for index, line in enumerate(wrapped_lines):
            y = 275 + index * 28
            text_nodes.append(
                f'<text x="60" y="{y}" font-size="20" fill="#334155" font-family="Segoe UI, Arial, sans-serif">{line}</text>'
            )

        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="640" viewBox="0 0 960 640">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f8fbff" />
      <stop offset="100%" stop-color="#eef4ff" />
    </linearGradient>
    <linearGradient id="card" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="100%" stop-color="#f8fafc" />
    </linearGradient>
  </defs>
  <rect width="960" height="640" fill="url(#bg)" />
  <circle cx="120" cy="110" r="56" fill="#dbeafe" />
  <circle cx="820" cy="130" r="72" fill="#e0e7ff" />
  <circle cx="760" cy="520" r="64" fill="#dcfce7" />
  <rect x="70" y="70" rx="28" ry="28" width="820" height="500" fill="url(#card)" stroke="#dbe3f0" stroke-width="2" />
  <rect x="110" y="120" rx="20" ry="20" width="320" height="180" fill="#dbeafe" />
  <rect x="470" y="120" rx="20" ry="20" width="160" height="120" fill="#c7d2fe" />
  <rect x="660" y="120" rx="20" ry="20" width="160" height="120" fill="#bfdbfe" />
  <rect x="470" y="260" rx="20" ry="20" width="350" height="40" fill="#e2e8f0" />
  <rect x="470" y="320" rx="20" ry="20" width="270" height="40" fill="#e2e8f0" />
  <text x="60" y="48" font-size="26" font-weight="700" fill="#1e3a8a" font-family="Segoe UI, Arial, sans-serif">TOEIC Photo Description</text>
  <text x="60" y="88" font-size="18" fill="#64748b" font-family="Segoe UI, Arial, sans-serif">根据题目内容生成的场景示意图</text>
  <text x="60" y="238" font-size="24" font-weight="700" fill="#0f172a" font-family="Segoe UI, Arial, sans-serif">Scene Prompt</text>
  {''.join(text_nodes)}
</svg>
"""

    async def close(self):
        await self.http_client.aclose()
        await self.obs_client.close()
