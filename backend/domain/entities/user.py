"""
User Domain Entity

Core business entity representing system users.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, EmailStr, validator


class User(BaseModel):
    """
    User entity representing a system user.
    
    Encapsulates user authentication and profile information
    with proper validation and business rules.
    """
    
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password_hash: str = Field(..., min_length=1)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    
    @validator("username")
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        username = v.strip().lower()
        
        # Check for valid characters (alphanumeric and underscore only)
        if not username.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, and underscores")
        
        # Cannot start or end with underscore
        if username.startswith("_") or username.endswith("_"):
            raise ValueError("Username cannot start or end with underscore")
        
        # Cannot have consecutive underscores
        if "__" in username:
            raise ValueError("Username cannot have consecutive underscores")
        
        return username
    
    @validator("password_hash")
    def validate_password_hash(cls, v: str) -> str:
        """Validate password hash is not empty."""
        if not v.strip():
            raise ValueError("Password hash cannot be empty")
        return v
    
    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate user account."""
        if self.is_active:
            return
        
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        if not self.is_active:
            return
        
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def verify_email(self) -> None:
        """Mark email as verified."""
        if self.is_verified:
            return
        
        self.is_verified = True
        self.updated_at = datetime.utcnow()
    
    def update_profile(self, **kwargs) -> None:
        """Update user profile information."""
        allowed_fields = {"username", "email"}
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
        
        self.updated_at = datetime.utcnow()
    
    @property
    def is_valid_user(self) -> bool:
        """Check if user is valid (active and verified)."""
        return self.is_active and self.is_verified
    
    @property
    def display_name(self) -> str:
        """Get display name for user."""
        return self.username.title()
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }