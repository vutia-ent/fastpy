# Quick Start

Get up and running with FastCLI in under 5 minutes.

## Prerequisites

Make sure you have completed the [installation](installation.md) process.

## Your First Resource

Let's create a complete blog post resource with a single command:

```bash
python cli.py make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -f published:boolean:required \
  -m -p
```

This generates:

| File | Description |
|------|-------------|
| `app/models/post.py` | SQLModel with schemas |
| `app/controllers/post_controller.py` | CRUD operations |
| `app/routes/post_routes.py` | API endpoints |
| `alembic/versions/xxx_create_posts.py` | Migration file |

## Run Migrations

Apply the database migration:

```bash
# Using CLI
python cli.py db:migrate -m "Create posts table"

# Or using Alembic directly
alembic upgrade head
```

## Register Routes

Add the routes to `main.py`:

```python
from app.routes.post_routes import router as post_router

app.include_router(post_router, prefix="/api/posts", tags=["Posts"])
```

## Start the Server

```bash
python cli.py serve
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see your new endpoints.

## Test Your API

### Create a Post

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "My First Post",
    "body": "This is the content of my first post.",
    "published": true
  }'
```

### Get All Posts

```bash
curl http://localhost:8000/api/posts
```

### Get Paginated Posts

```bash
curl "http://localhost:8000/api/posts/paginated?page=1&per_page=10"
```

## Understanding the Generated Code

### Model (`app/models/post.py`)

```python
from typing import Optional
from datetime import datetime
from sqlmodel import Field
from app.models.base import BaseModel

class Post(BaseModel, table=True):
    __tablename__ = "posts"

    title: str = Field(nullable=False, max_length=200)
    body: str = Field(nullable=False)
    published: bool = Field(nullable=False)


class PostCreate(BaseModel):
    """Schema for creating a post"""
    title: str = Field(min_length=1, max_length=200)
    body: str
    published: bool


class PostUpdate(BaseModel):
    """Schema for updating a post"""
    title: Optional[str] = Field(default=None, max_length=200)
    body: Optional[str] = None
    published: Optional[bool] = None


class PostRead(BaseModel):
    """Schema for reading a post"""
    id: int
    title: str
    body: str
    published: bool
    created_at: datetime
    updated_at: datetime
```

### Controller (`app/controllers/post_controller.py`)

```python
class PostController:
    @staticmethod
    async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100):
        """Get all posts"""
        query = select(Post).where(Post.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create(session: AsyncSession, data: PostCreate):
        """Create a new post"""
        post = Post(**data.model_dump())
        session.add(post)
        await session.flush()
        await session.refresh(post)
        return post

    # ... more methods
```

### Routes (`app/routes/post_routes.py`)

```python
@router.get("/", response_model=List[PostRead])
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)  # Protected
):
    return await PostController.get_all(session, skip, limit)

@router.post("/", response_model=PostRead, status_code=201)
async def create_post(
    data: PostCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    return await PostController.create(session, data)
```

## Adding Relationships

Create a comment model with a foreign key:

```bash
python cli.py make:resource Comment \
  -f body:text:required \
  -f post_id:integer:required,foreign:posts.id \
  -f author_id:integer:required,foreign:users.id \
  -m -p
```

## Interactive Mode

Use interactive mode for guided field creation:

```bash
python cli.py make:resource Category -i -m

# Follow the prompts:
# Field definition: name:string:required,unique,max:100
# ✓ Added field: name (string)
# Field definition: description:text:nullable
# ✓ Added field: description (text)
# Field definition: [press Enter to finish]
```

## Next Steps

- [Field Types](../fields/overview.md) - Learn about all available field types
- [Validation Rules](../fields/validation.md) - Add validation to your fields
- [CLI Commands](../commands/overview.md) - Explore all available commands
- [Authentication](../api/authentication.md) - Understand JWT authentication
