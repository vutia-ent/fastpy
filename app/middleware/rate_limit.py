"""
Rate limiting middleware using in-memory storage.
For production, consider using Redis-based rate limiting.
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response, JSONResponse

from app.config.settings import settings
from app.utils.logger import logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter.
    Uses a sliding window algorithm.

    Note: For distributed systems, use Redis-based rate limiting.
    """

    def __init__(self, app, requests: int = 100, window: int = 60):
        super().__init__(app)
        self.requests = requests
        self.window = window
        # Store: {client_id: [(timestamp, count), ...]}
        self.clients: Dict[str, list] = defaultdict(list)

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Use X-Forwarded-For for proxied requests
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Fall back to client host
        if request.client:
            return request.client.host

        return "unknown"

    def _clean_old_requests(self, client_id: str, current_time: float) -> None:
        """Remove requests outside the current window"""
        cutoff = current_time - self.window
        self.clients[client_id] = [
            (ts, count) for ts, count in self.clients[client_id]
            if ts > cutoff
        ]

    def _get_request_count(self, client_id: str) -> int:
        """Get total requests in current window"""
        return sum(count for _, count in self.clients[client_id])

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip rate limiting if disabled
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Skip rate limiting for certain paths
        skip_paths = ["/health", "/docs", "/openapi.json", "/redoc"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)

        client_id = self._get_client_id(request)
        current_time = time.time()

        # Clean old requests
        self._clean_old_requests(client_id, current_time)

        # Check rate limit
        request_count = self._get_request_count(client_id)

        if request_count >= self.requests:
            logger.warning(
                f"Rate limit exceeded for client {client_id}",
                extra={"client_id": client_id, "request_count": request_count}
            )

            retry_after = self.window
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "message": "Rate limit exceeded. Please try again later.",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + retry_after))
                }
            )

        # Record this request
        self.clients[client_id].append((current_time, 1))

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = max(0, self.requests - request_count - 1)
        response.headers["X-RateLimit-Limit"] = str(self.requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window))

        return response


class RateLimiter:
    """
    Decorator-style rate limiter for specific endpoints.
    Usage:
        limiter = RateLimiter(requests=10, window=60)

        @app.get("/api/expensive")
        @limiter.limit
        async def expensive_endpoint():
            ...
    """

    def __init__(self, requests: int = 10, window: int = 60):
        self.requests = requests
        self.window = window
        self.clients: Dict[str, list] = defaultdict(list)

    def _get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    def _check_limit(self, client_id: str) -> Tuple[bool, int]:
        """Check if client is within rate limit. Returns (allowed, remaining)"""
        current_time = time.time()
        cutoff = current_time - self.window

        # Clean old requests
        self.clients[client_id] = [
            (ts, c) for ts, c in self.clients[client_id] if ts > cutoff
        ]

        count = sum(c for _, c in self.clients[client_id])

        if count >= self.requests:
            return False, 0

        return True, self.requests - count - 1

    async def check(self, request: Request) -> Tuple[bool, int]:
        """Check rate limit for a request"""
        client_id = self._get_client_id(request)
        allowed, remaining = self._check_limit(client_id)

        if allowed:
            self.clients[client_id].append((time.time(), 1))

        return allowed, remaining
