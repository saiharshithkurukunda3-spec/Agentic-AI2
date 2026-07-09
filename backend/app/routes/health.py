import time
import os
import psutil
from fastapi import APIRouter
from app.utils.config import settings
from app.database.mongodb import Database
from app.utils.logging_config import logger

router = APIRouter()
START_TIME = time.time()

@router.get("/health", tags=["System"])
async def health_check():
    # 1. Check database connectivity
    db_status = "unconfigured"
    if Database.client:
        try:
            await Database.client.admin.command('ping')
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
            logger.error("Healthcheck database connection error", error=str(e))
    else:
        db_status = "disconnected"

    # 2. Check Gemini config
    gemini_status = "configured" if (settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "mock_key_for_testing") else "mocked/missing"

    # 3. Read memory usage using psutil
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    ram_usage_mb = memory_info.rss / (1024 * 1024)

    # 4. Calculate uptime
    uptime_seconds = time.time() - START_TIME

    # Log structured diagnostic message if RAM exceeds warning threshold (e.g., 350MB)
    if ram_usage_mb > 350:
        logger.warning("High RAM usage detected on healthcheck", ram_usage_mb=ram_usage_mb)

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "gemini_api": gemini_status,
        "environment": settings.ENVIRONMENT,
        "diagnostics": {
            "uptime_seconds": round(uptime_seconds, 2),
            "ram_usage_mb": round(ram_usage_mb, 2),
            "pid": os.getpid()
        }
    }
