---
title: Exceptions
description: Custom exception classes and error handling
---

Fastpy provides custom exception classes that automatically format error responses.

## Available Exceptions

```python
from app.utils.exceptions import (
    NotFoundException,      # 404
    BadRequestException,    # 400
    UnauthorizedException,  # 401
    ForbiddenException,     # 403
    ConflictException,      # 409
    ValidationException,    # 422
    RateLimitException      # 429
)
```

## Usage

Simply raise an exception and Fastpy handles the response:

```python
from app.utils.exceptions import NotFoundException

@router.get("/{id}")
async def get_user(id: int, session: AsyncSession = Depends(get_session)):
    user = await UserController.get_by_id(session, id)
    if not user:
        raise NotFoundException("User not found")
    return success_response(data=user)
```

---

## Exception Reference

### NotFoundException

Resource not found (404).

```python
raise NotFoundException("User not found")
raise NotFoundException("Post with ID 123 not found")
```

**Response:**
```json
{
  "success": false,
  "error": {
    "message": "User not found",
    "code": "NOT_FOUND"
  }
}
```

### BadRequestException

Invalid request (400).

```python
raise BadRequestException("Invalid email format")
raise BadRequestException("Missing required field: name")
```

### UnauthorizedException

Authentication required (401).

```python
raise UnauthorizedException("Invalid credentials")
raise UnauthorizedException("Token expired")
```

### ForbiddenException

Permission denied (403).

```python
raise ForbiddenException("You don't have permission to access this resource")
raise ForbiddenException("Admin access required")
```

### ConflictException

Duplicate or conflict (409).

```python
raise ConflictException("Email already exists")
raise ConflictException("Username is taken")
```

### ValidationException

Validation failed (422).

```python
raise ValidationException("Password must be at least 8 characters")
raise ValidationException("Invalid date format")
```

### RateLimitException

Too many requests (429).

```python
raise RateLimitException("Rate limit exceeded. Try again later.")
```

---

## Creating Custom Exceptions

### Generate Exception

```bash
python cli.py make:exception PaymentFailed
```

### Manual Creation

```python
# app/exceptions/payment_failed.py
from app.utils.exceptions import AppException

class PaymentFailedException(AppException):
    def __init__(self, message: str = "Payment processing failed"):
        super().__init__(
            message=message,
            code="PAYMENT_FAILED",
            status_code=402
        )
```

### Usage

```python
from app.exceptions.payment_failed import PaymentFailedException

async def process_payment(order_id: int):
    try:
        # Process payment
        ...
    except PaymentGatewayError:
        raise PaymentFailedException("Unable to process payment")
```

---

## Global Exception Handler

Fastpy automatically handles all exceptions. The handler is registered in `main.py`:

```python
from app.utils.exceptions import app_exception_handler, AppException

app.add_exception_handler(AppException, app_exception_handler)
```

### Handling Unexpected Errors

Unhandled exceptions return a generic 500 error:

```json
{
  "success": false,
  "error": {
    "message": "Internal server error",
    "code": "INTERNAL_ERROR"
  }
}
```

In development mode (`DEBUG=true`), the full error details are included.

---

## Best Practices

1. **Be specific** - Use the most appropriate exception type
2. **Clear messages** - Write user-friendly error messages
3. **Don't expose internals** - Hide implementation details in production
4. **Log errors** - Use the logger for debugging

```python
from app.utils.logger import logger
from app.utils.exceptions import NotFoundException

async def get_user(id: int):
    user = await UserController.get_by_id(session, id)
    if not user:
        logger.warning(f"User not found: {id}")
        raise NotFoundException(f"User with ID {id} not found")
    return user
```
