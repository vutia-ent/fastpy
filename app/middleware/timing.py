"""
Request timing middleware for performance monitoring.
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.utils.logger import logger

TIMING_HEADER = "X-Response-Time"


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that measures request processing time.
    Adds X-Response-Time header to responses.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        process_time_ms = round(process_time * 1000, 2)

        # Add timing header
        response.headers[TIMING_HEADER] = f"{process_time_ms}ms"

        # Log slow requests (> 1 second)
        if process_time > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path}",
                extra={
                    "duration_ms": process_time_ms,
                    "method": request.method,
                    "path": str(request.url.path)
                }
            )

        return response
