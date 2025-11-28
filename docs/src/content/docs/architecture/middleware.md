---
title: Middleware
description: Built-in middleware and how to create custom middleware
---

## Built-in Middleware

Fastpy includes three middleware components that run on every request.

### Request ID Middleware

Adds a unique `X-Request-ID` header to all requests and responses for tracing.

```python
# In main.py
from app.middleware.request_id import RequestIDMiddleware

app.add_middleware(RequestIDMiddleware)
```

**Headers:**
- Request: `X-Request-ID` (generated if not provided)
- Response: `X-Request-ID` (same value)

### Timing Middleware

Measures request duration and adds `X-Response-Time` header.

```python
from app.middleware.timing import TimingMiddleware

app.add_middleware(TimingMiddleware)
```

**Features:**
- Adds `X-Response-Time` header (in milliseconds)
- Logs slow requests (>1 second) as warnings

### Rate Limit Middleware

Implements sliding window rate limiting.

```python
from app.middleware.rate_limit import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware)
```

**Configuration (via .env):**
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

**Response when limited:**
```json
{
  "success": false,
  "error": {
    "message": "Rate limit exceeded",
    "code": "RATE_LIMIT_EXCEEDED"
  }
}
```

---

## Middleware Stack Order

Middleware executes in reverse order of registration:

```python
# main.py
app.add_middleware(RateLimitMiddleware)   # 3rd (innermost)
app.add_middleware(TimingMiddleware)       # 2nd
app.add_middleware(RequestIDMiddleware)    # 1st (outermost)
```

Request flow: `RequestID → Timing → RateLimit → Route → RateLimit → Timing → RequestID`

---

## Creating Custom Middleware

### Generate Middleware

```bash
python cli.py make:middleware Logging
```

### Structure

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Before request
        print(f"Request: {request.method} {request.url}")

        # Process request
        response = await call_next(request)

        # After request
        print(f"Response: {response.status_code}")

        return response
```

### Register Middleware

```python
# main.py
from app.middleware.logging import LoggingMiddleware

app.add_middleware(LoggingMiddleware)
```

---

## Example: Authentication Logging

```python
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import logger


class AuthLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check for auth header
        auth_header = request.headers.get("Authorization")

        if auth_header:
            logger.info(
                "Authenticated request",
                extra={
                    "path": str(request.url.path),
                    "method": request.method,
                }
            )

        response = await call_next(request)

        # Log failed auth attempts
        if response.status_code == 401:
            logger.warning(
                "Authentication failed",
                extra={
                    "path": str(request.url.path),
                    "ip": request.client.host,
                }
            )

        return response
```

---

## CORS Middleware

CORS is configured in `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Configuration:**
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_ALLOW_CREDENTIALS=true
```
