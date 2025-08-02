"""
Database Dependencies

Dependency injection for database sessions.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.connection import database_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session.
    
    Yields a database session and ensures it's properly closed.
    """
    async with database_manager.get_session() as session:
        yield session