# Make Commands

Code generators for creating models, controllers, routes, and more.

## make:resource

Generate a complete resource (model + controller + routes).

```bash
fastpy make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -m -p
```

### Options

| Option | Description |
|--------|-------------|
| `-f, --field` | Field definition (repeatable) |
| `-m, --migration` | Generate migration |
| `-p, --protected` | Require authentication |
| `-i, --interactive` | Interactive mode |

### Generated Files

- `app/models/post.py`
- `app/controllers/post_controller.py`
- `app/routes/post_routes.py`
- `alembic/versions/xxx_create_posts.py` (with `-m`)

## make:model

Generate just a model.

```bash
fastpy make:model Post -f title:string:required -f body:text
```

### Options

| Option | Description |
|--------|-------------|
| `-f, --field` | Field definition |
| `-m, --migration` | Generate migration |

### Generated Code

```python
from typing import Optional
from datetime import datetime
from sqlmodel import Field
from app.models.base import BaseModel

class Post(BaseModel, table=True):
    __tablename__ = "posts"

    title: str = Field(max_length=200)
    body: str = Field(sa_column=Column(Text))
```

## make:controller

Generate a controller.

```bash
fastpy make:controller Post
```

### Generated Code

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.post import Post

class PostController:
    @staticmethod
    async def get_all(session: AsyncSession):
        result = await session.execute(
            select(Post).where(Post.deleted_at.is_(None))
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int):
        result = await session.execute(
            select(Post).where(Post.id == id, Post.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data: dict):
        post = Post(**data)
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    @staticmethod
    async def update(session: AsyncSession, post: Post, data: dict):
        for key, value in data.items():
            setattr(post, key, value)
        post.touch()
        await session.commit()
        await session.refresh(post)
        return post

    @staticmethod
    async def delete(session: AsyncSession, post: Post):
        post.soft_delete()
        await session.commit()
```

## make:route

Generate route definitions.

```bash
fastpy make:route Post --protected
```

### Options

| Option | Description |
|--------|-------------|
| `--protected` | Require authentication |

### Generated Code

```python
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database.session import get_session
from app.utils.auth import get_current_active_user
from app.controllers.post_controller import PostController
from app.utils.responses import success_response

router = APIRouter()

@router.get("/")
async def list_posts(
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    posts = await PostController.get_all(session)
    return success_response(data=posts)
```

## make:service

Generate a service class with business logic hooks.

```bash
fastpy make:service Post
```

### Generated Code

```python
from app.services.base import BaseService
from app.models.post import Post

class PostService(BaseService[Post]):
    model = Post

    async def before_create(self, data: dict) -> dict:
        # Add custom logic before creation
        return data

    async def after_create(self, instance: Post) -> Post:
        # Add custom logic after creation
        return instance
```

## make:repository

Generate a repository class for data access.

```bash
fastpy make:repository Post
```

## make:middleware

Generate custom middleware.

```bash
fastpy make:middleware RateLimit
```

### Generated Code

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Add middleware logic here
        response = await call_next(request)
        return response
```

## make:seeder

Generate a database seeder.

```bash
fastpy make:seeder Post
```

## make:factory

Generate a test factory.

```bash
fastpy make:factory Post
```

### Generated Code

```python
import factory
from app.models.post import Post

class PostFactory(factory.Factory):
    class Meta:
        model = Post

    title = factory.Faker('sentence')
    body = factory.Faker('text')
```

## make:test

Generate a test file.

```bash
fastpy make:test Post
```

## make:enum

Generate an enum.

```bash
fastpy make:enum PostStatus
```

### Generated Code

```python
from enum import Enum

class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
```

## make:exception

Generate a custom exception.

```bash
fastpy make:exception PostNotFound
```

### Generated Code

```python
from app.utils.exceptions import BaseAPIException

class PostNotFoundException(BaseAPIException):
    def __init__(self, message: str = "Post not found"):
        super().__init__(
            message=message,
            code="POST_NOT_FOUND",
            status_code=404
        )
```
