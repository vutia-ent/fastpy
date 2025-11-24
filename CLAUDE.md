# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Production-ready FastAPI starter with SQLModel, PostgreSQL/MySQL support, JWT authentication, MVC architecture, and FastCLI code generator. Features soft deletes, automatic timestamps, password hashing, intelligent field validation, and clean folder structure.

## Technology Stack

- **Framework**: FastAPI (async/await)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL OR MySQL (configurable via .env)
- **Authentication**: JWT with bcrypt password hashing
- **Migrations**: Alembic
- **CLI**: FastCLI (Typer-based code generator with automatic validation)
- **Language**: Python 3.9+

## Development Commands

### Running the Application

```bash
# Run development server with auto-reload
uvicorn main:app --reload

# Run on specific host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### FastCLI - Code Generation

```bash
# List all available commands
python cli.py list
# Or after install: fastcli list

# Generate resources with field definitions
fastcli make:model Post -f title:string:required,max:200 -f body:text:required -m
fastcli make:controller Post
fastcli make:route Post --protected
fastcli make:resource Post -i -m -p  # Interactive mode, migration, protected

# Field definition syntax: name:type:rules
# Types: string, text, integer, float, boolean, datetime, email, url, json
# Rules: required, nullable, unique, index, max:N, min:N, foreign:table.column
```

### Database Migrations

```bash
# Create migration after model changes
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_users.py

# Run with coverage
pytest --cov=app --cov-report=html
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

### MVC Architecture

```
app/
├── config/       # Application settings (settings.py)
├── controllers/  # Business logic (UserController, AuthController)
├── database/     # DB connection and session management
├── models/       # SQLModel models (BaseModel, User)
├── routes/       # API route definitions (user_routes, auth_routes)
├── middleware/   # Custom middleware
└── utils/        # Utilities (auth.py for JWT & password hashing)
```

### Key Architectural Patterns

1. **Base Model Pattern**: All models inherit from `BaseModel` which provides:
   - `id`, `created_at`, `updated_at`, `deleted_at`
   - Soft delete methods: `soft_delete()`, `restore()`, `is_deleted`

2. **Controller Pattern**: Business logic separated into controllers
   - Controllers handle CRUD operations (e.g., `UserController`, `AuthController`)
   - Database queries managed in controllers
   - Routes call controller methods

3. **Dependency Injection**: Use `get_session()` for database sessions in routes

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

## Creating New Features

### Adding a New Model

1. Create model file in `app/models/new_model.py`:
```python
from sqlmodel import Field
from app.models.base import BaseModel

class Post(BaseModel, table=True):
    __tablename__ = "posts"
    title: str = Field(nullable=False, max_length=255)
    content: str = Field(nullable=False)
    user_id: int = Field(foreign_key="users.id")
```

2. Import in `alembic/env.py`:
```python
from app.models.new_model import Post  # noqa
```

3. Create migration:
```bash
alembic revision --autogenerate -m "Create posts table"
alembic upgrade head
```

### Adding a New Controller

Create in `app/controllers/`:
```python
from app.models.your_model import YourModel

class YourController:
    @staticmethod
    async def get_all(session: AsyncSession):
        query = select(YourModel).where(YourModel.deleted_at.is_(None))
        result = await session.execute(query)
        return result.scalars().all()
```

### Adding Routes

Create in `app/routes/` and register in `main.py`:
```python
# In main.py
from app.routes.your_routes import router as your_router
app.include_router(your_router, prefix="/api/your-resource", tags=["YourResource"])
```

## Database Connection

### Multi-Database Support
- Supports PostgreSQL OR MySQL (configure in `.env`)
- Set `DB_DRIVER=postgresql` or `DB_DRIVER=mysql`
- Connection string in `.env`:
  - PostgreSQL: `DATABASE_URL=postgresql://user:pass@localhost:5432/db`
  - MySQL: `DATABASE_URL=mysql://user:pass@localhost:3306/db`
- Session management via dependency injection: `session: AsyncSession = Depends(get_session)`

## Authentication

### JWT Authentication
- JWT tokens for authentication (`app/utils/auth.py`)
- Password hashing with bcrypt (`passlib`)
- Auth endpoints: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`
- Protect routes with: `current_user: User = Depends(get_current_active_user)`

### Password Hashing
```python
from app.utils.auth import get_password_hash, verify_password

# Hash password
hashed = get_password_hash("password123")

# Verify password
is_valid = verify_password("password123", hashed)
```

## CLI Tool

The `cli.py` provides powerful code generation:

```bash
# Use the CLI directly
python cli.py make:model BlogPost --migration
python cli.py make:controller BlogPost
python cli.py make:route BlogPost
python cli.py make:resource BlogPost -m  # Creates all at once

# After install (pip install -e .), use 'artisan' command
fastcli make:resource Post -m
```

## Important Notes

- Always use `async`/`await` for database operations
- Filter soft deletes in queries: `where(Model.deleted_at.is_(None))`
- Update `updated_at` manually when modifying records: `model.updated_at = datetime.utcnow()`
- Import new models in `alembic/env.py` for migrations to detect them
- Passwords are automatically hashed in `AuthController` and `UserController`
- Use CLI to generate resources (faster than manual creation)

## User-Specific Instructions

- All table Actions should be in an ActionGroup
