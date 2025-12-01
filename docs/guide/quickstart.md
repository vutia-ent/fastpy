# Quick Start

Build your first API resource in under 5 minutes.

## Start the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start development server
fastpy serve
```

Your API is now running at [http://localhost:8000](http://localhost:8000).

## Explore the API

Visit the interactive documentation:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Create Your First Resource

Let's create a complete blog post resource:

```bash
fastpy make:resource Post \
  -f title:string:required,max:200 \
  -f slug:slug:unique \
  -f body:text:required \
  -f published:boolean:default:false \
  -f published_at:datetime:nullable \
  -m -p
```

This generates:

| File | Description |
|------|-------------|
| `app/models/post.py` | SQLModel model with fields |
| `app/controllers/post_controller.py` | CRUD business logic |
| `app/routes/post_routes.py` | Protected API endpoints |
| `alembic/versions/xxx_create_posts.py` | Database migration |

## Apply the Migration

```bash
fastpy db:migrate -m "Create posts table"
```

## Register the Routes

Add your new routes to `app/routes/__init__.py`:

```python
from app.routes.post_routes import router as post_router

# In the register_routes function
app.include_router(post_router, prefix="/api/posts", tags=["Posts"])
```

## Test Your Endpoints

### Create a Post

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "My First Post",
    "body": "Hello, world!",
    "published": true
  }'
```

### List All Posts

```bash
curl http://localhost:8000/api/posts \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get a Single Post

```bash
curl http://localhost:8000/api/posts/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Understanding the Generated Code

### Model

```python
# app/models/post.py
class Post(BaseModel, table=True):
    __tablename__ = "posts"

    title: str = Field(max_length=200)
    slug: str = Field(unique=True, index=True)
    body: str = Field(sa_column=Column(Text))
    published: bool = Field(default=False)
    published_at: Optional[datetime] = None
```

### Controller

```python
# app/controllers/post_controller.py
class PostController:
    @staticmethod
    async def get_all(session: AsyncSession):
        result = await session.execute(
            select(Post).where(Post.deleted_at.is_(None))
        )
        return result.scalars().all()
```

### Routes

```python
# app/routes/post_routes.py
@router.get("/")
async def list_posts(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    posts = await PostController.get_all(session)
    return success_response(data=posts)
```

## What's Next?

- [CLI Commands](/commands/overview) - Explore all code generators
- [Field Types](/fields/overview) - Available field types and validation
- [Authentication](/api/authentication) - Auth system documentation
