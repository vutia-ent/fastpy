# API Responses

Standard response formats for consistent API design.

## Response Structure

All API responses follow a consistent structure.

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE"
  }
}
```

### Paginated Response

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Response Helpers

### success_response

```python
from app.utils.responses import success_response

@router.post("/", status_code=201)
async def create_post(data: PostCreate, session: AsyncSession = Depends(get_session)):
    post = await PostController.create(session, data)
    return success_response(data=post, message="Post created successfully")
```

**Output:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "My Post",
    "body": "Content here"
  },
  "message": "Post created successfully"
}
```

### error_response

```python
from app.utils.responses import error_response

@router.get("/{id}")
async def get_post(id: int, session: AsyncSession = Depends(get_session)):
    post = await PostController.get_by_id(session, id)
    if not post:
        return error_response(
            message="Post not found",
            code="NOT_FOUND",
            status_code=404
        )
    return success_response(data=post)
```

**Output:**
```json
{
  "success": false,
  "error": {
    "message": "Post not found",
    "code": "NOT_FOUND"
  }
}
```

### paginated_response

```python
from app.utils.responses import paginated_response

@router.get("/")
async def get_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    result = await PostController.get_paginated(session, page, per_page)
    return paginated_response(
        items=result.items,
        page=result.page,
        per_page=result.per_page,
        total=result.total
    )
```

**Output:**
```json
{
  "success": true,
  "data": [
    {"id": 1, "title": "Post 1"},
    {"id": 2, "title": "Post 2"}
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Implementation

```python
# app/utils/responses.py

from typing import Any, Optional, List
from math import ceil
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "Success"
) -> dict:
    """Create a success response"""
    return {
        "success": True,
        "data": data,
        "message": message
    }


def error_response(
    message: str,
    code: str,
    status_code: int = 400,
    details: Optional[dict] = None
) -> JSONResponse:
    """Create an error response"""
    content = {
        "success": False,
        "error": {
            "message": message,
            "code": code
        }
    }
    if details:
        content["error"]["details"] = details

    return JSONResponse(status_code=status_code, content=content)


def paginated_response(
    items: List[Any],
    page: int,
    per_page: int,
    total: int
) -> dict:
    """Create a paginated response"""
    pages = ceil(total / per_page) if per_page > 0 else 0

    return {
        "success": True,
        "data": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1
        }
    }
```

---

## Response Models

### Pydantic Response Models

```python
from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Generic API response"""
    success: bool
    data: Optional[T] = None
    message: str = "Success"


class PaginationInfo(BaseModel):
    """Pagination metadata"""
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated API response"""
    success: bool = True
    data: List[T]
    pagination: PaginationInfo


class ErrorDetail(BaseModel):
    """Error detail"""
    message: str
    code: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error API response"""
    success: bool = False
    error: ErrorDetail
```

### Using Response Models

```python
@router.get("/", response_model=PaginatedResponse[PostRead])
async def get_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    result = await PostController.get_paginated(session, page, per_page)
    return paginated_response(
        items=result.items,
        page=result.page,
        per_page=result.per_page,
        total=result.total
    )
```

---

## HTTP Status Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

---

## Common Response Patterns

### List Response

```python
@router.get("/", response_model=List[PostRead])
async def get_posts(session: AsyncSession = Depends(get_session)):
    posts = await PostController.get_all(session)
    return posts  # FastAPI handles serialization
```

### Single Item Response

```python
@router.get("/{id}", response_model=PostRead)
async def get_post(id: int, session: AsyncSession = Depends(get_session)):
    post = await PostController.get_by_id(session, id)
    if not post:
        raise NotFoundException("Post not found")
    return post
```

### Create Response

```python
@router.post("/", response_model=PostRead, status_code=201)
async def create_post(
    data: PostCreate,
    session: AsyncSession = Depends(get_session)
):
    return await PostController.create(session, data)
```

### Delete Response

```python
@router.delete("/{id}")
async def delete_post(id: int, session: AsyncSession = Depends(get_session)):
    success = await PostController.delete(session, id)
    if not success:
        raise NotFoundException("Post not found")
    return {"message": "Post deleted successfully"}
```

---

## Validation Errors

Automatic from Pydantic:

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "String should have at most 200 characters",
      "type": "string_too_long"
    },
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## Next Steps

- [Exceptions](exceptions.md) - Error handling
- [Pagination](pagination.md) - Pagination utilities
- [Authentication](authentication.md) - Auth responses
