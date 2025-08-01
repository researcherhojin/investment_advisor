"""
Health Check Routes

Provides system health and status endpoints for monitoring.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.config import get_settings, Settings
from infrastructure.database.connection import database_manager
from infrastructure.cache.redis_cache import cache_manager

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    environment: str
    services: Dict[str, Any]


@router.get("/", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """
    Basic health check endpoint.
    
    Returns system status and basic information.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="2.0.0",
        environment=settings.environment,
        services={
            "api": "healthy",
            "database": "unknown",
            "cache": "unknown",
        },
    )


@router.get("/detailed", response_model=HealthResponse)
async def detailed_health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """
    Detailed health check endpoint.
    
    Checks the status of all dependent services.
    """
    services = {}
    
    # Check database connection
    try:
        await database_manager.execute("SELECT 1")
        services["database"] = "healthy"
    except Exception as e:
        services["database"] = f"unhealthy: {str(e)}"
    
    # Check cache connection
    try:
        await cache_manager.ping()
        services["cache"] = "healthy"
    except Exception as e:
        services["cache"] = f"unhealthy: {str(e)}"
    
    # Check AI service availability (basic check)
    services["openai"] = "configured" if settings.openai_api_key else "not configured"
    services["alpha_vantage"] = "configured" if settings.alpha_vantage_api_key else "not configured"
    
    # Overall status
    overall_status = "healthy" if all(
        status == "healthy" or status.startswith("configured")
        for status in services.values()
    ) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="2.0.0",
        environment=settings.environment,
        services=services,
    )


@router.get("/ready")
async def readiness_check() -> Dict[str, str]:
    """
    Kubernetes readiness probe endpoint.
    
    Returns simple status for container orchestration.
    """
    return {"status": "ready"}


@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """
    Kubernetes liveness probe endpoint.
    
    Returns simple status for container orchestration.
    """
    return {"status": "alive"}