# Blog System Example

Build a complete blog system with posts, categories, tags, and comments.

## Overview

This example demonstrates:

- Multiple related models
- Many-to-many relationships
- Nested resources
- Search and filtering
- Full CRUD operations

---

## Models

### Category

```bash
python cli.py make:model Category \
  -f name:string:required,unique,max:100 \
  -f slug:slug:required,unique \
  -f description:text:nullable \
  -m
```

### Tag

```bash
python cli.py make:model Tag \
  -f name:string:required,unique,max:50 \
  -f slug:slug:required,unique \
  -f color:color:nullable \
  -m
```

### Post

```bash
python cli.py make:resource Post \
  -f title:string:required,max:200,min:5 \
  -f slug:slug:required,unique \
  -f excerpt:text:nullable,max:500 \
  -f body:text:required,min:50 \
  -f featured_image:image:nullable \
  -f published:boolean:required \
  -f published_at:datetime:nullable \
  -f views:integer:required,ge:0 \
  -f author_id:integer:required,foreign:users.id \
  -f category_id:integer:nullable,foreign:categories.id \
  -m -p
```

### Comment

```bash
python cli.py make:resource Comment \
  -f body:text:required,min:10,max:1000 \
  -f approved:boolean:required \
  -f post_id:integer:required,foreign:posts.id \
  -f author_id:integer:required,foreign:users.id \
  -f parent_id:integer:nullable,foreign:comments.id \
  -m -p
```

---

## Enhanced Post Model

Add relationships manually:

```python
# app/models/post.py

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, Relationship
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.comment import Comment


class Post(BaseModel, table=True):
    __tablename__ = "posts"

    title: str = Field(nullable=False, max_length=200)
    slug: str = Field(nullable=False, unique=True, max_length=255)
    excerpt: Optional[str] = Field(default=None, nullable=True)
    body: str = Field(nullable=False)
    featured_image: Optional[str] = Field(default=None, nullable=True)
    published: bool = Field(default=False, nullable=False)
    published_at: Optional[datetime] = Field(default=None, nullable=True)
    views: int = Field(default=0, nullable=False)

    author_id: int = Field(foreign_key="users.id", nullable=False)
    category_id: Optional[int] = Field(foreign_key="categories.id", nullable=True)

    # Relationships
    author: Optional["User"] = Relationship(back_populates="posts")
    category: Optional["Category"] = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")


class PostCreate(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    slug: Optional[str] = None
    excerpt: Optional[str] = Field(default=None, max_length=500)
    body: str = Field(min_length=50)
    featured_image: Optional[str] = None
    published: bool = False
    category_id: Optional[int] = None


class PostRead(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    body: str
    featured_image: Optional[str]
    published: bool
    published_at: Optional[datetime]
    views: int
    author_id: int
    category_id: Optional[int]
    created_at: datetime
    updated_at: datetime
```

---

## Controller with Advanced Features

```python
# app/controllers/post_controller.py

from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from slugify import slugify

from app.models.post import Post, PostCreate, PostUpdate
from app.utils.pagination import paginate, PaginationParams, PaginatedResult
from app.utils.exceptions import NotFoundException, ConflictException


class PostController:

    @staticmethod
    async def get_all(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        published_only: bool = True
    ) -> List[Post]:
        query = select(Post).where(Post.deleted_at.is_(None))
        if published_only:
            query = query.where(Post.published == True)
        query = query.order_by(Post.created_at.desc()).offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_paginated(
        session: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        category_id: Optional[int] = None,
        author_id: Optional[int] = None,
        search: Optional[str] = None,
        published_only: bool = True
    ) -> PaginatedResult[Post]:
        query = select(Post).where(Post.deleted_at.is_(None))

        if published_only:
            query = query.where(Post.published == True)
        if category_id:
            query = query.where(Post.category_id == category_id)
        if author_id:
            query = query.where(Post.author_id == author_id)
        if search:
            query = query.where(
                or_(
                    Post.title.ilike(f"%{search}%"),
                    Post.body.ilike(f"%{search}%")
                )
            )

        params = PaginationParams(page=page, per_page=per_page)
        return await paginate(session, query, params)

    @staticmethod
    async def get_by_slug(session: AsyncSession, slug: str) -> Optional[Post]:
        query = select(Post).where(
            Post.slug == slug,
            Post.deleted_at.is_(None)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        session: AsyncSession,
        data: PostCreate,
        author_id: int
    ) -> Post:
        # Generate slug if not provided
        slug = data.slug or slugify(data.title)

        # Check slug uniqueness
        existing = await PostController.get_by_slug(session, slug)
        if existing:
            raise ConflictException("A post with this slug already exists")

        post = Post(
            **data.model_dump(exclude={"slug"}),
            slug=slug,
            author_id=author_id
        )
        session.add(post)
        await session.flush()
        await session.refresh(post)
        return post

    @staticmethod
    async def publish(session: AsyncSession, id: int) -> Post:
        post = await PostController.get_by_id(session, id)
        if not post:
            raise NotFoundException("Post not found")

        post.published = True
        post.published_at = datetime.now(timezone.utc)
        post.touch()
        await session.flush()
        await session.refresh(post)
        return post

    @staticmethod
    async def increment_views(session: AsyncSession, id: int) -> Post:
        post = await PostController.get_by_id(session, id)
        if not post:
            raise NotFoundException("Post not found")

        post.views += 1
        await session.flush()
        return post
```

