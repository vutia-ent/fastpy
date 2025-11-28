# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Production-ready FastAPI starter with SQLModel, PostgreSQL/MySQL support, JWT authentication with refresh tokens, MVC architecture, service/repository patterns, and FastCLI code generator. Features soft deletes, automatic timestamps, password hashing, rate limiting, structured logging, pagination, health checks, and comprehensive testing setup.

## Technology Stack

- **Framework**: FastAPI (async/await)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL OR MySQL (configurable via .env)
- **Authentication**: JWT with bcrypt password hashing + refresh tokens
- **Migrations**: Alembic
- **CLI**: FastCLI (Typer-based code generator with automatic validation)
- **Testing**: pytest + pytest-asyncio + factory-boy
- **Language**: Python 3.9+

## Development Commands

### Running the Application

```bash
# Run development server with auto-reload
uvicorn main:app --reload

# Run on specific host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Using CLI
python cli.py serve
python cli.py serve --host 0.0.0.0 --port 8000
```

### FastCLI - Code Generation

```bash
# List all available commands
python cli.py list

# Generate resources with field definitions
python cli.py make:model Post -f title:string:required,max:200 -f body:text:required -m
python cli.py make:controller Post
python cli.py make:route Post --protected
python cli.py make:resource Post -i -m -p  # Interactive mode, migration, protected

# Field definition syntax: name:type:rules
# Types: string, text, integer, float, boolean, datetime, email, url, json
#        uuid, decimal, money, percent, date, time, phone, slug, ip, color, file, image
# Rules: required, nullable, unique, index, max:N, min:N, foreign:table.column

# Additional generators
python cli.py make:service Post         # Create service class
python cli.py make:repository Post      # Create repository class
python cli.py make:middleware Auth      # Create middleware
python cli.py make:seeder Post          # Create database seeder
python cli.py make:test Post            # Create test file
python cli.py make:factory Post         # Create test factory
python cli.py make:enum Status          # Create enum
python cli.py make:exception NotFound   # Create custom exception
```

### Database Commands

```bash
# Migrations (via CLI)
python cli.py db:migrate -m "Create posts table"  # Create migration
python cli.py db:rollback                         # Rollback one migration
python cli.py db:rollback --steps 3               # Rollback multiple
python cli.py db:fresh                            # Drop all & re-migrate

# Migrations (via Alembic directly)
alembic revision --autogenerate -m "Description"
alembic upgrade head
alembic downgrade -1
alembic history

# Seeding
python cli.py db:seed                    # Run all seeders
python cli.py db:seed --seeder User      # Run specific seeder
python cli.py db:seed --count 50         # Create 50 records
```

### Route Management

```bash
# List all routes
python cli.py route:list
python cli.py route:list --tag Users      # Filter by tag
python cli.py route:list --method POST    # Filter by method
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_users.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_auth.py::test_login_success
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Type checking
mypy .
```

## Architecture

### Project Structure

```
app/
├── config/           # Application settings (settings.py)
├── controllers/      # Business logic (UserController, AuthController)
├── database/         # DB connection and session management
├── enums/            # Enum definitions
├── middleware/       # Custom middleware (request_id, timing, rate_limit)
├── models/           # SQLModel models (BaseModel, User)
├── repositories/     # Data access layer (BaseRepository)
├── routes/           # API route definitions
├── seeders/          # Database seeders
├── services/         # Business logic services (BaseService)
└── utils/            # Utilities (auth, logger, pagination, exceptions, responses)

tests/
├── conftest.py       # Pytest fixtures
├── factories.py      # Test data factories
├── test_auth.py      # Auth endpoint tests
├── test_health.py    # Health check tests
├── test_users.py     # User endpoint tests
└── test_root.py      # Root endpoint tests
```

### Key Architectural Patterns

1. **Base Model Pattern**: All models inherit from `BaseModel` which provides:
   - `id`, `created_at`, `updated_at`, `deleted_at`
   - Soft delete methods: `soft_delete()`, `restore()`, `is_deleted`
   - `touch()` method to update timestamps

2. **Controller Pattern**: Business logic separated into controllers
   - Controllers handle CRUD operations (e.g., `UserController`, `AuthController`)
   - Database queries managed in controllers
   - Routes call controller methods

3. **Service/Repository Pattern**: Optional layered architecture
   - `BaseRepository` - Generic CRUD operations with soft delete support
   - `BaseService` - Business logic with hooks (before_create, after_update, etc.)
   - Use for complex domains requiring separation of concerns

4. **Middleware Stack**:
   - `RequestIDMiddleware` - Adds X-Request-ID to requests/responses
   - `TimingMiddleware` - Adds X-Response-Time header, logs slow requests
   - `RateLimitMiddleware` - Sliding window rate limiting

5. **Dependency Injection**: Use `get_session()` for database sessions in routes

### Naming Conventions

- **Tables**: Plural, snake_case (`users`, `blog_posts`)
- **Columns**: snake_case (`created_at`, `email_verified_at`)
- **Models**: Singular, PascalCase (`User`, `BlogPost`)
- **Table name explicitly set**: `__tablename__ = "users"`

### Soft Deletes

