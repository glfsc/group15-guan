from contextlib import asynccontextmanager
import logging
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db.init_db import init_database
from .routers import answers, questions, settings as settings_router, stats

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception:
        logger.exception("Failed to initialize database")
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="托业英语学习应用API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_audio_dir = Path(settings.STATIC_AUDIO_DIR)
static_audio_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_audio_dir.parent)), name="static")

app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])
app.include_router(answers.router, prefix="/api/v1/answers", tags=["answers"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["stats"])
app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["settings"])

@app.get("/")
async def root():
    return {"message": "TOEIC Learning App API", "version": settings.APP_VERSION}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
