# Quick Start

Build your first API resource in under 5 minutes.

::: tip Prerequisites
Make sure you've completed the [Installation](/guide/installation) steps before continuing.
:::

## Step 1: Start the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start development server
fastpy serve
```

::: info Server Running
Your API is now running at [http://localhost:8000](http://localhost:8000)
:::

## Step 2: Explore the API

Visit the interactive documentation:

<div class="api-docs-grid">
  <a href="http://localhost:8000/docs" target="_blank" class="api-doc-card">
    <div class="api-doc-icon">📚</div>
    <div class="api-doc-content">
      <h4>Swagger UI</h4>
      <p>Interactive API explorer</p>
    </div>
  </a>
  <a href="http://localhost:8000/redoc" target="_blank" class="api-doc-card">
    <div class="api-doc-icon">📖</div>
    <div class="api-doc-content">
      <h4>ReDoc</h4>
      <p>Clean API reference</p>
    </div>
  </a>
</div>

## Step 3: Create Your First Resource

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
| `app/models/post.py` | SQLModel model with Model Concerns |
| `app/controllers/post_controller.py` | Active Record-based CRUD logic |
| `app/routes/post_routes.py` | Routes with Route Model Binding |
| `alembic/versions/xxx_create_posts.py` | Database migration |

::: info Included by Default
- **Active Record** - `Post.create()`, `post.update()`, `post.delete()`
- **Route Model Binding** - Auto-resolve `{id}` params to model instances
- **Model Concerns** - `HasScopes`, `GuardsAttributes` for clean queries
:::

## Step 4: Apply the Migration

```bash
fastpy db:migrate -m "Create posts table"
```

## Step 5: Register the Routes

Add your new routes to `app/routes/__init__.py`:

```python
from app.routes.post_routes import router as post_router

# In the register_routes function
app.include_router(post_router, prefix="/api/posts", tags=["Posts"])
```

## Step 6: Test Your Endpoints

::: code-group

```bash [Create Post]
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "My First Post",
    "body": "Hello, world!",
    "published": true
  }'
```

```bash [List Posts]
curl http://localhost:8000/api/posts \
  -H "Authorization: Bearer YOUR_TOKEN"
```

```bash [Get Single Post]
curl http://localhost:8000/api/posts/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

:::

## Understanding the Generated Code

::: details Model (`app/models/post.py`)
```python
from app.models.base import BaseModel
from app.models.concerns import HasScopes, GuardsAttributes

class Post(BaseModel, HasScopes, GuardsAttributes, table=True):
    __tablename__ = "posts"

    title: str = Field(max_length=200)
    slug: str = Field(unique=True, index=True)
    body: str = Field(sa_column=Column(Text))
    published: bool = Field(default=False)
    published_at: Optional[datetime] = None

    # Mass assignment protection
    _fillable = ['title', 'slug', 'body', 'published', 'published_at']
    _guarded = ['id', 'created_at', 'updated_at', 'deleted_at']
```
:::

::: details Controller (`app/controllers/post_controller.py`) - Active Record
```python
from app.models.post import Post

class PostController:
    @staticmethod
    async def get_all(skip: int = 0, limit: int = 100):
        """Uses Active Record pattern - no session needed"""
        return await Post.query().limit(limit).offset(skip).get()

    @staticmethod
    async def create(data: PostCreate):
        return await Post.create(**data.model_dump())

    @staticmethod
    async def update(id: int, data: PostUpdate):
        post = await Post.find_or_fail(id)
        await post.update(**data.model_dump(exclude_unset=True))
        return post

    @staticmethod
    async def delete(id: int):
        post = await Post.find_or_fail(id)
        await post.delete()  # Soft delete
```
:::

::: details Routes (`app/routes/post_routes.py`) - Route Model Binding
```python
from app.utils.binding import bind_or_fail

@router.get("/")
async def list_posts(current_user: User = Depends(get_current_active_user)):
    """No session needed - Active Record handles it"""
    return await PostController.get_all()

@router.get("/{id}")
async def get_one(post: Post = bind_or_fail(Post)):
    """Route model binding - auto-resolved from {id}"""
    return post

@router.put("/{id}")
async def update(data: PostUpdate, post: Post = bind_or_fail(Post)):
    await post.update(**data.model_dump(exclude_unset=True))
    return post
```
:::

## What's Next?

<div class="next-steps">
  <a href="/commands/overview" class="next-step-card">
    <span class="step-icon">⚡</span>
    <div class="step-content">
      <h4>CLI Commands</h4>
      <p>Explore all 30+ code generators</p>
    </div>
  </a>
  <a href="/fields/overview" class="next-step-card">
    <span class="step-icon">📝</span>
    <div class="step-content">
      <h4>Field Types</h4>
      <p>Available field types and validation</p>
    </div>
  </a>
  <a href="/api/authentication" class="next-step-card">
    <span class="step-icon">🔐</span>
    <div class="step-content">
      <h4>Authentication</h4>
      <p>Auth system documentation</p>
    </div>
  </a>
</div>

<style>
.api-docs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.api-doc-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.api-doc-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
}

.api-doc-icon {
  font-size: 1.5rem;
}

.api-doc-content h4 {
  margin: 0 0 4px;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.api-doc-content p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
}

.next-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 24px 0;
}

.next-step-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 18px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.next-step-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
}

.step-icon {
  font-size: 1.5rem;
}

.step-content h4 {
  margin: 0 0 4px;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.step-content p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
}
</style>
