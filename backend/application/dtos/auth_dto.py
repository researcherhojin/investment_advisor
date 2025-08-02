"""
Authentication DTOs

Data Transfer Objects for authentication-related operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator


class UserCreateDTO(BaseModel):
    """DTO for user registration."""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    
    @validator("username")
    def validate_username(cls, v):
        """Validate username format."""
        if not v.isalnum() and "_" not in v:
            raise ValueError("Username must contain only letters, numbers, and underscores")
        return v
    
    @validator("password")
    def validate_password(cls, v):
        """Validate password strength."""
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "john_doe",
                "password": "SecurePass123",
                "full_name": "John Doe"
            }
        }


class UserResponseDTO(BaseModel):
    """DTO for user response."""
    id: UUID = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    is_active: bool = Field(..., description="Is user active")
    is_superuser: bool = Field(..., description="Is user superuser")
    created_at: datetime = Field(..., description="Account creation time")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "username": "john_doe",
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2025-01-15T10:30:00Z"
            }
        }


class TokenResponseDTO(BaseModel):
    """DTO for token response."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class RefreshTokenRequestDTO(BaseModel):
    """DTO for refresh token request."""
    refresh_token: str = Field(..., description="JWT refresh token")
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class PasswordChangeDTO(BaseModel):
    """DTO for password change."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator("new_password")
    def validate_new_password(cls, v, values):
        """Validate new password."""
        if "current_password" in values and v == values["current_password"]:
            raise ValueError("New password must be different from current password")
        
        # Apply same validation as UserCreateDTO
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "OldPass123",
                "new_password": "NewPass456"
            }
        }


class UserUpdateDTO(BaseModel):
    """DTO for user profile update."""
    email: Optional[EmailStr] = Field(None, description="New email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "full_name": "John Smith"
            }
        }