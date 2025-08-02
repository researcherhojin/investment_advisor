"""
Base Repository

Abstract base repository with common CRUD operations.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import structlog

from backend.infrastructure.database.connection import Base

logger = structlog.get_logger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType], ABC):
    """Base repository with common database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @property
    @abstractmethod
    def model_class(self) -> Type[ModelType]:
        """Return the model class for this repository."""
        pass
    
    async def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        try:
            instance = self.model_class(**kwargs)
            self.session.add(instance)
            await self.session.flush()
            await self.session.refresh(instance)
            return instance
        except Exception as e:
            logger.error(f"Error creating {self.model_class.__name__}", error=str(e))
            raise
    
    async def get_by_id(
        self,
        id: UUID,
        load_relationships: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """Get a record by ID."""
        try:
            query = select(self.model_class).where(self.model_class.id == id)
            
            # Load relationships if specified
            if load_relationships:
                for rel in load_relationships:
                    query = query.options(selectinload(getattr(self.model_class, rel)))
            
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting {self.model_class.__name__} by id", id=id, error=str(e))
            raise
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        load_relationships: Optional[List[str]] = None
    ) -> List[ModelType]:
        """Get all records with optional filtering and pagination."""
        try:
            query = select(self.model_class)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    query = query.where(getattr(self.model_class, key) == value)
            
            # Apply ordering
            if order_by:
                if order_by.startswith("-"):
                    query = query.order_by(getattr(self.model_class, order_by[1:]).desc())
                else:
                    query = query.order_by(getattr(self.model_class, order_by))
            
            # Load relationships
            if load_relationships:
                for rel in load_relationships:
                    query = query.options(selectinload(getattr(self.model_class, rel)))
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting all {self.model_class.__name__}", error=str(e))
            raise
    
    async def update(
        self,
        id: UUID,
        **kwargs
    ) -> Optional[ModelType]:
        """Update a record."""
        try:
            # Remove None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                return await self.get_by_id(id)
            
            query = (
                update(self.model_class)
                .where(self.model_class.id == id)
                .values(**update_data)
                .returning(self.model_class)
            )
            
            result = await self.session.execute(query)
            await self.session.flush()
            
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error updating {self.model_class.__name__}", id=id, error=str(e))
            raise
    
    async def delete(self, id: UUID) -> bool:
        """Delete a record."""
        try:
            query = delete(self.model_class).where(self.model_class.id == id)
            result = await self.session.execute(query)
            await self.session.flush()
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting {self.model_class.__name__}", id=id, error=str(e))
            raise
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering."""
        try:
            query = select(func.count()).select_from(self.model_class)
            
            if filters:
                for key, value in filters.items():
                    query = query.where(getattr(self.model_class, key) == value)
            
            result = await self.session.execute(query)
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error counting {self.model_class.__name__}", error=str(e))
            raise
    
    async def exists(self, **kwargs) -> bool:
        """Check if a record exists."""
        try:
            query = select(func.count()).select_from(self.model_class)
            
            for key, value in kwargs.items():
                query = query.where(getattr(self.model_class, key) == value)
            
            result = await self.session.execute(query)
            count = result.scalar() or 0
            return count > 0
        except Exception as e:
            logger.error(f"Error checking existence of {self.model_class.__name__}", error=str(e))
            raise