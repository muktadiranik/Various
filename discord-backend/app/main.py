# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
from app.api.v1.router import router as api_router
from app.config import settings
from app.core.database import init_db, close_db
from app.core.redis_client import close_redis
from app.services.redis_service import redis_service
from app.services.presence_service import presence_service
from app.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

async def cleanup_presence_task():
    """Background task to clean up stale presence data"""
    while True:
        await asyncio.sleep(300)
        await presence_service.cleanup_stale_presence()
        logger.info("Stale presence data cleaned up")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting up...")
    
    await init_db()
    logger.info("Database initialized")
    
    await redis_service.initialize()
    await redis_service.start_subscriber()
    logger.info("Redis service initialized")
    
    cleanup_task = asyncio.create_task(cleanup_presence_task())
    logger.info("Presence cleanup task started")
    
    yield
    
    logger.info("Shutting down...")
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    
    await redis_service.stop_subscriber()
    await close_redis()
    await close_db()
    logger.info("Shutdown complete")

app = FastAPI(
    title="Discord-like Backend API",
    description="Production-grade Discord-like backend with real-time messaging",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "Discord-like Backend API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }