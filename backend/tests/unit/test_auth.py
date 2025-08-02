"""
Unit Tests for Authentication

Test authentication and authorization functionality.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from backend.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    create_refresh_token,
    verify_token_type
)


class TestPasswordHashing:
    """Test password hashing functionality."""
    
    def test_password_hash_and_verify(self):
        """Test password hashing and verification."""
        password = "SecurePassword123"
        
        # Hash password
        hashed = get_password_hash(password)
        
        # Verify correct password
        assert verify_password(password, hashed) is True
        
        # Verify incorrect password
        assert verify_password("WrongPassword", hashed) is False
    
    def test_different_hashes_for_same_password(self):
        """Test that same password generates different hashes."""
        password = "TestPassword123"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different (due to salt)
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token functionality."""
    
    def test_create_and_decode_access_token(self):
        """Test creating and decoding access token."""
        user_id = str(uuid4())
        data = {"sub": user_id}
        
        # Create token
        token = create_access_token(data)
        
        # Decode token
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == user_id
        assert "exp" in decoded
    
    def test_access_token_expiration(self):
        """Test access token expiration."""
        user_id = str(uuid4())
        
        # Create token with short expiration
        token = create_access_token(
            {"sub": user_id},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        # Decode should return None for expired token
        decoded = decode_access_token(token)
        assert decoded is None
    
    def test_create_and_verify_refresh_token(self):
        """Test creating and verifying refresh token."""
        user_id = str(uuid4())
        data = {"sub": user_id}
        
        # Create refresh token
        token = create_refresh_token(data)
        
        # Decode token
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == user_id
        assert decoded["type"] == "refresh"
        assert verify_token_type(decoded, "refresh") is True
        assert verify_token_type(decoded, "access") is False
    
    def test_invalid_token_decode(self):
        """Test decoding invalid token."""
        invalid_token = "invalid.token.here"
        
        decoded = decode_access_token(invalid_token)
        assert decoded is None
    
    def test_token_with_additional_claims(self):
        """Test token with additional claims."""
        data = {
            "sub": str(uuid4()),
            "email": "user@example.com",
            "roles": ["user", "admin"]
        }
        
        token = create_access_token(data)
        decoded = decode_access_token(token)
        
        assert decoded["email"] == data["email"]
        assert decoded["roles"] == data["roles"]


@pytest.mark.asyncio
class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    async def test_user_registration(self, client):
        """Test user registration endpoint."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123",
            "full_name": "New User"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data
    
    async def test_duplicate_email_registration(self, client, create_test_user):
        """Test registration with duplicate email."""
        # Create existing user
        user = await create_test_user(email="existing@example.com")
        
        # Try to register with same email
        user_data = {
            "email": "existing@example.com",
            "username": "different_username",
            "password": "SecurePass123"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    async def test_user_login(self, client, create_test_user):
        """Test user login endpoint."""
        # Create user with known password
        password = "TestPassword123"
        hashed = get_password_hash(password)
        user = await create_test_user(
            username="testuser",
            email="test@example.com",
            hashed_password=hashed
        )
        
        # Login
        login_data = {
            "username": "testuser",
            "password": password
        }
        
        response = await client.post(
            "/api/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_with_email(self, client, create_test_user):
        """Test login using email instead of username."""
        password = "TestPassword123"
        hashed = get_password_hash(password)
        user = await create_test_user(
            email="emailtest@example.com",
            hashed_password=hashed
        )
        
        # Login with email
        login_data = {
            "username": "emailtest@example.com",  # Using email as username
            "password": password
        }
        
        response = await client.post(
            "/api/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
    
    async def test_invalid_login(self, client, create_test_user):
        """Test login with invalid credentials."""
        user = await create_test_user()
        
        login_data = {
            "username": user.username,
            "password": "WrongPassword"
        }
        
        response = await client.post(
            "/api/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    async def test_get_current_user(self, client, create_test_user):
        """Test getting current user info."""
        # Create user and get token
        password = "TestPassword123"
        hashed = get_password_hash(password)
        user = await create_test_user(hashed_password=hashed)
        
        # Login to get token
        login_response = await client.post(
            "/api/auth/token",
            data={"username": user.username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Get user info
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(user.id)
        assert data["email"] == user.email
        assert data["username"] == user.username
    
    async def test_refresh_token(self, client, create_test_user):
        """Test refreshing access token."""
        # Create user and get tokens
        password = "TestPassword123"
        hashed = get_password_hash(password)
        user = await create_test_user(hashed_password=hashed)
        
        # Login to get tokens
        login_response = await client.post(
            "/api/auth/token",
            data={"username": user.username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        tokens = login_response.json()
        
        # Refresh token
        refresh_response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]}
        )
        
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        assert new_tokens["access_token"] != tokens["access_token"]