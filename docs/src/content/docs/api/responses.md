---
title: API Responses
description: Standard response format for all API endpoints
---

Fastpy uses a consistent response format across all endpoints.

## Response Format

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

Import from `app.utils.responses`:

```python
from app.utils.responses import (
    success_response,
    error_response,
    paginated_response
)
```

### success_response

```python
@router.get("/{id}")
async def get_user(id: int, session: AsyncSession = Depends(get_session)):
    user = await UserController.get_by_id(session, id)
    if not user:
        raise NotFoundException("User not found")
    return success_response(data=user, message="User retrieved")
```

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `data` | Any | Response data |
| `message` | str | Optional message |
| `status_code` | int | HTTP status (default: 200) |

### error_response

```python
return error_response(
    message="Invalid email format",
    code="VALIDATION_ERROR",
    status_code=422
)
```

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `message` | str | Error message |
| `code` | str | Error code |
| `status_code` | int | HTTP status |

### paginated_response

```python
@router.get("/")
async def list_users(
    page: int = 1,
    per_page: int = 20,
    session: AsyncSession = Depends(get_session)
):
    result = await paginate(session, select(User), PaginationParams(page, per_page))
    return paginated_response(
        items=result.items,
        page=result.page,
        per_page=result.per_page,
        total=result.total
    )
```

---

## HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate entry |
| 422 | Unprocessable | Validation failed |
| 429 | Too Many Requests | Rate limited |
| 500 | Server Error | Internal error |

---

## Example Responses

### Create User (201)

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "message": "User created successfully"
}
```

### List Users (200)

```json
{
  "success": true,
  "data": [
    { "id": 1, "name": "John", "email": "john@example.com" },
    { "id": 2, "name": "Jane", "email": "jane@example.com" }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 2,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### Not Found (404)

```json
{
  "success": false,
  "error": {
    "message": "User not found",
    "code": "NOT_FOUND"
  }
}
```

### Validation Error (422)

```json
{
  "success": false,
  "error": {
    "message": "Validation failed",
    "code": "VALIDATION_ERROR",
    "details": [
      { "field": "email", "message": "Invalid email format" },
      { "field": "password", "message": "Must be at least 8 characters" }
    ]
  }
}
```
