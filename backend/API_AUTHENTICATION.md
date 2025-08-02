# API Authentication Guide

## Overview

The API uses JWT (JSON Web Tokens) for authentication with access tokens and refresh tokens.

## Authentication Flow

### 1. User Registration

```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### 2. User Login

```bash
POST /api/auth/token
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=SecurePass123
```

Or with JSON:
```bash
POST /api/auth/token
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePass123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Using Access Token

Include the access token in the Authorization header:

```bash
GET /api/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Refreshing Access Token

When the access token expires (after 30 minutes by default):

```bash
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response:
```json
{
  "access_token": "new_access_token",
  "refresh_token": "new_refresh_token",
  "token_type": "bearer"
}
```

## Protected Endpoints

### Endpoints Requiring Authentication

- `GET /api/auth/me` - Get current user info
- `PUT /api/auth/me` - Update current user info
- `POST /api/auth/logout` - Logout

### Endpoints with Optional Authentication

- `POST /api/analysis/` - Create analysis (saves to user history if authenticated)
- `GET /api/analysis/` - List analyses (filters by user if authenticated)

### Admin-Only Endpoints

Future endpoints that require superuser status will use the `get_current_superuser` dependency.

## Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

## Security Best Practices

### 1. Token Storage (Frontend)

```javascript
// Store tokens securely
localStorage.setItem('access_token', response.access_token);
localStorage.setItem('refresh_token', response.refresh_token);

// Include in API requests
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
};
```

### 2. Token Refresh Logic

```javascript
async function apiRequest(url, options = {}) {
  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  });
  
  if (response.status === 401) {
    // Try to refresh token
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      // Retry request with new token
      response = await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
    }
  }
  
  return response;
}
```

### 3. Logout

```javascript
function logout() {
  // Remove tokens
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  
  // Optional: Call logout endpoint for audit
  fetch('/api/auth/logout', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${access_token}`
    }
  });
}
```

## Environment Configuration

Set these in your `.env` file:

```env
# Security
SECRET_KEY=your_super_secret_key_minimum_32_characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Testing Authentication

### Using cURL

1. Register:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"TestPass123"}'
```

2. Login:
```bash
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=TestPass123"
```

3. Access protected endpoint:
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/token",
    data={"username": "testuser", "password": "TestPass123"}
)
tokens = response.json()

# Use access token
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
user_info = requests.get(
    "http://localhost:8000/api/auth/me",
    headers=headers
)
print(user_info.json())
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

## Future Enhancements

1. **OAuth2 Support**: Google, GitHub login
2. **Two-Factor Authentication**: TOTP support
3. **API Keys**: For service-to-service communication
4. **Rate Limiting**: Per-user rate limits
5. **Token Blacklisting**: Revoke tokens on logout
6. **Session Management**: View/revoke active sessions