import asyncio
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

maas_endpoint = (os.getenv("MAAS_ENDPOINT") or "").strip()
maas_api_key = (os.getenv("MAAS_API_KEY") or "").strip()
model = (os.getenv("MAAS_MODEL") or "glm-5.1").strip()


def validate_env() -> None:
    missing = []
    if not maas_endpoint:
        missing.append("MAAS_ENDPOINT")
    if not maas_api_key:
        missing.append("MAAS_API_KEY")
    if not model:
        missing.append("MAAS_MODEL")

    if missing:
        raise ValueError(f"Missing required env vars: {', '.join(missing)}")


async def main():
    validate_env()

    print(f"Using endpoint: {maas_endpoint}")
    print(f"Using model: {model}")
    print(f"Using API key prefix: {maas_api_key[:8]}***")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {maas_api_key}",
    }
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你好"},
        ],
    }

    async with httpx.AsyncClient(timeout=40.0, verify=False) as client:
        resp = await client.post(maas_endpoint, headers=headers, json=body)
        print(f"MaaS Status: {resp.status_code}")
        print(f"MaaS Body: {resp.text[:1000]}")


if __name__ == "__main__":
    asyncio.run(main())
