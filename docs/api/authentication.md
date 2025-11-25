# Authentication

JWT-based authentication with access and refresh tokens.

## Overview

FastCLI uses JWT (JSON Web Tokens) for authentication:

- **Access tokens**: Short-lived (30 min default)
- **Refresh tokens**: Long-lived (7 days default)
- **Password hashing**: bcrypt

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Create new user |
| `/api/auth/login` | POST | Login (form data) |
| `/api/auth/login/json` | POST | Login (JSON body) |
| `/api/auth/refresh` | POST | Refresh access token |
| `/api/auth/me` | GET | Get current user |
| `/api/auth/change-password` | POST | Change password |
| `/api/auth/forgot-password` | POST | Request password reset |
| `/api/auth/reset-password` | POST | Reset password |
| `/api/auth/verify-email` | POST | Verify email |
| `/api/auth/logout` | POST | Logout |

---

## Registration

### Request

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### Response

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "email_verified_at": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Password Requirements

- Minimum 8 characters
- Maximum 72 characters (bcrypt limit)
- Must contain letter and digit

---

## Login

### Form Data (OAuth2)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=SecurePass123"
```

### JSON Body

```bash
curl -X POST http://localhost:8000/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

---

## Using Access Tokens

Include the token in the `Authorization` header:

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Token Structure

```json
{
  "sub": "john@example.com",
  "type": "access",
  "exp": 1699900000,
  "iat": 1699898200
}
```

---

## Refreshing Tokens

When the access token expires, use the refresh token:

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## Protected Routes

### Using Dependency Injection

```python
from app.utils.auth import get_current_active_user

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": f"Hello, {current_user.name}"}
```

### Generated Protected Routes

When using `-p` flag:

```bash
python cli.py make:route Post -p
```

Generated code:

```python
@router.get("/", response_model=List[PostRead])
async def get_posts(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)  # Protected
):
    return await PostController.get_all(session)
```

---

## Change Password

```bash
curl -X POST http://localhost:8000/api/auth/change-password \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPass123",
    "new_password": "NewSecurePass456"
  }'
```

---

## Password Reset Flow

### 1. Request Reset

```bash
curl -X POST http://localhost:8000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com"}'
```

Response (always success to prevent email enumeration):
```json
{
  "message": "If an account exists with this email, you will receive a password reset link."
}
```

### 2. Reset Password

```bash
curl -X POST http://localhost:8000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "reset-token-from-email",
    "email": "john@example.com",
    "new_password": "NewSecurePass789"
  }'
```

---

## Configuration

```env
# JWT Settings
SECRET_KEY=your-super-secret-key-at-least-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## Implementation Details

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### Token Creation

```python
from jose import jwt
from datetime import datetime, timedelta, timezone

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
```

### Token Validation

```python
from jose import jwt, JWTError

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await UserController.get_by_email(session, email)
    if user is None:
        raise credentials_exception
    return user
```

---

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

### Invalid Token

```json
{
  "success": false,
  "error": {
    "message": "Could not validate credentials",
    "code": "INVALID_TOKEN"
  }
}
```

## Next Steps

- [Responses](responses.md) - API response formats
- [Exceptions](exceptions.md) - Error handling
- [Middleware](../architecture/middleware.md) - Auth middleware
