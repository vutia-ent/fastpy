"""
Request ID middleware for request tracing.
"""
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.utils.logger import request_id_var

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds a unique request ID to each request.
    The ID is available in the request state and response headers.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Get request ID from header or generate a new one
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        # Store in context variable for logging
        request_id_var.set(request_id)

        # Store in request state for access in routes
        request.state.request_id = request_id

        # Process the request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers[REQUEST_ID_HEADER] = request_id

        return response


def get_request_id(request: Request) -> str:
    """Get the request ID from the current request"""
    return getattr(request.state, "request_id", str(uuid.uuid4()))
