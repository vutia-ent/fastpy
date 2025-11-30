# Authentication

Fastpy includes a complete JWT authentication system with refresh tokens.

## Overview

- **Access Tokens** - Short-lived (30 min default), for API access
- **Refresh Tokens** - Long-lived (7 days default), for token renewal
- **Password Hashing** - bcrypt with automatic salting

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Create new user |
| `/api/auth/login` | POST | Login (JSON body) |
| `/api/auth/login/form` | POST | Login (form data, OAuth2 compatible) |
| `/api/auth/refresh` | POST | Refresh access token |
| `/api/auth/me` | GET | Get current user |
| `/api/auth/change-password` | POST | Change password |
| `/api/auth/forgot-password` | POST | Request password reset |
| `/api/auth/reset-password` | POST | Reset password |
| `/api/auth/verify-email` | POST | Verify email |
| `/api/auth/logout` | POST | Logout |

## Registration

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "name": "John Doe"
  }'
```

**Response:**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe"
    },
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer"
  }
}
```

## Login

### JSON Body (Default)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Form Data (OAuth2 Compatible)

```bash
curl -X POST http://localhost:8000/api/auth/login/form \
  -d "username=user@example.com&password=securepassword123"
```

**Response:**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

## Refresh Token

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ..."
  }'
```

## Protected Routes

### Using the Auth Dependency

```python
from app.utils.auth import get_current_active_user
from app.models.user import User

@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    return success_response(data=current_user)
```

### Making API Requests

```bash
curl http://localhost:8000/api/users \
  -H "Authorization: Bearer eyJ..."
```

## Configuration

```bash
# .env
SECRET_KEY=your-super-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Password Utilities

### Hashing

```python
from app.utils.auth import get_password_hash

hashed = get_password_hash("mypassword")
```

### Verification

```python
from app.utils.auth import verify_password

is_valid = verify_password("mypassword", hashed_password)
```

## Token Structure

### Access Token Payload

```json
{
  "sub": "1",
  "email": "user@example.com",
  "type": "access",
  "exp": 1704067200,
  "iat": 1704065400
}
```

### Refresh Token Payload

```json
{
  "sub": "1",
  "type": "refresh",
  "exp": 1704672000,
  "iat": 1704065400
}
```

## Error Responses

### Invalid Credentials

```json
{
  "success": false,
  "error": {
    "message": "Invalid email or password",
    "code": "INVALID_CREDENTIALS"
  }
}
```

### Token Expired

```json
{
  "success": false,
  "error": {
    "message": "Token has expired",
    "code": "TOKEN_EXPIRED"
  }
}
```

### Unauthorized

```json
{
  "success": false,
  "error": {
    "message": "Not authenticated",
    "code": "UNAUTHORIZED"
  }
}
```

## Security Best Practices

1. **Use HTTPS** in production
2. **Rotate SECRET_KEY** periodically
3. **Short access token lifetime** (15-30 minutes)
4. **Store refresh tokens securely** (httpOnly cookies or secure storage)
5. **Implement token blacklisting** for logout
6. **Use strong passwords** (min 8 characters)
