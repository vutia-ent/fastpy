# Make Commands

Commands for generating code files including models, controllers, routes, services, and more.

## make:resource

Generate a complete resource with model, controller, and routes in one command.

### Usage

```bash
python cli.py make:resource NAME [OPTIONS]
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `-f, --field` | string | Field definition (repeatable) |
| `-m, --migration` | flag | Generate migration |
| `-p, --protected` | flag | Add authentication |
| `-i, --interactive` | flag | Interactive mode |

### Examples

```bash
# Basic resource
python cli.py make:resource Post -f title:string:required -m

# Complete blog post
python cli.py make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -f published:boolean:required \
  -f author_id:integer:foreign:users.id \
  -m -p

# Interactive mode
python cli.py make:resource Comment -i -m -p
```

### Generated Files

| File | Description |
|------|-------------|
| `app/models/post.py` | Model + Create/Update/Read schemas |
| `app/controllers/post_controller.py` | CRUD operations |
| `app/routes/post_routes.py` | API endpoints |
| `alembic/versions/xxx.py` | Migration (if `-m`) |

---

## make:model

Generate a SQLModel with Pydantic schemas.

### Usage

```bash
python cli.py make:model NAME [OPTIONS]
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `-f, --field` | string | Field definition (repeatable) |
| `-m, --migration` | flag | Generate migration |
| `-i, --interactive` | flag | Interactive mode |

### Examples

```bash
# Basic model
python cli.py make:model Category -f name:string:required,unique

# Model with multiple fields
python cli.py make:model Product \
  -f name:string:required,max:255 \
  -f price:money:required,ge:0 \
  -f stock:integer:required,ge:0 \
  -f sku:string:required,unique \
  -m

# Interactive mode
python cli.py make:model Tag -i -m
```

### Generated Code

```python
# app/models/product.py

from typing import Optional
from datetime import datetime
from decimal import Decimal
from sqlmodel import Field
from app.models.base import BaseModel


class Product(BaseModel, table=True):
    __tablename__ = "products"

    name: str = Field(nullable=False, max_length=255)
    price: Decimal = Field(nullable=False, decimal_places=2)
    stock: int = Field(nullable=False)
    sku: str = Field(nullable=False, unique=True)


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    price: Decimal = Field(ge=0)
    stock: int = Field(ge=0)
    sku: str


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    price: Optional[Decimal] = Field(default=None, ge=0)
    stock: Optional[int] = Field(default=None, ge=0)
    sku: Optional[str] = None


class ProductRead(BaseModel):
    id: int
    name: str
    price: Decimal
    stock: int
    sku: str
    created_at: datetime
    updated_at: datetime
```

---

## make:controller

Generate a controller with CRUD operations.

### Usage

```bash
python cli.py make:controller NAME
```

### Examples

```bash
python cli.py make:controller Post
python cli.py make:controller Product
```

### Generated Code

```python
# app/controllers/post_controller.py

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.post import Post, PostCreate, PostUpdate
from app.utils.pagination import PaginatedResult, paginate


class PostController:

    @staticmethod
    async def get_all(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Post]:
        query = (
            select(Post)
            .where(Post.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> Optional[Post]:
        query = select(Post).where(
            Post.id == id,
            Post.deleted_at.is_(None)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data: PostCreate) -> Post:
        post = Post(**data.model_dump())
        session.add(post)
        await session.flush()
        await session.refresh(post)
        return post

    @staticmethod
    async def update(
        session: AsyncSession,
        id: int,
        data: PostUpdate
    ) -> Optional[Post]:
        post = await PostController.get_by_id(session, id)
        if not post:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(post, key, value)
        post.touch()
        await session.flush()
        await session.refresh(post)
        return post

    @staticmethod
    async def delete(session: AsyncSession, id: int) -> bool:
        post = await PostController.get_by_id(session, id)
        if not post:
            return False
        post.soft_delete()
        await session.flush()
        return True
```

---

## make:route

Generate API routes for a model.

### Usage

```bash
python cli.py make:route NAME [OPTIONS]
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `-p, --protected` | flag | Add authentication |

### Examples

```bash
# Public routes
python cli.py make:route Post

