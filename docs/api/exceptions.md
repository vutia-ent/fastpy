# Exceptions

Custom exception handling for consistent error responses.

## Built-in Exceptions

| Exception | Status Code | Code |
|-----------|-------------|------|
| `NotFoundException` | 404 | `NOT_FOUND` |
| `BadRequestException` | 400 | `BAD_REQUEST` |
| `UnauthorizedException` | 401 | `UNAUTHORIZED` |
| `ForbiddenException` | 403 | `FORBIDDEN` |
| `ConflictException` | 409 | `CONFLICT` |
| `ValidationException` | 422 | `VALIDATION_ERROR` |
| `RateLimitException` | 429 | `RATE_LIMIT_EXCEEDED` |

---

## Usage

### Raising Exceptions

```python
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException
)

@router.get("/{id}")
async def get_post(id: int, session: AsyncSession = Depends(get_session)):
    post = await PostController.get_by_id(session, id)
    if not post:
        raise NotFoundException("Post not found")
    return post

@router.post("/")
async def create_post(data: PostCreate, session: AsyncSession = Depends(get_session)):
    existing = await PostController.get_by_slug(session, data.slug)
    if existing:
        raise ConflictException("A post with this slug already exists")
    return await PostController.create(session, data)
```

### Response Format

```json
{
  "success": false,
  "error": {
    "message": "Post not found",
    "code": "NOT_FOUND"
  }
}
```

---

## Exception Classes

### Base Exception

```python
# app/utils/exceptions.py

class AppException(Exception):
    """Base application exception"""

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = 400,
        details: dict = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)
```

### NotFoundException

```python
class NotFoundException(AppException):
    """Resource not found exception"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404
        )
```

### BadRequestException

```python
class BadRequestException(AppException):
    """Bad request exception"""

    def __init__(self, message: str = "Bad request"):
        super().__init__(
            message=message,
            code="BAD_REQUEST",
            status_code=400
        )
```

### UnauthorizedException

```python
class UnauthorizedException(AppException):
    """Unauthorized exception"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401
        )
```

### ForbiddenException

```python
class ForbiddenException(AppException):
    """Forbidden exception"""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403
        )
```

### ConflictException

```python
class ConflictException(AppException):
    """Conflict exception"""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409
        )
```

### ValidationException

```python
class ValidationException(AppException):
    """Validation exception"""

    def __init__(self, message: str = "Validation failed", details: dict = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )
```

### RateLimitException

```python
class RateLimitException(AppException):
    """Rate limit exceeded exception"""

    def __init__(self, message: str = "Too many requests"):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429
        )
```

---

## Exception Handlers

### Global Handler Registration

```python
# main.py

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.utils.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

app = FastAPI()

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
```

### Handler Implementations

```python
# app/utils/exceptions.py

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions"""
    content = {
        "success": False,
        "error": {
            "message": exc.message,
            "code": exc.code
        }
    }
    if exc.details:
        content["error"]["details"] = exc.details

    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.detail,
                "code": "HTTP_ERROR"
            }
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """Handle Pydantic validation exceptions"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "message": "Validation failed",
                "code": "VALIDATION_ERROR",
                "details": errors
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "message": "Internal server error",
                "code": "INTERNAL_ERROR"
            }
        }
    )
```

---

## Creating Custom Exceptions

### Using CLI

```bash
python cli.py make:exception PostNotFound
```

### Generated Code

```python
# app/exceptions/post_not_found.py

from app.utils.exceptions import AppException


class PostNotFoundException(AppException):
    """Exception raised when post is not found"""

    def __init__(self, message: str = "Post not found"):
        super().__init__(
            message=message,
            code="POST_NOT_FOUND",
            status_code=404
        )
```

### Manual Creation

```python
# app/exceptions/payment.py

from app.utils.exceptions import AppException


class PaymentFailedException(AppException):
    """Payment processing failed"""

    def __init__(
        self,
        message: str = "Payment failed",
        transaction_id: str = None
    ):
        super().__init__(
            message=message,
            code="PAYMENT_FAILED",
            status_code=402,
            details={"transaction_id": transaction_id} if transaction_id else None
        )


class InsufficientFundsException(AppException):
    """Insufficient funds for transaction"""

    def __init__(self, required: float, available: float):
        super().__init__(
            message="Insufficient funds",
            code="INSUFFICIENT_FUNDS",
            status_code=402,
            details={
                "required": required,
                "available": available
            }
        )
```

---

## Error Response Examples

### Not Found

```json
{
  "success": false,
  "error": {
    "message": "Post not found",
    "code": "NOT_FOUND"
  }
}
```

### Validation Error

```json
{
  "success": false,
  "error": {
    "message": "Validation failed",
    "code": "VALIDATION_ERROR",
    "details": [
      {
        "field": "body.title",
        "message": "String should have at most 200 characters",
        "type": "string_too_long"
      }
    ]
  }
}
```

### Conflict

```json
{
  "success": false,
  "error": {
    "message": "A user with this email already exists",
    "code": "CONFLICT"
  }
}
```

### Rate Limit

```json
{
  "success": false,
  "error": {
    "message": "Too many requests. Please try again later.",
    "code": "RATE_LIMIT_EXCEEDED"
  }
}
```

---

## Best Practices

### Be Specific

```python
# Good
raise NotFoundException("User with ID 123 not found")

# Avoid
raise NotFoundException("Not found")
```

### Include Context

```python
raise ValidationException(
    message="Invalid order data",
    details={
        "items": "At least one item required",
        "shipping_address": "Address is required for physical items"
    }
)
```

### Don't Expose Internal Details

```python
# Good (production)
raise AppException("An error occurred processing your request")

# Avoid in production
raise AppException(f"Database error: {str(db_error)}")
```

## Next Steps

- [Responses](responses.md) - Response formats
- [Pagination](pagination.md) - Pagination handling
- [Authentication](authentication.md) - Auth errors