---

## Routes with Filtering

```python
# app/routes/post_routes.py

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.controllers.post_controller import PostController
from app.models.post import PostCreate, PostRead
from app.utils.auth import get_current_active_user

router = APIRouter()


@router.get("/")
async def get_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    author_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None, min_length=2),
    session: AsyncSession = Depends(get_session)
):
    """Get paginated posts with optional filters"""
    result = await PostController.get_paginated(
        session,
        page=page,
        per_page=per_page,
        category_id=category_id,
        author_id=author_id,
        search=search
    )
    return {
        "data": result.items,
        "pagination": {
            "page": result.page,
            "per_page": result.per_page,
            "total": result.total,
            "pages": result.pages
        }
    }


@router.get("/slug/{slug}", response_model=PostRead)
async def get_post_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_session)
):
    """Get post by slug"""
    post = await PostController.get_by_slug(session, slug)
    if not post:
        raise NotFoundException("Post not found")

    # Increment views
    await PostController.increment_views(session, post.id)

    return post


@router.post("/{post_id}/publish", response_model=PostRead)
async def publish_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    """Publish a draft post"""
    return await PostController.publish(session, post_id)
```

---

## Seeder

```python
# app/seeders/post_seeder.py

from typing import List
from faker import Faker
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post

fake = Faker()


class PostSeeder:
    @staticmethod
    async def run(
        session: AsyncSession,
        count: int = 20,
        author_id: int = 1
    ) -> List[Post]:
        posts = []

        for _ in range(count):
            title = fake.sentence()
            post = Post(
                title=title,
                slug=slugify(title) + f"-{fake.unique.random_int()}",
                excerpt=fake.paragraph(nb_sentences=2),
                body=fake.paragraph(nb_sentences=10),
                published=fake.boolean(chance_of_getting_true=70),
                views=fake.random_int(min=0, max=1000),
                author_id=author_id
            )
            session.add(post)
            posts.append(post)

        await session.flush()
        for post in posts:
            await session.refresh(post)

        return posts
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts/` | List posts with filters |
| GET | `/api/posts/{id}` | Get post by ID |
| GET | `/api/posts/slug/{slug}` | Get post by slug |
| POST | `/api/posts/` | Create post |
| PUT | `/api/posts/{id}` | Update post |
| DELETE | `/api/posts/{id}` | Delete post |
| POST | `/api/posts/{id}/publish` | Publish post |

---

## Usage Examples

### Create Post

```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Getting Started with FastAPI",
    "body": "FastAPI is a modern web framework...",
    "category_id": 1
  }'
```

### Search Posts

```bash
curl "http://localhost:8000/api/posts/?search=fastapi&category_id=1&page=1"
```

### Get by Slug

```bash
curl http://localhost:8000/api/posts/slug/getting-started-with-fastapi
```

## Next Steps

- [E-commerce Example](ecommerce.md) - Product catalog
- [API Service Example](api-service.md) - Microservice
- [Make Commands](../commands/make.md) - Generate more resources
