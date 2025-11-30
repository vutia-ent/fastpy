# Fastpy

A production-ready FastAPI starter template with SQLModel, PostgreSQL/MySQL support, JWT authentication with refresh tokens, MVC architecture, service/repository patterns, and comprehensive tooling. Features **FastCLI** - an intelligent code generator with 20+ commands, automatic validation, and AI assistant integration.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-00C7B7.svg)](https://fastapi.tiangolo.com)
[![SQLModel](https://img.shields.io/badge/SQLModel-0.0.22-red.svg)](https://sqlmodel.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Table of Contents

- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [FastCLI Commands](#-fastcli---code-generation)
- [API Features](#-api-features)
- [Architecture](#-architecture)
- [Authentication](#-authentication)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)

## Key Features

### FastCLI - Intelligent Code Generator
- **20+ Commands**: Models, controllers, routes, services, repositories, middleware, tests, factories, seeders, enums, exceptions
- **Field-based generation**: Define models with simple syntax: `title:string:required,max:200`
- **15+ Field Types**: string, text, integer, float, boolean, datetime, email, url, json, uuid, decimal, money, date, time, phone, slug, ip, color, file, image
- **Automatic validation**: Pydantic rules generated from field definitions
- **AI Integration**: Generate config files for Claude, Copilot, Gemini, Cursor
- **Interactive mode**: Guided field creation with prompts
- **Database commands**: Migrate, rollback, fresh, seed
- **Server management**: Serve, route listing

### Database & ORM
- **SQLModel** (SQLAlchemy + Pydantic) for type-safe models
- **PostgreSQL OR MySQL** support (configurable via .env)
- **Alembic** migrations with auto-generation
- **Soft deletes** via `deleted_at` timestamp
- **Auto timestamps**: `created_at`, `updated_at` on all models
- **Async operations**: Full async/await support
- **Connection pooling**: Environment-based pool configuration

### Authentication & Security
- **JWT tokens** with access + refresh token rotation
- **Bcrypt** password hashing (compatible versions)
- **Protected routes** with dependency injection
- **Rate limiting** middleware (sliding window)
- **CORS** middleware configured
- **Password validation**: Min 8, max 72 characters with complexity rules

### API Features
- **Health checks**: `/health/`, `/health/ready`, `/health/live`, `/health/info`
- **Standard responses**: Consistent API response format
- **Pagination**: Built-in pagination utilities with sorting
- **Exception handling**: Custom exceptions with global handlers
- **Request tracking**: X-Request-ID middleware
- **Performance monitoring**: X-Response-Time middleware

### Architecture & Code Quality
- **MVC pattern**: Models, Controllers, Routes separation
- **Service/Repository pattern**: Optional layered architecture
- **Base model**: Automatic id, timestamps, soft deletes
- **Testing**: pytest with async support, fixtures, factories
- **Code quality**: black, ruff, mypy, pre-commit hooks
- **Structured logging**: JSON/text format with context

## Prerequisites

- Python 3.9 or higher
- PostgreSQL 12+ OR MySQL 5.7+ (MySQL 8.0+ recommended)
- pip

## Quick Start

```bash
# Clone and setup
git clone https://github.com/vutia-ent/fastpy.git && cd fastpy
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Start the development server
python cli.py serve
# Or: uvicorn main:app --reload
```

Visit: http://localhost:8000/docs

### Generate Resources

```bash
# Generate a resource with FastCLI
python cli.py make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -f author_id:integer:foreign:users.id \
  -m -p

# Run migrations
alembic upgrade head
```

## FastCLI - Code Generation

### Available Commands

```bash
# List all commands
python cli.py list

# Server Management
python cli.py serve                    # Start development server
python cli.py serve --host 0.0.0.0     # Custom host
python cli.py route:list               # List all routes
python cli.py route:list --tag Users   # Filter by tag

# Database Commands
python cli.py db:migrate -m "Add posts"  # Create migration
python cli.py db:rollback                # Rollback one migration
python cli.py db:rollback --steps 3      # Rollback multiple
python cli.py db:fresh                   # Drop all & re-migrate
python cli.py db:seed                    # Run all seeders
python cli.py db:seed --seeder User      # Run specific seeder

# Resource Generation
python cli.py make:model Post -f title:string:required -m
python cli.py make:controller Post
python cli.py make:route Post --protected
python cli.py make:resource Post -i -m -p  # All at once

# Additional Generators
python cli.py make:service Post          # Service class
python cli.py make:repository Post       # Repository class
python cli.py make:middleware Auth       # Middleware
python cli.py make:seeder Post           # Database seeder
python cli.py make:test Post             # Test file
python cli.py make:factory Post          # Test factory
python cli.py make:enum Status           # Enum class
python cli.py make:exception NotFound    # Custom exception

# AI Assistant Config
python cli.py init:ai claude             # Claude Code
python cli.py init:ai copilot            # GitHub Copilot
python cli.py init:ai cursor             # Cursor AI
```

### Field Definition Syntax

**Format:** `name:type:rules`

**Field Types:**
| Type | Description | Example |
|------|-------------|---------|
| `string` | Short text (max 255) | `title:string:required,max:200` |
| `text` | Long text | `body:text:required` |
| `integer` | Whole numbers | `count:integer:required,ge:0` |
| `float` | Decimal numbers | `price:float:required,ge:0` |
| `boolean` | True/False | `published:boolean:required` |
| `datetime` | Date and time | `published_at:datetime:nullable` |
| `email` | Email with validation | `contact:email:required,unique` |
| `url` | URL string | `website:url:nullable` |
| `json` | JSON data | `metadata:json:nullable` |
| `uuid` | UUID field | `uuid:uuid:required,unique` |
| `decimal` | Precise decimal | `amount:decimal:required` |
| `money` | Currency amount | `price:money:required` |
| `date` | Date only | `birth_date:date:nullable` |
| `time` | Time only | `start_time:time:required` |
| `phone` | Phone number | `phone:phone:nullable` |
| `slug` | URL slug | `slug:slug:required,unique` |
| `ip` | IP address | `ip_address:ip:nullable` |
| `color` | Hex color | `theme_color:color:nullable` |
| `file` | File path | `document:file:nullable` |
| `image` | Image path | `avatar:image:nullable` |

**Validation Rules:**
| Rule | Description | Example |
|------|-------------|---------|
| `required` | Cannot be null | `title:string:required` |
| `nullable` | Can be null | `bio:text:nullable` |
| `unique` | Unique constraint | `email:email:unique` |
| `index` | Database index | `status:string:index` |
| `max:N` | Maximum length/value | `title:string:max:200` |
| `min:N` | Minimum length/value | `body:text:min:50` |
| `ge:N` / `gte:N` | Greater than or equal | `price:float:ge:0` |
| `le:N` / `lte:N` | Less than or equal | `rating:integer:le:5` |
| `gt:N` | Greater than | `age:integer:gt:0` |
| `lt:N` | Less than | `discount:float:lt:100` |
| `foreign:table.col` | Foreign key | `user_id:integer:foreign:users.id` |

### Real-World Examples

**Blog System:**
```bash
python cli.py make:resource Post \
  -f title:string:required,max:200,min:5 \
  -f slug:slug:required,unique \
  -f body:text:required,min:50 \
  -f excerpt:text:nullable,max:500 \
  -f published_at:datetime:nullable \
  -f author_id:integer:required,foreign:users.id \
  -m -p
```

**E-commerce Product:**
```bash
python cli.py make:resource Product \
  -f name:string:required,max:255 \
  -f description:text:nullable \
  -f price:money:required,ge:0 \
  -f stock:integer:required,ge:0 \
  -f sku:string:required,unique,max:50 \
  -f image:image:nullable \
  -f category_id:integer:required,foreign:categories.id \
  -m -p
```

**User Profile:**
```bash
python cli.py make:resource Profile \
  -f user_id:integer:required,unique,foreign:users.id \
  -f bio:text:nullable,max:1000 \
  -f avatar:image:nullable \
  -f website:url:nullable \
  -f phone:phone:nullable \
  -m -p
```

## API Features

### Standard Response Format

All API responses follow a consistent format:

```json
// Success
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}

// Error
{
  "success": false,
  "error": {
    "message": "Not found",
    "code": "NOT_FOUND"
  }
}

// Paginated
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

### Health Checks

| Endpoint | Description |
|----------|-------------|
| `GET /health/` | Basic health check |
| `GET /health/ready` | Readiness (includes DB check) |
| `GET /health/live` | Liveness probe |
| `GET /health/info` | Service information |

### Custom Exceptions

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

raise NotFoundException("User not found")
raise ConflictException("Email already exists")
```

## Architecture

### Project Structure

```
app/
├── config/           # Application settings
├── controllers/      # Business logic
├── database/         # DB connection & session
├── enums/            # Enum definitions
├── middleware/       # Custom middleware
│   ├── request_id.py   # X-Request-ID tracking
│   ├── timing.py       # X-Response-Time header
│   └── rate_limit.py   # Sliding window rate limiting
├── models/           # SQLModel models
├── repositories/     # Data access layer
├── routes/           # API route definitions
├── seeders/          # Database seeders
├── services/         # Business logic services
└── utils/
    ├── auth.py         # JWT & password hashing
    ├── exceptions.py   # Custom exceptions
    ├── logger.py       # Structured logging
    ├── pagination.py   # Pagination utilities
    └── responses.py    # Standard response format

tests/
├── conftest.py       # Pytest fixtures
├── factories.py      # Test data factories
├── test_auth.py      # Auth tests
├── test_health.py    # Health check tests
├── test_users.py     # User tests
└── test_root.py      # Root endpoint tests
```

### Architectural Patterns

1. **Base Model**: All models inherit from `BaseModel`
   - Auto `id`, `created_at`, `updated_at`, `deleted_at`
   - `soft_delete()`, `restore()`, `is_deleted`, `touch()`

2. **Controller Pattern**: Business logic in controllers
   - CRUD operations with soft delete support
   - Pagination, filtering, sorting

3. **Service/Repository Pattern** (optional):
   - `BaseRepository` - Generic data access
   - `BaseService` - Business logic with hooks

4. **Middleware Stack**:
   - RequestID → Timing → RateLimit → CORS

## Authentication

### JWT with Refresh Tokens

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/register` | Register new user |
| `POST /api/auth/login` | Login (JSON body) |
| `POST /api/auth/login/form` | Login (form data, OAuth2 compatible) |
| `POST /api/auth/refresh` | Refresh access token |
| `GET /api/auth/me` | Get current user |
| `POST /api/auth/change-password` | Change password |
| `POST /api/auth/forgot-password` | Request password reset |
| `POST /api/auth/reset-password` | Reset with token |
| `POST /api/auth/verify-email` | Verify email |
| `POST /api/auth/logout` | Logout |

### Usage Examples

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com", "password": "securePass123"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "securePass123"}'
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": { "id": 1, "name": "John", "email": "john@example.com" }
}
```

**Protected Route:**
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Refresh Token:**
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

### Protect Routes

```python
from app.utils.auth import get_current_active_user

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"user": current_user}
```

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login_success

# Run with coverage
pytest --cov=app --cov-report=html
```

### Using Fixtures

```python
import pytest

@pytest.mark.asyncio
async def test_get_user(client, test_user, auth_headers):
    response = await client.get(f"/api/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email
```

### Available Fixtures

| Fixture | Description |
|---------|-------------|
| `db_session` | Fresh database session |
| `client` | AsyncClient with DB override |
| `test_user` | Verified test user |
| `test_user_unverified` | Unverified test user |
| `auth_headers` | Auth headers for test_user |
| `multiple_users` | 5 test users |

### Test Factories

```python
from tests.factories import UserFactory

user = UserFactory.build(name="Test User")
verified_user = UserFactory.build_verified()
users = UserFactory.build_batch(5)
admin = UserFactory.build_admin()
```

## Environment Variables

```env
# Application
APP_NAME=FastAPI App
APP_VERSION=1.0.0
ENVIRONMENT=development  # development, staging, production
DEBUG=true

# Database
DB_DRIVER=postgresql  # postgresql or mysql
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # json or text

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_ALLOW_CREDENTIALS=true
```

## Deployment

### Production Checklist

1. Set `DEBUG=false` and `ENVIRONMENT=production`
2. Generate secure `SECRET_KEY`: `openssl rand -hex 32`
3. Configure production `DATABASE_URL`
4. Set appropriate `CORS_ORIGINS`
5. Enable rate limiting
6. Use JSON logging format

### Running in Production

```bash
# Using Gunicorn with Uvicorn workers
pip install gunicorn
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/fastpy_db
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=fastpy_db
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Troubleshooting

### Common Issues

**`mysqlclient` fails on macOS:**
```bash
brew install mysql
export PATH="/usr/local/opt/mysql/bin:$PATH"
pip install mysqlclient
```

**`bcrypt` errors:**
```bash
pip install bcrypt==4.2.1 passlib==1.7.4
```

**`greenlet` missing:**
```bash
pip install greenlet==3.2.4
```

**Migration `sqlmodel` not defined:**
Add `import sqlmodel` to the migration file.

**401 on protected endpoints:**
- Check `Authorization: Bearer <token>` header
- Verify token hasn't expired (30 min default)

### Useful Commands

```bash
# View setup logs
cat setup.log

# Reset database
alembic downgrade base && alembic upgrade head

# Generate new secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Check database connection
python -c "from app.database.connection import check_db_connection; import asyncio; print(asyncio.run(check_db_connection()))"
```

## Updating an Existing Project

To get the latest Fastpy updates in an existing project:

### Update CLI Only (Recommended)

The CLI (`cli.py`) contains all code generators and commands. To update just the CLI:

```bash
# Download the latest cli.py
curl -o cli.py https://raw.githubusercontent.com/vutia-ent/fastpy/main/cli.py

# Or using wget
wget -O cli.py https://raw.githubusercontent.com/vutia-ent/fastpy/main/cli.py
```

### Update Core Utilities

To update the utility files (auth, exceptions, responses, pagination):

```bash
# Update utils
curl -o app/utils/auth.py https://raw.githubusercontent.com/vutia-ent/fastpy/main/app/utils/auth.py
curl -o app/utils/exceptions.py https://raw.githubusercontent.com/vutia-ent/fastpy/main/app/utils/exceptions.py
curl -o app/utils/responses.py https://raw.githubusercontent.com/vutia-ent/fastpy/main/app/utils/responses.py
curl -o app/utils/pagination.py https://raw.githubusercontent.com/vutia-ent/fastpy/main/app/utils/pagination.py
```

### Update Base Models

```bash
curl -o app/models/base.py https://raw.githubusercontent.com/vutia-ent/fastpy/main/app/models/base.py
```

### Update Middleware

```bash
curl -o app/middleware/rate_limit.py https://raw.githubusercontent.com/vutia-ent/fastpy/main/app/middleware/rate_limit.py
curl -o app/middleware/request_id.py https://raw.githubusercontent.com/vutia-ent/fastpy/main/app/middleware/request_id.py
curl -o app/middleware/timing.py https://raw.githubusercontent.com/vutia-ent/fastpy/main/app/middleware/timing.py
```

### Full Update (New Projects Only)

For a fresh start, clone the latest version:

```bash
git clone https://github.com/vutia-ent/fastpy.git my-new-api
cd my-new-api
./setup.sh
```

:warning: **Note**: Be careful when updating files you've customized. Always backup your changes first.

## Contributing

Contributions welcome:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## License

MIT
