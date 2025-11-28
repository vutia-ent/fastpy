# Middleware

Built-in middleware for common cross-cutting concerns.

## Included Middleware

Fastpy includes three middleware components:

1. **RequestIDMiddleware** - Request tracing
2. **TimingMiddleware** - Performance monitoring
3. **RateLimitMiddleware** - Rate limiting

## RequestIDMiddleware

Adds a unique request ID to every request for tracing.

### Behavior

- Generates UUID for each request
- Adds `X-Request-ID` header to response
- Available in request state: `request.state.request_id`

### Implementation

```python
# app/middleware/request_id.py
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response
```

### Usage in Logging

```python
from app.utils.logger import logger

@router.get("/")
async def list_items(request: Request):
    logger.info(
        "Listing items",
        extra={"request_id": request.state.request_id}
    )
```

## TimingMiddleware

Measures and logs request processing time.

### Behavior

- Adds `X-Response-Time` header (in milliseconds)
- Logs slow requests (>1 second) as warnings
- Includes request details in logs

### Implementation

```python
# app/middleware/timing.py
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = (time.time() - start_time) * 1000
        response.headers["X-Response-Time"] = f"{duration:.2f}ms"

        if duration > 1000:
            logger.warning(
                f"Slow request: {request.method} {request.url.path}",
                extra={"duration_ms": duration}
            )

        return response
```

## RateLimitMiddleware

Sliding window rate limiting.

### Configuration

```bash
# .env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Behavior

- Limits requests per IP address
- Uses sliding window algorithm
- Returns 429 Too Many Requests when exceeded
- Adds headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

### Implementation

```python
# app/middleware/rate_limit.py
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests: int = 100, window: int = 60):
        super().__init__(app)
        self.requests = requests
        self.window = window
        self.clients: Dict[str, List[float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()

        # Clean old requests
        if client_ip in self.clients:
            self.clients[client_ip] = [
                t for t in self.clients[client_ip]
                if now - t < self.window
            ]
        else:
            self.clients[client_ip] = []

        # Check limit
        if len(self.clients[client_ip]) >= self.requests:
            raise RateLimitException()

        self.clients[client_ip].append(now)
        response = await call_next(request)

        # Add headers
        response.headers["X-RateLimit-Limit"] = str(self.requests)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests - len(self.clients[client_ip])
        )

        return response
```

## Creating Custom Middleware

Generate middleware with CLI:

```bash
python cli.py make:middleware MyCustom
```

### Template

```python
# app/middleware/my_custom.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class MyCustomMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, **kwargs):
        super().__init__(app)
        # Store configuration

    async def dispatch(self, request: Request, call_next):
        # Before request
        # ...

        response = await call_next(request)

        # After response
        # ...

        return response
```

### Example: API Key Middleware

```python
class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str, exclude_paths: list = None):
        super().__init__(app)
        self.api_key = api_key
        self.exclude_paths = exclude_paths or ["/health", "/docs"]

    async def dispatch(self, request: Request, call_next):
        # Skip excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Check API key
        key = request.headers.get("X-API-Key")
        if key != self.api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid API key"}
            )

        return await call_next(request)
```

## Registering Middleware

Add middleware in `app/middleware/__init__.py`:

```python
def register_middleware(app: FastAPI):
    # Order matters: last added = first executed
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

## Middleware Order

Middleware executes in reverse order of registration:

```
1. CORS
2. RequestID
3. Timing
4. RateLimit
5. Your Route Handler
```
