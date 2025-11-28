---
title: Architectural Patterns
description: Design patterns used in Fastpy
---

## Base Model Pattern

All models inherit from `BaseModel`, which provides common functionality.

### Features

- Auto-incrementing `id`
- Timestamps: `created_at`, `updated_at`
- Soft delete: `deleted_at`
- Helper methods

### Usage

```python
from app.models.base import BaseModel
from sqlmodel import Field

class Post(BaseModel, table=True):
    __tablename__ = "posts"

    title: str = Field(max_length=200)
    body: str
```

### Helper Methods

```python
# Soft delete
post.soft_delete()

# Restore soft-deleted record
post.restore()

# Check if deleted
if post.is_deleted:
    ...

# Update timestamp
post.touch()
```

---

## Controller Pattern

Controllers handle business logic and database operations.

### Structure

```python
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

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
            select(Post).where(
                Post.id == id,
                Post.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data: PostCreate):
        post = Post(**data.model_dump())
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post
```

### Usage in Routes

```python
@router.get("/")
async def list_posts(session: AsyncSession = Depends(get_session)):
    return await PostController.get_all(session)
```

---

## Service/Repository Pattern

For complex domains, use the layered architecture.

### Repository (Data Access)

```python
from app.repositories.base_repository import BaseRepository

class PostRepository(BaseRepository[Post]):
    pass

# Usage
repo = PostRepository(Post, session)
posts = await repo.get_all()
post = await repo.get_by_id(1)
```

### Service (Business Logic)

```python
from app.services.base_service import BaseService

class PostService(BaseService[Post]):
    async def before_create(self, data: dict):
        # Generate slug from title
        data['slug'] = slugify(data['title'])
        return data

    async def after_create(self, instance: Post):
        # Send notification
        await notify_subscribers(instance)
```

### When to Use

| Pattern | Use When |
|---------|----------|
| Controller only | Simple CRUD, straightforward logic |
| Service/Repository | Complex business rules, multiple data sources |

---

## Dependency Injection

FastAPI's dependency injection for database sessions.

```python
from fastapi import Depends
from app.database.connection import get_session

@router.get("/posts")
async def list_posts(session: AsyncSession = Depends(get_session)):
    # session is automatically managed
    return await PostController.get_all(session)
```

### Benefits

- Automatic session lifecycle management
- Easy testing with mock sessions
- Transaction handling

---

## Soft Deletes

Records are never permanently deleted by default.

### Implementation

```python
# In controller
async def delete(session: AsyncSession, id: int):
    post = await cls.get_by_id(session, id)
    if post:
        post.soft_delete()
        await session.commit()
    return post
```

### Querying

Always filter out deleted records:

```python
select(Post).where(Post.deleted_at.is_(None))
```

### Permanent Delete

When you actually need to delete:

```python
await session.delete(post)
await session.commit()
```
