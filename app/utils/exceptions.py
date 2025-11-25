"""
Custom exception classes and exception handlers.
"""
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from datetime import datetime, timezone
import traceback

from app.utils.logger import logger, request_id_var


class AppException(Exception):
    """Base application exception"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        errors: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.errors = errors
        self.headers = headers
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found exception"""

    def __init__(self, message: str = "Resource not found", resource: Optional[str] = None):
        super().__init__(
            message=f"{resource} not found" if resource else message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND"
        )


class BadRequestException(AppException):
    """Bad request exception"""

    def __init__(self, message: str = "Bad request", errors: Optional[List[str]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST",
            errors=errors
        )


class UnauthorizedException(AppException):
    """Unauthorized exception"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(AppException):
    """Forbidden exception"""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN"
        )


class ConflictException(AppException):
    """Conflict exception (e.g., duplicate entry)"""

    def __init__(self, message: str = "Conflict", resource: Optional[str] = None):
        super().__init__(
            message=f"{resource} already exists" if resource else message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT"
        )


class ValidationException(AppException):
    """Validation exception"""

    def __init__(self, message: str = "Validation error", errors: Optional[List[str]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            errors=errors
        )


class RateLimitException(AppException):
    """Rate limit exceeded exception"""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED"
        )


class ServiceUnavailableException(AppException):
    """Service unavailable exception"""

    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="SERVICE_UNAVAILABLE"
        )


def create_error_response(
    status_code: int,
    message: str,
    error_code: str,
    errors: Optional[List[str]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a standardized error response"""
    response = {
        "success": False,
        "message": message,
        "error_code": error_code,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    if errors:
        response["errors"] = errors

    if request_id:
        response["request_id"] = request_id

    return response


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle AppException"""
    request_id = request_id_var.get()

    logger.error(
        f"AppException: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "error_code": exc.error_code,
            "path": str(request.url.path)
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code,
            errors=exc.errors,
            request_id=request_id
        ),
        headers=exc.headers
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException"""
    request_id = request_id_var.get()

    logger.warning(
        f"HTTPException: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            error_code="HTTP_ERROR",
            request_id=request_id
        ),
        headers=getattr(exc, "headers", None)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors"""
    request_id = request_id_var.get()

    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")

    logger.warning(
        "Validation error",
        extra={
            "errors": errors,
            "path": str(request.url.path)
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation error",
            error_code="VALIDATION_ERROR",
            errors=errors,
            request_id=request_id
        )
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    request_id = request_id_var.get()

    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "traceback": traceback.format_exc(),
            "path": str(request.url.path)
        }
    )

    # Don't expose internal errors in production
    from app.config.settings import settings
    message = str(exc) if settings.debug else "Internal server error"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            error_code="INTERNAL_ERROR",
            request_id=request_id
        )
    )
