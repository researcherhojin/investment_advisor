"""
FastAPI Main Application

Entry point for the AI Investment Advisory System API.
Implements Clean Architecture principles with proper dependency injection.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import structlog
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.routes import health, stocks, analysis, agents
from api.middleware.logging import LoggingMiddleware
from api.middleware.rate_limiting import RateLimitingMiddleware
from infrastructure.database.connection import database_manager
from infrastructure.cache.redis_cache import cache_manager
from core.config import get_settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown tasks."""
    settings = get_settings()
    
    logger.info("Starting AI Investment Advisory API", version="2.0")
    
    try:
        # Initialize database connection
        await database_manager.connect()
        logger.info("Database connected successfully")
        
        # Initialize cache connection
        await cache_manager.connect()
        logger.info("Cache connected successfully")
        
        # Perform database migrations if needed
        if settings.auto_migrate:
            await database_manager.migrate()
            logger.info("Database migrations completed")
    
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        # Continue startup even if some services fail (for development)
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down AI Investment Advisory API")
    try:
        await cache_manager.disconnect()
        await database_manager.disconnect()
        logger.info("Cleanup completed")
    except Exception as e:
        logger.error("Error during cleanup", error=str(e))


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="AI Investment Advisory System",
        description="Professional stock analysis using multiple AI agents",
        version="2.0.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )
    
    # Add middleware
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(LoggingMiddleware)
    
    if settings.rate_limiting_enabled:
        app.add_middleware(RateLimitingMiddleware)
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(stocks.router, prefix="/api/v1/stocks", tags=["Stocks"])
    app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["AI Agents"])
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Unhandled exception occurred",
            exc_info=exc,
            path=request.url.path,
            method=request.method,
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, "request_id", None),
            },
        )
    
    return app


# Create the application instance
app = create_application()


# Health check endpoint (for development)
@app.get("/")
async def root():
    """Root endpoint for basic health check."""
    return {
        "message": "AI Investment Advisory System API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )