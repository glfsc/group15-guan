from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "TOEIC Learning App"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    DATABASE_URL: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "toeic_app"
    DB_USER: str = "postgres"
    DB_PASSWORD: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    MAAS_ENDPOINT: str = "https://api.modelarts-maas.com"
    MAAS_API_KEY: Optional[str] = None
    MAAS_AK: Optional[str] = None
    MAAS_SK: Optional[str] = None
    MAAS_MODEL: str = "glm-5.1"
    MAAS_REGION: str = "cn-north-4"
    MAAS_PROJECT_ID: str = ""
    MAAS_TIMEOUT_SECONDS: float = 120.0
    MAAS_MAX_RETRIES: int = 3
    MAAS_BATCH_SIZE: int = 3

    MAAS_IMAGE_ENDPOINT: str = "https://api.modelarts-maas.com/v1/images/generations"
    MAAS_IMAGE_API_KEY: Optional[str] = None
    MAAS_IMAGE_MODEL: str = "qwen-image"
    MAAS_IMAGE_SIZE: str = "1024x1024"
    MAAS_IMAGE_QUALITY: str = ""
    MAAS_IMAGE_RESPONSE_FORMAT: str = "b64_json"
    MAAS_IMAGE_SEED: Optional[int] = 1

    TTS_LANGUAGE: str = "en"
    STATIC_AUDIO_DIR: str = "app/static/audio"
    STATIC_IMAGE_DIR: str = "app/static/images"

    OBS_BUCKET: str
    OBS_REGION: str
    OBS_ENDPOINT: str
    OBS_AK: str
    OBS_SK: str

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
