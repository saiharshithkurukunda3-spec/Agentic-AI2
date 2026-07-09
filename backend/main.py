import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.utils.config import settings
from app.utils.logging_config import setup_logging, logger
from app.utils.http_client import HTTPClientProvider
from app.utils.rate_limiter import RateLimiterMiddleware
from app.database.mongodb import Database
from app.services.rag import rag_cache

from app.routes.auth import router as auth_router
from app.routes.history import router as history_router
from app.routes.research import router as research_router
from app.routes.health import router as health_router

# Setup structured logger
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP EVENT ---
    logger.info("Starting up VERITAS AI backend...", env=settings.ENVIRONMENT)
    
    # 1. Initialize HTTPX client connection pool
    HTTPClientProvider.initialize()
    
    # 2. Connect MongoDB Atlas
    await Database.connect_db()
    
    # 3. Start RAG Cache cleanup task
    rag_cache.start_cleanup_worker()
    
    yield
    
    # --- SHUTDOWN EVENT ---
    logger.info("Shutting down VERITAS AI backend...")
    
    # 1. Close HTTPX client connection pool
    await HTTPClientProvider.close()
    
    # 2. Close MongoDB connection
    await Database.close_db()
    
    # 3. Stop RAG Cache cleanup task
    await rag_cache.stop_cleanup_worker()
    
    logger.info("Shutdown sequence complete.")

# Initialize FastAPI with metadata
app = FastAPI(
    title="VERITAS AI Backend",
    description="Lightweight production-ready AI RAG Assistant backend",
    version="1.0.0",
    lifespan=lifespan
)

# Enforce strict CORS with cookie support
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Apply Rate Limiter middleware
# 60 requests per minute capacity, refills 1 token per second
app.add_middleware(
    RateLimiterMiddleware,
    capacity=60,
    refill_rate=1.0
)

# Mount Routes
app.include_router(health_router, prefix="", tags=["System"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(research_router, prefix="/research", tags=["Research"])
app.include_router(history_router, prefix="/history", tags=["Search History"])

@app.get("/")
async def root():
    return {
        "name": "VERITAS AI API",
        "description": "Premium lightweight RAG assistant backend running on FastAPI",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
