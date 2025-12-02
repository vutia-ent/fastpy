# Authentication

Fastpy includes a complete JWT authentication system with refresh tokens.

## Overview

<div class="auth-overview">
  <div class="auth-card">
    <div class="auth-icon">🎫</div>
    <div class="auth-content">
      <h4>Access Tokens</h4>
      <p>Short-lived (30 min), for API access</p>
    </div>
  </div>
  <div class="auth-card">
    <div class="auth-icon">🔄</div>
    <div class="auth-content">
      <h4>Refresh Tokens</h4>
      <p>Long-lived (7 days), for renewal</p>
    </div>
  </div>
  <div class="auth-card">
    <div class="auth-icon">🔒</div>
    <div class="auth-content">
      <h4>Password Hashing</h4>
      <p>bcrypt with automatic salting</p>
    </div>
  </div>
</div>

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | `POST` | Create new user |
| `/api/auth/login` | `POST` | Login (form data, OAuth2 compatible) |
| `/api/auth/login/json` | `POST` | Login (JSON body) |
| `/api/auth/refresh` | `POST` | Refresh access token |
| `/api/auth/me` | `GET` | Get current user |
| `/api/auth/change-password` | `POST` | Change password |
| `/api/auth/forgot-password` | `POST` | Request password reset |
| `/api/auth/reset-password` | `POST` | Reset password |
| `/api/auth/verify-email` | `POST` | Verify email |
| `/api/auth/logout` | `POST` | Logout |

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

::: code-group

```bash [Form Data (OAuth2)]
# Works with Swagger UI's Authorize button
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=user@example.com&password=securepassword123"
```

```bash [JSON Body]
curl -X POST http://localhost:8000/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

:::

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

::: warning Important
Always follow these practices in production environments.
:::

<div class="security-grid">
  <div class="security-item">
    <span class="security-icon">🔐</span>
    <div class="security-content">
      <strong>Use HTTPS</strong>
      <p>Always use TLS/SSL in production</p>
    </div>
  </div>
  <div class="security-item">
    <span class="security-icon">🔑</span>
    <div class="security-content">
      <strong>Rotate SECRET_KEY</strong>
      <p>Change your secret key periodically</p>
    </div>
  </div>
  <div class="security-item">
    <span class="security-icon">⏱️</span>
    <div class="security-content">
      <strong>Short Token Lifetime</strong>
      <p>Keep access tokens to 15-30 minutes</p>
    </div>
  </div>
  <div class="security-item">
    <span class="security-icon">🍪</span>
    <div class="security-content">
      <strong>Secure Storage</strong>
      <p>Use httpOnly cookies for refresh tokens</p>
    </div>
  </div>
  <div class="security-item">
    <span class="security-icon">🚫</span>
    <div class="security-content">
      <strong>Token Blacklisting</strong>
      <p>Invalidate tokens on logout</p>
    </div>
  </div>
  <div class="security-item">
    <span class="security-icon">💪</span>
    <div class="security-content">
      <strong>Strong Passwords</strong>
      <p>Enforce minimum 8 characters</p>
    </div>
  </div>
</div>

<style>
.auth-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 24px 0;
}

.auth-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 10px;
}

.auth-icon {
  font-size: 1.5rem;
}

.auth-content h4 {
  margin: 0 0 4px;
  font-size: 0.95rem;
  font-weight: 600;
}

.auth-content p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
}

.security-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 14px;
  margin: 24px 0;
}

.security-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 8px;
}

.security-icon {
  font-size: 1.25rem;
}

.security-content strong {
  display: block;
  font-size: 0.9rem;
  margin-bottom: 2px;
}

.security-content p {
  margin: 0;
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
}
</style>
