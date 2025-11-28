# Response Formatting

Standardized API responses for consistent client integration.

## Response Helpers

Import from `app/utils/responses.py`:

```python
from app.utils.responses import (
    success_response,
    error_response,
    paginated_response
)
```

## success_response

Return successful operation results.

```python
@router.get("/{id}")
async def get_user(id: int, session: AsyncSession = Depends(get_session)):
    user = await UserController.get_by_id(session, id)
    return success_response(data=user)
```

### Output

```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### With Message

```python
return success_response(
    data=user,
    message="User retrieved successfully"
)
```

```json
{
  "success": true,
  "data": {...},
  "message": "User retrieved successfully"
}
```

### List Data

```python
users = await UserController.get_all(session)
return success_response(data=users)
```

```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Jane"}
  ]
}
```

## error_response

Return error information.

```python
return error_response(
    message="User not found",
    code="NOT_FOUND",
    status_code=404
)
```

### Output

```json
{
  "success": false,
  "error": {
    "message": "User not found",
    "code": "NOT_FOUND"
  }
}
```

### With Details

```python
return error_response(
    message="Validation failed",
    code="VALIDATION_ERROR",
    status_code=422,
    details={
        "email": ["Invalid email format"],
        "password": ["Must be at least 8 characters"]
    }
)
```

```json
{
  "success": false,
  "error": {
    "message": "Validation failed",
    "code": "VALIDATION_ERROR",
    "details": {
      "email": ["Invalid email format"],
      "password": ["Must be at least 8 characters"]
    }
  }
}
```

## paginated_response

Return paginated list data.

```python
from app.utils.pagination import paginate, PaginationParams

@router.get("/")
async def list_users(
    page: int = 1,
    per_page: int = 20,
    session: AsyncSession = Depends(get_session)
):
    params = PaginationParams(page=page, per_page=per_page)
    result = await paginate(session, select(User), params)

    return paginated_response(
        items=result.items,
        page=result.page,
        per_page=result.per_page,
        total=result.total
    )
```

### Output

```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Jane"}
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

## Response Schemas

For API documentation, define response schemas:

```python
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: Optional[str] = None

class ErrorDetail(BaseModel):
    message: str
    code: str
    details: Optional[dict] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail

class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: List[T]
    meta: PaginationMeta
```

### Using in Routes

```python
@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users():
    ...

@router.get("/{id}", response_model=SuccessResponse[UserResponse])
async def get_user(id: int):
    ...
```

## HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Successful GET, PUT |
| 201 | Successful POST (created) |
| 204 | Successful DELETE (no content) |
| 400 | Bad request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not found |
| 409 | Conflict |
| 422 | Validation error |
| 429 | Rate limited |
| 500 | Server error |

## Best Practices

1. **Always use helpers** - Don't construct responses manually
2. **Include codes** - Error codes help clients handle errors programmatically
3. **Be consistent** - All endpoints should return the same structure
4. **Use appropriate status codes** - Match HTTP semantics
5. **Don't expose internals** - Hide stack traces in production
