# Middleware

Custom middleware components for request processing.

## Middleware Stack

Middleware is executed in order (last added runs first):

```python
# main.py
app.add_middleware(CORSMiddleware, ...)      # 1. CORS
app.add_middleware(RateLimitMiddleware, ...) # 2. Rate Limiting
app.add_middleware(TimingMiddleware)          # 3. Timing
app.add_middleware(RequestIDMiddleware)       # 4. Request ID
```

**Execution Order:**
```
Request → RequestID → Timing → RateLimit → CORS → Route → Response
```

---

## RequestIDMiddleware

Adds unique request ID for tracing.

### Features

- Generates UUID for each request
- Respects incoming `X-Request-ID` header
- Adds `X-Request-ID` to response
- Stores in context for logging

### Implementation

```python
# app/middleware/request_id.py

from uuid import uuid4
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid4()))

        # Store in context for logging
        request_id_var.set(request_id)

        # Process request
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Request-ID"] = request_id

        return response
```

### Usage in Logging

```python
from app.middleware.request_id import request_id_var

logger.info("Processing request", extra={"request_id": request_id_var.get()})
```

### Response Header

```
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

---

## TimingMiddleware

Tracks request processing time.

### Features

- Measures total request time
- Adds `X-Response-Time` header
- Logs slow requests (>1 second)

### Implementation

```python
# app/middleware/timing.py

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.utils.logger import logger


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Response-Time"] = f"{process_time:.3f}s"

        # Log slow requests
        if process_time > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path}",
                extra={
                    "duration": process_time,
                    "method": request.method,
                    "path": request.url.path
                }
            )

        return response
```

### Response Header

```
X-Response-Time: 0.045s
```

---

## RateLimitMiddleware

Sliding window rate limiting.

### Features

- In-memory rate limiting
- Configurable requests per window
- Per-client IP tracking
- Returns `429 Too Many Requests` when exceeded
- Adds rate limit headers

### Configuration

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Implementation

```python
# app/middleware/rate_limit.py

import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests: int = 100, window: int = 60):
        super().__init__(app)
        self.requests = requests
        self.window = window
        self.clients: dict = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_rate_limited(self, client_ip: str) -> tuple[bool, int]:
        now = time.time()
        window_start = now - self.window

        # Clean old requests
        self.clients[client_ip] = [
            t for t in self.clients[client_ip] if t > window_start
        ]

        # Check limit
        if len(self.clients[client_ip]) >= self.requests:
            return True, 0

        # Add current request
        self.clients[client_ip].append(now)
        remaining = self.requests - len(self.clients[client_ip])

        return False, remaining

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        is_limited, remaining = self._is_rate_limited(client_ip)

        if is_limited:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "message": "Too many requests",
                        "code": "RATE_LIMIT_EXCEEDED"
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + self.window)
                }
            )

        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time()) + self.window
        )

        return response
```

### Response Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699900000
```

### Rate Limit Exceeded Response

```json
{
  "success": false,
  "error": {
    "message": "Too many requests",
    "code": "RATE_LIMIT_EXCEEDED"
  }
}
```

---

## Creating Custom Middleware

Generate middleware with CLI:

```bash
python cli.py make:middleware CustomAuth
```

### Template

```python
# app/middleware/custom_auth_middleware.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CustomAuthMiddleware(BaseHTTPMiddleware):
    """Custom authentication middleware"""

    def __init__(self, app, **kwargs):
        super().__init__(app)
        # Initialize options from kwargs

    async def dispatch(self, request: Request, call_next) -> Response:
        # Before request processing
        # - Validate headers
        # - Check authentication
        # - Modify request

        response = await call_next(request)

        # After request processing
        # - Add headers
        # - Log response
        # - Modify response

        return response
```

### Registering Middleware

```python
# main.py

from app.middleware.custom_auth import CustomAuthMiddleware

app.add_middleware(
    CustomAuthMiddleware,
    secret_key=settings.secret_key,
    exclude_paths=["/health", "/docs"]
)
```

---

## Middleware Best Practices

### Order Matters

```python
# Correct order (inside out)
app.add_middleware(CORSMiddleware, ...)   # Outermost
app.add_middleware(RateLimitMiddleware, ...)
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)   # Innermost
```

### Performance

```python
# Avoid heavy operations
class OptimizedMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip for specific paths
        if request.url.path.startswith("/health"):
            return await call_next(request)

        # Process normally
        return await call_next(request)
```

### Error Handling

```python
class SafeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal error"}
            )
```

---

## CORS Configuration

Built-in CORS middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Configuration

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_ALLOW_CREDENTIALS=true
```

## Next Steps

- [Project Structure](structure.md) - Directory layout
- [Patterns](patterns.md) - Architectural patterns
- [Authentication](../api/authentication.md) - Auth middleware
