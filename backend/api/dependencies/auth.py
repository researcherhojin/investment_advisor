"""
Authentication Dependencies

FastAPI dependencies for authentication and authorization.
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import decode_access_token
from api.dependencies.database import get_db_session
from infrastructure.database.models import User

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """
    Get current user if authenticated (optional).
    
    Returns None if no valid token is provided.
    """
    if not token:
        return None
    
    payload = decode_access_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return None
    
    # Get user from database
    user = await db.get(User, user_uuid)
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Get current authenticated user (required).
    
    Raises HTTPException if not authenticated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception
    
    # Get user from database
    user = await db.get(User, user_uuid)
    if not user:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


class RoleChecker:
    """
    Dependency class for role-based access control.
    
    Usage:
        @router.get("/admin", dependencies=[Depends(RoleChecker(roles=["admin"]))])
    """
    
    def __init__(self, roles: list[str]):
        self.roles = roles
    
    async def __call__(self, user: User = Depends(get_current_user)) -> bool:
        """Check if user has required role."""
        # For now, we use is_superuser as admin role
        if "admin" in self.roles and not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return True