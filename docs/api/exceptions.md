# Exception Handling

Custom exceptions that automatically return proper HTTP responses.

## Built-in Exceptions

Import from `app/utils/exceptions.py`:

```python
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
    ValidationException,
    RateLimitException
)
```

## NotFoundException

Resource not found (404).

```python
@router.get("/{id}")
async def get_user(id: int, session: AsyncSession = Depends(get_session)):
    user = await UserController.get_by_id(session, id)
    if not user:
        raise NotFoundException("User not found")
    return success_response(data=user)
```

### Response

```json
{
  "success": false,
  "error": {
    "message": "User not found",
    "code": "NOT_FOUND"
  }
}
```

## BadRequestException

Invalid request (400).

```python
if not valid_email(data.email):
    raise BadRequestException("Invalid email format")
```

## UnauthorizedException

Authentication required (401).

```python
if not token:
    raise UnauthorizedException("Authentication required")
```

## ForbiddenException

Permission denied (403).

```python
if current_user.role != "admin":
    raise ForbiddenException("Admin access required")
```

## ConflictException

Resource conflict (409).

```python
existing = await UserController.get_by_email(session, data.email)
if existing:
    raise ConflictException("Email already registered")
```

## ValidationException

Validation errors (422).

```python
errors = validate_input(data)
if errors:
    raise ValidationException("Validation failed", details=errors)
```

### Response with Details

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

## RateLimitException

Rate limit exceeded (429).

```python
if is_rate_limited(client_ip):
    raise RateLimitException("Too many requests")
```

## Creating Custom Exceptions

Generate with CLI:

```bash
python cli.py make:exception PostNotFound
```

### Manual Creation

```python
# app/exceptions/post_exceptions.py
from app.utils.exceptions import BaseAPIException

class PostNotFoundException(BaseAPIException):
    def __init__(self, post_id: int = None):
        message = f"Post {post_id} not found" if post_id else "Post not found"
        super().__init__(
            message=message,
            code="POST_NOT_FOUND",
            status_code=404
        )

class PostAlreadyPublishedException(BaseAPIException):
    def __init__(self):
        super().__init__(
            message="Post is already published",
            code="POST_ALREADY_PUBLISHED",
            status_code=409
        )
```

### Usage

```python
from app.exceptions.post_exceptions import (
    PostNotFoundException,
    PostAlreadyPublishedException
)

@router.post("/{id}/publish")
async def publish_post(id: int, session: AsyncSession = Depends(get_session)):
    post = await PostController.get_by_id(session, id)

    if not post:
        raise PostNotFoundException(id)

    if post.published:
        raise PostAlreadyPublishedException()

    await PostController.publish(session, post)
    return success_response(data=post)
```

## Exception Handler

Exceptions are handled automatically by the global handler:

```python
# app/utils/exceptions.py
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "code": exc.code,
                "details": exc.details
            }
        }
    )
```

## Handling Unexpected Errors

```python
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the error
    logger.error(f"Unexpected error: {exc}", exc_info=True)

    # Return generic error in production
    if settings.environment == "production":
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "message": "An unexpected error occurred",
                    "code": "INTERNAL_ERROR"
                }
            }
        )

    # Return detailed error in development
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "message": str(exc),
                "code": "INTERNAL_ERROR"
            }
        }
    )
```

## Best Practices

1. **Use specific exceptions** - Not just generic errors
2. **Include context** - IDs, field names, etc.
3. **Don't expose internals** - Hide stack traces in production
4. **Log errors** - Especially 500 errors
5. **Use error codes** - Help clients handle errors programmatically
