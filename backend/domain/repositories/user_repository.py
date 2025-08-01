"""
User Repository Interface

Abstract repository interface for user operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.user import User


class UserRepository(ABC):
    """Abstract repository interface for user operations."""
    
    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        pass
    
    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass
    
    @abstractmethod
    async def list_users(
        self,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[User]:
        """List users with optional filters."""
        pass
    
    @abstractmethod
    async def update_user(self, user: User) -> User:
        """Update an existing user."""
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user by ID."""
        pass
    
    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        pass
    
    @abstractmethod
    async def username_exists(self, username: str) -> bool:
        """Check if username already exists."""
        pass
    
    @abstractmethod
    async def search_users(self, query: str, limit: int = 10) -> List[User]:
        """Search users by username or email."""
        pass