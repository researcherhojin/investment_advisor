"""
Health Check Routes

API endpoints for service health monitoring.
"""

from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.database import get_db_session
from core.config import get_settings

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def health_check():
    """
    Basic health check endpoint.
    
    Returns service status and basic information.
    """
    settings = get_settings()
    
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment
    }


@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check(db: AsyncSession = Depends(get_db_session)):
    """
    Readiness check endpoint.
    
    Verifies that all dependencies are available and functioning.
    """
    settings = get_settings()
    checks = {
        "database": False,
        "cache": False,
        "openai": bool(settings.openai_api_key)
    }
    
    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        checks["database"] = result.scalar() == 1
    except Exception:
        pass
    
    # Check cache
    try:
        from infrastructure.cache.redis_cache import cache_manager
        await cache_manager.ping()
        checks["cache"] = True
    except Exception:
        pass
    
    # Overall status
    all_ready = all(checks.values())
    
    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/live", response_model=Dict[str, str])
async def liveness_check():
    """
    Liveness check endpoint.
    
    Simple endpoint to verify the service is running.
    Used by container orchestrators for health monitoring.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }