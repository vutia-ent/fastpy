---
title: Project Structure
description: Understanding the Fastpy directory layout
---

## Directory Overview

```
fastpy/
├── app/
│   ├── config/           # Application settings
│   │   └── settings.py
│   ├── controllers/      # Business logic
│   │   ├── auth_controller.py
│   │   └── user_controller.py
│   ├── database/         # Database connection
│   │   └── connection.py
│   ├── enums/            # Enum definitions
│   ├── middleware/       # Custom middleware
│   │   ├── rate_limit.py
│   │   ├── request_id.py
│   │   └── timing.py
│   ├── models/           # SQLModel definitions
│   │   ├── base.py
│   │   └── user.py
│   ├── repositories/     # Data access layer
│   │   └── base_repository.py
│   ├── routes/           # API route definitions
│   │   ├── auth.py
│   │   ├── health.py
│   │   └── users.py
│   ├── seeders/          # Database seeders
│   ├── services/         # Business logic services
│   │   └── base_service.py
│   └── utils/            # Utilities
│       ├── auth.py
│       ├── exceptions.py
│       ├── logger.py
│       ├── pagination.py
│       └── responses.py
├── alembic/              # Database migrations
│   └── versions/
├── tests/                # Test files
│   ├── conftest.py
│   ├── factories.py
│   └── test_*.py
├── .env                  # Environment variables
├── .env.example          # Example environment file
├── main.py               # Application entry point
├── cli.py                # FastCLI commands
└── requirements.txt      # Python dependencies
```

## Key Directories

### app/config/

Application configuration using Pydantic Settings.

```python
from app.config.settings import settings

print(settings.app_name)
print(settings.database_url)
```

### app/controllers/

Business logic for handling requests. Controllers contain CRUD operations and data manipulation.

```python
from app.controllers.user_controller import UserController

users = await UserController.get_all(session)
```

### app/models/

SQLModel definitions with Pydantic validation.

```python
from app.models.base import BaseModel

class Post(BaseModel, table=True):
    __tablename__ = "posts"
    title: str
```

### app/routes/

FastAPI router definitions.

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_items():
    ...
```

### app/utils/

Shared utilities:
- `auth.py` - JWT and password hashing
- `exceptions.py` - Custom exception classes
- `logger.py` - Structured logging
- `pagination.py` - Pagination helpers
- `responses.py` - Standard response format

## File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Models | Singular, snake_case | `user.py`, `blog_post.py` |
| Controllers | Singular + `_controller` | `user_controller.py` |
| Routes | Plural, snake_case | `users.py`, `blog_posts.py` |
| Tests | `test_` + feature | `test_users.py` |
