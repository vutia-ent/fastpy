"""
Standard API response formats for consistent API responses.
"""
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime, timezone

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(ge=1, description="Current page number")
    per_page: int = Field(ge=1, description="Items per page")
    total: int = Field(ge=0, description="Total number of items")
    pages: int = Field(ge=0, description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    success: bool = Field(description="Whether the request was successful")
    message: Optional[str] = Field(default=None, description="Response message")
    data: Optional[T] = Field(default=None, description="Response data")
    errors: Optional[List[str]] = Field(default=None, description="List of error messages")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation successful",
                "data": {"id": 1, "name": "Example"},
                "errors": None,
                "meta": None,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated API response"""
    success: bool = True
    message: Optional[str] = None
    data: List[T] = Field(default_factory=list)
    pagination: PaginationMeta
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ErrorResponse(BaseModel):
    """Error response format"""
    success: bool = False
    message: str
    errors: Optional[List[str]] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Validation error",
                "errors": ["Field 'email' is required"],
                "error_code": "VALIDATION_ERROR",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }


# Helper functions for creating responses
def success_response(
    data: Any = None,
    message: str = "Success",
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a success response"""
    return APIResponse(
        success=True,
        message=message,
        data=data,
        meta=meta
    ).model_dump()


def error_response(
    message: str,
    errors: Optional[List[str]] = None,
    error_code: Optional[str] = None
) -> Dict[str, Any]:
    """Create an error response"""
    return ErrorResponse(
        message=message,
        errors=errors,
        error_code=error_code
    ).model_dump()


def paginated_response(
    data: List[Any],
    page: int,
    per_page: int,
    total: int,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """Create a paginated response"""
    pages = (total + per_page - 1) // per_page if per_page > 0 else 0

    return PaginatedResponse(
        message=message,
        data=data,
        pagination=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )
    ).model_dump()
