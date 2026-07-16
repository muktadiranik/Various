"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_database
from app.api.v1.endpoints import documents, search
from app.services.embedding import embedding_service
from app.services.vector_store import vector_store

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    await init_database()
    logger.info("✅ Database initialized")
    
    # Initialize embedding service (models loaded on first use)
    try:
        embedding_health = embedding_service.health_check()
        logger.info(f"✅ Embedding service ready: {embedding_health['model']} (dim: {embedding_health['dimension']})")
    except Exception as e:
        logger.error(f"❌ Failed to initialize embedding service: {e}")
        raise
    
    # Initialize vector store
    try:
        vector_health = vector_store.health_check()
        logger.info(f"✅ Vector store ready: {vector_health['total_vectors']} vectors")
    except Exception as e:
        logger.error(f"❌ Failed to initialize vector store: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")
    embedding_service.clear_cache()
    logger.info("✅ Cleanup completed")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Knowledge Base with semantic search",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    documents.router,
    prefix="/api/v1/documents",
    tags=["documents"],
)
app.include_router(
    search.router,
    prefix="/api/v1/search",
    tags=["search"],
)


@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else None,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with service statuses"""
    embedding_health = embedding_service.health_check()
    vector_health = vector_store.health_check()
    
    return {
        "status": "healthy" if all([
            embedding_health['status'] == 'healthy',
            vector_health['status'] == 'healthy',
        ]) else "degraded",
        "services": {
            "embedding": embedding_health,
            "vector_store": vector_health,
        },
        "cache_stats": embedding_service.get_cache_stats(),
        "vector_stats": vector_store.get_stats(),
    }