---
title: Authentication
description: JWT authentication with access and refresh tokens
---

Fastpy uses JWT (JSON Web Tokens) for authentication with a dual-token system.

## Token Types

| Token | Lifetime | Purpose |
|-------|----------|---------|
| Access Token | 30 minutes | API authentication |
| Refresh Token | 7 days | Obtain new access tokens |

## Endpoints

### Register

```bash
POST /api/auth/register
```

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123"
}
```

### Login

```bash
POST /api/auth/login/json
```

```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

### Refresh Token

```bash
POST /api/auth/refresh
```

```json
{
  "refresh_token": "eyJ..."
}
```

### Get Current User

```bash
GET /api/auth/me
Authorization: Bearer <access_token>
```

### Change Password

```bash
POST /api/auth/change-password
Authorization: Bearer <access_token>
```

```json
{
  "current_password": "oldPassword",
  "new_password": "newSecurePassword"
}
```

### Logout

```bash
POST /api/auth/logout
Authorization: Bearer <access_token>
```

---

## Protecting Routes

### Using Dependency

```python
from fastapi import Depends
from app.utils.auth import get_current_active_user
from app.models.user import User

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": f"Hello, {current_user.name}"}
```

### Generated Protected Routes

When using `-p` flag:

```bash
python cli.py make:resource Post -p
```

Routes automatically require authentication:

```python
@router.post("/")
async def create_post(
    data: PostCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    ...
```

---

## Password Hashing

```python
from app.utils.auth import get_password_hash, verify_password

# Hash a password
hashed = get_password_hash("mypassword")

# Verify a password
is_valid = verify_password("mypassword", hashed)
```

---

## Configuration

```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

:::caution
Generate a secure secret key for production:
```bash
openssl rand -hex 32
```
:::

---

## Error Responses

### 401 Unauthorized

```json
{
  "success": false,
  "error": {
    "message": "Could not validate credentials",
    "code": "UNAUTHORIZED"
  }
}
```

### 403 Forbidden

```json
{
  "success": false,
  "error": {
    "message": "Not enough permissions",
    "code": "FORBIDDEN"
  }
}
```