# Protected routes
python cli.py make:route Post -p
```

### Generated Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List all |
| GET | `/paginated` | Paginated list |
| GET | `/count` | Total count |
| GET | `/{id}` | Get by ID |
| HEAD | `/{id}` | Check exists |
| POST | `/` | Create |
| PUT | `/{id}` | Full update |
| PATCH | `/{id}` | Partial update |
| DELETE | `/{id}` | Soft delete |
| POST | `/{id}/restore` | Restore |

---

## make:service

Generate a service class for business logic.

### Usage

```bash
python cli.py make:service NAME
```

### Examples

```bash
python cli.py make:service Post
python cli.py make:service Order
```

### Generated Code

```python
# app/services/post_service.py

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post, PostCreate, PostUpdate
from app.repositories.post_repository import PostRepository
from app.services.base import BaseService


class PostService(BaseService[Post, PostRepository]):
    """Service for Post business logic"""

    def __init__(self, session: AsyncSession):
        super().__init__(PostRepository(session))
        self.session = session

    async def before_create(self, data: PostCreate) -> PostCreate:
        """Hook called before creating a post"""
        # Add custom logic here
        return data

    async def after_create(self, post: Post) -> Post:
        """Hook called after creating a post"""
        # Add custom logic (notifications, events, etc.)
        return post
```

---

## make:repository

Generate a repository class for data access.

### Usage

```bash
python cli.py make:repository NAME
```

### Examples

```bash
python cli.py make:repository Post
python cli.py make:repository User
```

---

## make:middleware

Generate custom middleware.

### Usage

```bash
python cli.py make:middleware NAME
```

### Examples

```bash
python cli.py make:middleware RateLimit
python cli.py make:middleware Logging
python cli.py make:middleware Auth
```

### Generated Code

```python
# app/middleware/rate_limit_middleware.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Custom RateLimit middleware"""

    def __init__(self, app, **kwargs):
        super().__init__(app)
        # Initialize middleware options

    async def dispatch(self, request: Request, call_next) -> Response:
        # Before request
        # Add your logic here

        response = await call_next(request)

        # After request
        # Add your logic here

        return response
```

---

## make:seeder

Generate a database seeder.

### Usage

```bash
python cli.py make:seeder NAME
```

### Examples

```bash
python cli.py make:seeder User
python cli.py make:seeder Post
python cli.py make:seeder Category
```

---

## make:test

Generate a test file with fixtures.

### Usage

```bash
python cli.py make:test NAME
```

### Examples

```bash
python cli.py make:test Post
python cli.py make:test Auth
```

### Generated Code

```python
# tests/test_post.py

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_posts(client: AsyncClient):
    """Test getting all posts"""
    response = await client.get("/api/posts/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_post(client: AsyncClient, auth_headers: dict):
    """Test creating a post"""
    response = await client.post(
        "/api/posts/",
        headers=auth_headers,
        json={
            "title": "Test Post",
            "body": "Test content"
        }
    )
    assert response.status_code == 201
```

---

## make:factory

Generate a test factory.

### Usage

```bash
python cli.py make:factory NAME
```

### Examples

```bash
python cli.py make:factory Post
python cli.py make:factory User
```

---

## make:enum

Generate an enum class.

### Usage

```bash
python cli.py make:enum NAME
```

### Examples

```bash
python cli.py make:enum PostStatus
python cli.py make:enum OrderStatus
python cli.py make:enum UserRole
```

### Generated Code

```python
# app/enums/post_status.py

from enum import Enum


class PostStatus(str, Enum):
    """PostStatus enumeration"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

    @classmethod
    def values(cls) -> list:
        return [e.value for e in cls]
```

---

## make:exception

Generate a custom exception.

### Usage

```bash
python cli.py make:exception NAME
```

### Examples

```bash
python cli.py make:exception PostNotFound
python cli.py make:exception InvalidToken
python cli.py make:exception PaymentFailed
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

---

## Field Definition Reference

See [Field Types](../fields/overview.md) for complete field documentation.

### Quick Reference

```bash
# String fields
-f title:string:required,max:200
-f slug:slug:required,unique

# Numeric fields
-f price:money:required,ge:0
-f quantity:integer:required,ge:0

# Boolean
-f published:boolean:required

# Date/Time
-f published_at:datetime:nullable
-f birth_date:date:nullable

# Relationships
-f user_id:integer:required,foreign:users.id
-f category_id:integer:nullable,foreign:categories.id
```
