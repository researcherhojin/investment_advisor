"""
Authentication Routes

API endpoints for user authentication and registration.
"""

from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    verify_token_type
)
from core.config import get_settings
from api.dependencies.database import get_db_session
from api.dependencies.auth import get_current_user
from application.dtos.auth_dto import (
    UserCreateDTO,
    UserResponseDTO,
    TokenResponseDTO,
    RefreshTokenRequestDTO
)
from infrastructure.database.models import User

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreateDTO,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Register a new user.
    
    Creates a new user account with hashed password.
    """
    # Check if user already exists
    stmt = select(User).where(
        (User.email == user_data.email) | (User.username == user_data.username)
    )
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        is_active=True,
        is_superuser=False
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponseDTO(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at
    )


@router.post("/token", response_model=TokenResponseDTO)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Login with username/email and password.
    
    Returns access token and refresh token.
    """
    # Try to find user by username or email
    stmt = select(User).where(
        (User.username == form_data.username) | (User.email == form_data.username)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # Verify user and password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return TokenResponseDTO(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponseDTO)
async def refresh_token(
    refresh_data: RefreshTokenRequestDTO,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Refresh access token using refresh token.
    
    Returns new access token and refresh token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode refresh token
    payload = decode_access_token(refresh_data.refresh_token)
    if not payload or not verify_token_type(payload, "refresh"):
        raise credentials_exception
    
    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception
    
    # Get user
    from uuid import UUID
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception
    
    user = await db.get(User, user_uuid)
    if not user or not user.is_active:
        raise credentials_exception
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    new_access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return TokenResponseDTO(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponseDTO)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.
    
    Requires authentication.
    """
    return UserResponseDTO(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at
    )


@router.put("/me", response_model=UserResponseDTO)
async def update_current_user(
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update current user information.
    
    Allows updating: full_name, email
    """
    # Update allowed fields
    if "full_name" in update_data:
        current_user.full_name = update_data["full_name"]
    
    if "email" in update_data and update_data["email"] != current_user.email:
        # Check if email is already taken
        stmt = select(User).where(User.email == update_data["email"])
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = update_data["email"]
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponseDTO(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user.
    
    In a stateless JWT system, logout is handled client-side by removing the token.
    This endpoint can be used for audit logging or token blacklisting if needed.
    """
    # TODO: Implement token blacklisting if needed
    return {"message": "Successfully logged out"}