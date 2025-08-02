"""
FastAPI Main Application

Entry point for the AI Investment Advisory API.
"""

import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

import structlog

from core.config import get_settings
from infrastructure.database.connection import database_manager
from api.routes import health, analysis, stocks, auth

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting AI Investment Advisory API")
    settings = get_settings()
    
    # Initialize database connection
    try:
        await database_manager.connect()
        logger.info("Database connection established")
        
        # Run migrations if enabled
        if settings.auto_migrate:
            logger.info("Running database migrations")
            # TODO: Add alembic migration runner
            
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise
    
    # Initialize cache
    try:
        from infrastructure.cache.redis_cache import cache_manager
        await cache_manager.connect()
        logger.info("Cache connection established")
    except Exception as e:
        logger.warning("Failed to initialize cache", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Investment Advisory API")
    
    # Close database connection
    await database_manager.disconnect()
    
    # Close cache connection
    try:
        await cache_manager.disconnect()
    except:
        pass


def create_app() -> FastAPI:
    """
    Create FastAPI application instance.
    """
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="AI-powered investment advisory system for analyzing US and Korean stocks",
        lifespan=lifespan,
        debug=settings.debug,
        docs_url="/api/docs" if settings.is_development else None,
        redoc_url="/api/redoc" if settings.is_development else None,
    )
    
    # Add middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.is_development else ["api.yourdomain.com"],
    )
    
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
    )
    
    # Include routers
    app.include_router(health.router, prefix="/api/health", tags=["health"])
    app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
    app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
    app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )