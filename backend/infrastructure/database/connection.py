"""
Database Connection Manager

Handles PostgreSQL database connections using asyncpg and SQLAlchemy.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
import structlog

from backend.core.config import get_settings

logger = structlog.get_logger(__name__)

# Naming convention for database constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.async_session_maker: Optional[async_sessionmaker] = None
        self.settings = get_settings()
        self._lock = asyncio.Lock()
    
    async def connect(self) -> None:
        """Initialize database connection."""
        async with self._lock:
            if self.engine is not None:
                return
            
            try:
                # Create async engine
                self.engine = create_async_engine(
                    self.settings.database_url,
                    echo=self.settings.is_development,
                    pool_pre_ping=True,
                    pool_size=20,
                    max_overflow=10,
                    pool_timeout=30,
                    pool_recycle=3600,
                )
                
                # Create session factory
                self.async_session_maker = async_sessionmaker(
                    self.engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                    autocommit=False,
                    autoflush=False,
                )
                
                # Test connection
                async with self.engine.begin() as conn:
                    await conn.execute("SELECT 1")
                
                logger.info("Database connection established successfully")
                
            except Exception as e:
                logger.error("Failed to connect to database", error=str(e))
                raise
    
    async def disconnect(self) -> None:
        """Close database connection."""
        async with self._lock:
            if self.engine is None:
                return
            
            try:
                await self.engine.dispose()
                self.engine = None
                self.async_session_maker = None
                logger.info("Database connection closed")
            except Exception as e:
                logger.error("Error closing database connection", error=str(e))
                raise
    
    async def migrate(self) -> None:
        """Run database migrations."""
        if self.engine is None:
            raise RuntimeError("Database not connected")
        
        try:
            # Import all models to register them with Base
            from backend.infrastructure.database import models  # noqa
            
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database migrations completed successfully")
        except Exception as e:
            logger.error("Database migration failed", error=str(e))
            raise
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        if self.async_session_maker is None:
            raise RuntimeError("Database not connected")
        
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """Check if database is healthy."""
        if self.engine is None:
            return False
        
        try:
            async with self.engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False


# Singleton instance
database_manager = DatabaseManager()


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get database session."""
    async with database_manager.get_session() as session:
        yield session