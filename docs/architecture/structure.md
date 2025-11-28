# Project Structure

Fastpy follows a clean MVC architecture with optional service/repository layers.

## Directory Overview

```
├── app/
│   ├── config/           # Application settings
│   ├── controllers/      # Business logic
│   ├── database/         # DB connection and session
│   ├── enums/            # Enum definitions
│   ├── middleware/       # Custom middleware
│   ├── models/           # SQLModel models
│   ├── repositories/     # Data access layer
│   ├── routes/           # API route definitions
│   ├── seeders/          # Database seeders
│   ├── services/         # Business logic services
│   └── utils/            # Utilities (auth, logger, etc.)
├── alembic/              # Database migrations
├── tests/                # Test files
├── cli.py                # FastCLI entry point
├── main.py               # Application entry point
└── requirements.txt      # Python dependencies
```

## Core Directories

### app/config/

Application configuration using Pydantic Settings.

```python
# app/config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Fastpy"
    debug: bool = False
    database_url: str
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
```

### app/controllers/

Business logic controllers handling CRUD operations.

```python
# app/controllers/user_controller.py
class UserController:
    @staticmethod
    async def get_all(session: AsyncSession):
        result = await session.execute(
            select(User).where(User.deleted_at.is_(None))
        )
        return result.scalars().all()
```

### app/models/

SQLModel models with automatic timestamps and soft deletes.

```python
# app/models/base.py
class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()

    def restore(self):
        self.deleted_at = None

    def touch(self):
        self.updated_at = datetime.utcnow()
```

### app/routes/

FastAPI route definitions.

```python
# app/routes/user_routes.py
router = APIRouter()

@router.get("/")
async def list_users(session: AsyncSession = Depends(get_session)):
    users = await UserController.get_all(session)
    return success_response(data=users)
```

### app/database/

Database connection and session management.

```python
# app/database/session.py
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### app/utils/

Utility modules for common functionality.

| File | Purpose |
|------|---------|
| `auth.py` | JWT authentication |
| `logger.py` | Structured logging |
| `pagination.py` | Query pagination |
| `responses.py` | Response formatting |
| `exceptions.py` | Custom exceptions |

## Optional Layers

### app/services/

Business logic with lifecycle hooks.

```python
# app/services/base.py
class BaseService(Generic[T]):
    model: Type[T]

    async def before_create(self, data: dict) -> dict:
        return data

    async def after_create(self, instance: T) -> T:
        return instance

    async def create(self, session: AsyncSession, data: dict) -> T:
        data = await self.before_create(data)
        instance = self.model(**data)
        session.add(instance)
        await session.commit()
        return await self.after_create(instance)
```

### app/repositories/

Data access abstraction.

```python
# app/repositories/base.py
class BaseRepository(Generic[T]):
    model: Type[T]

    async def find_all(self, session: AsyncSession):
        result = await session.execute(
            select(self.model).where(self.model.deleted_at.is_(None))
        )
        return result.scalars().all()
```

## Entry Points

### main.py

FastAPI application setup.

```python
from fastapi import FastAPI
from app.routes import register_routes
from app.middleware import register_middleware

app = FastAPI(title="Fastpy")
register_middleware(app)
register_routes(app)
```

### cli.py

FastCLI command entry point.

```python
import typer
from commands import make, db, serve

app = typer.Typer()
app.add_typer(make.app, name="make")
app.add_typer(db.app, name="db")

if __name__ == "__main__":
    app()
```

## Naming Conventions

| Entity | Convention | Example |
|--------|------------|---------|
| Tables | plural, snake_case | `users`, `blog_posts` |
| Models | singular, PascalCase | `User`, `BlogPost` |
| Controllers | PascalCase + Controller | `UserController` |
| Routes | snake_case | `user_routes.py` |
| Services | PascalCase + Service | `UserService` |
