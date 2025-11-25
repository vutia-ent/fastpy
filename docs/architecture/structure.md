# Project Structure

Understanding the FastCLI project architecture.

## Directory Layout

```
api/
├── app/
│   ├── config/           # Application configuration
│   │   └── settings.py   # Settings management
│   ├── controllers/      # Business logic
│   │   ├── auth_controller.py
│   │   └── user_controller.py
│   ├── database/         # Database connection
│   │   └── connection.py
│   ├── enums/            # Enum definitions
│   │   └── __init__.py
│   ├── middleware/       # Custom middleware
│   │   ├── request_id.py
│   │   ├── timing.py
│   │   └── rate_limit.py
│   ├── models/           # SQLModel definitions
│   │   ├── base.py       # Base model
│   │   └── user.py
│   ├── repositories/     # Data access layer
│   │   ├── base.py
│   │   └── user_repository.py
│   ├── routes/           # API endpoints
│   │   ├── auth_routes.py
│   │   ├── health_routes.py
│   │   └── user_routes.py
│   ├── seeders/          # Database seeders
│   │   └── user_seeder.py
│   ├── services/         # Business services
│   │   ├── base.py
│   │   └── user_service.py
│   └── utils/            # Utilities
│       ├── auth.py       # JWT & password
│       ├── exceptions.py # Custom exceptions
│       ├── logger.py     # Structured logging
│       ├── pagination.py # Pagination helpers
│       └── responses.py  # Response formats
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py
├── tests/                # Test files
│   ├── conftest.py       # Pytest fixtures
│   ├── factories.py      # Test factories
│   └── test_*.py
├── docs/                 # Documentation
├── cli.py                # FastCLI tool
├── main.py               # Application entry
├── requirements.txt      # Dependencies
├── .env                  # Environment config
└── alembic.ini           # Alembic config
```

## Core Components

### app/config/

Application configuration using Pydantic settings.

```python
# settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI App"
    debug: bool = True
    database_url: str
    secret_key: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

### app/models/

SQLModel definitions with Pydantic schemas.

```python
# base.py - All models inherit from this
class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    deleted_at: Optional[datetime] = None

    def soft_delete(self):
        self.deleted_at = utc_now()

    def restore(self):
        self.deleted_at = None

    def touch(self):
        self.updated_at = utc_now()
```

### app/controllers/

Business logic separated from routes.

```python
# user_controller.py
class UserController:
    @staticmethod
    async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100):
        query = select(User).where(User.deleted_at.is_(None))
        result = await session.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
```

### app/routes/

FastAPI route definitions.

```python
# user_routes.py
router = APIRouter()

@router.get("/", response_model=List[UserRead])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session)
):
    return await UserController.get_all(session, skip, limit)
```

### app/middleware/

Custom middleware components.

```python
# request_id.py
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request_id_var.set(request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

### app/utils/

Shared utilities and helpers.

| File | Purpose |
|------|---------|
| `auth.py` | JWT tokens, password hashing |
| `exceptions.py` | Custom exception classes |
| `logger.py` | Structured logging |
| `pagination.py` | Pagination utilities |
| `responses.py` | Standard response formats |

## Entry Points

### main.py

Application setup and configuration:

```python
from fastapi import FastAPI
from app.config.settings import settings
from app.routes.user_routes import router as user_router

app = FastAPI(title=settings.app_name)

# Middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Routes
app.include_router(user_router, prefix="/api/users")
```

### cli.py

FastCLI code generation tool:

```python
import typer

app = typer.Typer()

@app.command("make:model")
def make_model(name: str, fields: List[str]):
    # Generate model code
    pass

if __name__ == "__main__":
    app()
```

## Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables |
| `requirements.txt` | Python dependencies |
| `alembic.ini` | Migration configuration |
| `pytest.ini` | Test configuration |
| `pyproject.toml` | Project metadata |

## Next Steps

- [Patterns](patterns.md) - Architectural patterns
- [Middleware](middleware.md) - Middleware stack
- [Commands](../commands/overview.md) - CLI commands