- All models have `deleted_at` field
- Queries automatically filter out soft-deleted records in controllers
- Use `user.soft_delete()` instead of actual deletion
- Restore with `user.restore()`

## API Features

### Standard Response Format

```python
from app.utils.responses import success_response, error_response, paginated_response

# Success response
return success_response(data=user, message="User created")
# {"success": true, "data": {...}, "message": "User created"}

# Error response
return error_response(message="Not found", code="NOT_FOUND", status_code=404)
# {"success": false, "error": {"message": "Not found", "code": "NOT_FOUND"}}

# Paginated response
return paginated_response(items=users, page=1, per_page=20, total=100)
```

### Pagination

```python
from app.utils.pagination import paginate, PaginationParams

# In route
params = PaginationParams(page=1, per_page=20)
result = await paginate(session, select(User), params)
# result.items, result.total, result.pages, result.has_next, result.has_prev
```

### Custom Exceptions

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

# Raise exceptions - automatically handled by exception handlers
raise NotFoundException("User not found")
raise BadRequestException("Invalid email format")
raise ConflictException("Email already exists")
```

### Health Checks

- `GET /health/` - Basic health check
- `GET /health/ready` - Readiness check (includes DB connectivity)
- `GET /health/live` - Liveness probe
- `GET /health/info` - Service information

## Database Connection

### Multi-Database Support
- Supports PostgreSQL OR MySQL (configure in `.env`)
- Set `DB_DRIVER=postgresql` or `DB_DRIVER=mysql`
- Connection string in `.env`:
  - PostgreSQL: `DATABASE_URL=postgresql://user:pass@localhost:5432/db`
  - MySQL: `DATABASE_URL=mysql://user:pass@localhost:3306/db`
- Session management via dependency injection: `session: AsyncSession = Depends(get_session)`
- Auto-commit on success, auto-rollback on exception

## Authentication

### JWT Authentication with Refresh Tokens
- Access tokens (short-lived, default 30 minutes)
- Refresh tokens (long-lived, default 7 days)
- Token endpoints:
  - `POST /api/auth/register` - Create new user
  - `POST /api/auth/login` - Login (form data)
  - `POST /api/auth/login/json` - Login (JSON body)
  - `POST /api/auth/refresh` - Refresh access token
  - `GET /api/auth/me` - Get current user
  - `POST /api/auth/change-password` - Change password
  - `POST /api/auth/forgot-password` - Request password reset
  - `POST /api/auth/reset-password` - Reset password with token
  - `POST /api/auth/verify-email` - Verify email
  - `POST /api/auth/logout` - Logout

### Protect Routes
```python
from app.utils.auth import get_current_active_user

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"user": current_user}
```

### Password Hashing
```python
from app.utils.auth import get_password_hash, verify_password

# Hash password
hashed = get_password_hash("password123")

# Verify password
is_valid = verify_password("password123", hashed)
```

## Middleware

### Rate Limiting
Enabled via `RATE_LIMIT_ENABLED=true` in `.env`:
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Request ID
Automatically adds `X-Request-ID` header to all requests/responses for tracing.

### Timing
Adds `X-Response-Time` header and logs requests taking longer than 1 second.

## Logging

Structured logging with JSON or text format:
```python
from app.utils.logger import logger

logger.info("User created", extra={"user_id": user.id})
logger.error("Database error", extra={"error": str(e)})
```

Configure in `.env`:
```env
LOG_LEVEL=INFO
LOG_FORMAT=json  # or "text"
```

## CLI Tool

The `cli.py` provides comprehensive code generation and management:

```bash
# List all commands
python cli.py list

# Generate complete resource
python cli.py make:resource Post -m -p

# Database operations
python cli.py db:migrate -m "Add posts"
python cli.py db:seed --seeder User

# Server management
python cli.py serve --reload
python cli.py route:list
```

## Testing

### Test Structure
- `tests/conftest.py` - Fixtures (db_session, client, test_user, auth_headers)
- `tests/factories.py` - Test data factories
- Test files organized by feature (test_auth.py, test_users.py, etc.)

### Using Fixtures
```python
import pytest

@pytest.mark.asyncio
async def test_get_user(client, test_user, auth_headers):
    response = await client.get(f"/api/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 200
```

### Using Factories
```python
from tests.factories import UserFactory

user = UserFactory.build(name="Test User")
verified_user = UserFactory.build_verified()
users = UserFactory.build_batch(5)
```

## Important Notes

- Always use `async`/`await` for database operations
- Filter soft deletes in queries: `where(Model.deleted_at.is_(None))`
- Use `model.touch()` to update timestamps
- Import new models in `alembic/env.py` for migrations to detect them
- Passwords are automatically hashed in `AuthController` and `UserController`
- Use CLI to generate resources (faster than manual creation)
- Run tests with SQLite for speed: `pytest` (uses in-memory SQLite)

## Environment Variables

Key configuration options in `.env`:
```env
# Application
APP_NAME=Fastpy
ENVIRONMENT=development
DEBUG=true

# Database
DB_DRIVER=postgresql
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Authentication
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## User-Specific Instructions

- All table Actions should be in an ActionGroup
