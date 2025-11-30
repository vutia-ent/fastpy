# Example: Blog System

Build a complete blog API with Fastpy.

## Overview

We'll create:
- Posts with categories and tags
- Comments with nested replies
- User authentication
- Full-text search

## Generate Resources

```bash
# Category
python cli.py make:resource Category \
  -f name:string:required,max:100 \
  -f slug:slug:required,unique,index \
  -f description:text:nullable \
  -m

# Post
python cli.py make:resource Post \
  -f title:string:required,max:200 \
  -f slug:slug:required,unique,index \
  -f body:text:required \
  -f excerpt:string:nullable,max:300 \
  -f featured_image:image:nullable \
  -f published:boolean:default:false \
  -f published_at:datetime:nullable \
  -f category_id:integer:foreign:categories.id \
  -f user_id:integer:foreign:users.id \
  -m -p

# Comment
python cli.py make:resource Comment \
  -f body:text:required \
  -f post_id:integer:required,foreign:posts.id \
  -f user_id:integer:required,foreign:users.id \
  -f parent_id:integer:foreign:comments.id,nullable \
  -m -p

# Tag
python cli.py make:model Tag \
  -f name:string:required,max:50,unique \
  -f slug:slug:required,unique,index \
  -m

# Post-Tag pivot
python cli.py make:model PostTag \
  -f post_id:integer:required,foreign:posts.id \
  -f tag_id:integer:required,foreign:tags.id \
  -m
```

## Run Migrations

```bash
python cli.py db:migrate -m "Create blog tables"
```

## Enhanced Models

### Post with Relationships

```python
# app/models/post.py
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, Relationship
from sqlalchemy import Column, Text
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.comment import Comment

class Post(BaseModel, table=True):
    __tablename__ = "posts"

    title: str = Field(max_length=200)
    slug: str = Field(unique=True, index=True)
    body: str = Field(sa_column=Column(Text))
    excerpt: Optional[str] = Field(max_length=300, default=None)
    featured_image: Optional[str] = None
    published: bool = Field(default=False)
    published_at: Optional[datetime] = None

    # Foreign keys
    category_id: Optional[int] = Field(foreign_key="categories.id")
    user_id: int = Field(foreign_key="users.id")

    # Relationships
    category: Optional["Category"] = Relationship(back_populates="posts")
    author: Optional["User"] = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")

    def publish(self):
        self.published = True
        self.published_at = datetime.utcnow()
```

## Enhanced Controller

```python
# app/controllers/post_controller.py
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from slugify import slugify
from app.models.post import Post
from app.utils.exceptions import NotFoundException

class PostController:
    @staticmethod
    async def get_published(session: AsyncSession):
        result = await session.execute(
            select(Post)
            .where(Post.published == True)
            .where(Post.deleted_at.is_(None))
            .order_by(Post.published_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_slug(session: AsyncSession, slug: str):
        result = await session.execute(
            select(Post)
            .where(Post.slug == slug)
            .where(Post.deleted_at.is_(None))
        )
        post = result.scalar_one_or_none()
        if not post:
            raise NotFoundException("Post not found")
        return post

    @staticmethod
    async def create(session: AsyncSession, data: dict, user_id: int):
        # Auto-generate slug
        if 'slug' not in data:
            data['slug'] = slugify(data['title'])

        post = Post(**data, user_id=user_id)
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    @staticmethod
    async def publish(session: AsyncSession, post: Post):
        post.publish()
        await session.commit()
        await session.refresh(post)
        return post
```

## API Routes

```python
# app/routes/post_routes.py
from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database.session import get_session
from app.utils.auth import get_current_active_user
from app.controllers.post_controller import PostController
from app.utils.responses import success_response, paginated_response
from app.utils.pagination import paginate, PaginationParams
from app.models.post import Post

router = APIRouter()

@router.get("/")
async def list_posts(
    page: int = 1,
    per_page: int = 20,
    session: AsyncSession = Depends(get_session)
):
    """List published posts (public)."""
    params = PaginationParams(page=page, per_page=per_page)
    query = select(Post).where(Post.published == True)
    result = await paginate(session, query, params)
    return paginated_response(**result.__dict__)

@router.get("/{slug}")
async def get_post(
    slug: str,
    session: AsyncSession = Depends(get_session)
):
    """Get post by slug (public)."""
    post = await PostController.get_by_slug(session, slug)
    return success_response(data=post)

@router.post("/")
async def create_post(
    data: PostCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    """Create new post (authenticated)."""
    post = await PostController.create(session, data.dict(), current_user.id)
    return success_response(data=post, message="Post created")

@router.post("/{id}/publish")
async def publish_post(
    id: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    """Publish a post (author only)."""
    post = await PostController.get_by_id(session, id)
    if post.user_id != current_user.id:
        raise ForbiddenException("Not authorized")
    post = await PostController.publish(session, post)
    return success_response(data=post, message="Post published")
```

## Request/Response Schemas

```python
# app/schemas/post.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    title: str
    body: str
    excerpt: Optional[str] = None
    category_id: Optional[int] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    excerpt: Optional[str] = None
    category_id: Optional[int] = None

class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    body: str
    excerpt: Optional[str]
    published: bool
    published_at: Optional[datetime]
    created_at: datetime
    author_name: str

    class Config:
        from_attributes = True
```

## Seeder

```python
# app/seeders/post_seeder.py
from faker import Faker
from app.models.post import Post
from app.models.category import Category

fake = Faker()

class PostSeeder:
    @staticmethod
    async def run(session, count: int = 20):
        # Get categories
        categories = await session.execute(select(Category))
        category_ids = [c.id for c in categories.scalars().all()]

        for _ in range(count):
            post = Post(
                title=fake.sentence(nb_words=6),
                slug=fake.slug(),
                body=fake.text(max_nb_chars=2000),
                excerpt=fake.text(max_nb_chars=200),
                published=fake.boolean(chance_of_getting_true=70),
                published_at=fake.date_time_this_year() if fake.boolean() else None,
                category_id=fake.random_element(category_ids) if category_ids else None,
                user_id=1
            )
            session.add(post)

        await session.commit()
```

## API Usage

```bash
# List published posts
curl http://localhost:8000/api/posts

# Get single post
curl http://localhost:8000/api/posts/my-first-post

# Create post
curl -X POST http://localhost:8000/api/posts \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Post",
    "body": "This is the content...",
    "category_id": 1
  }'

# Publish post
curl -X POST http://localhost:8000/api/posts/1/publish \
  -H "Authorization: Bearer TOKEN"
```
