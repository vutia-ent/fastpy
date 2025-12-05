# Architectural Patterns

Fastpy implements Laravel-style patterns adapted for Python/FastAPI.

## Key Principles

1. **Active Record Pattern** - Models handle their own persistence
2. **Route Model Binding** - Auto-resolve route params to model instances
3. **Model Concerns** - Laravel-style traits for reusable functionality
4. **FormRequest Validation** - Declarative validation with rules
5. **Soft Deletes by Default** - `deleted_at` timestamp on all models
6. **Query Scopes** - Reusable, chainable query constraints
7. **Facades** - Clean interfaces for common services
8. **Code Generation** - Sensible defaults in all generators

## MVC Pattern with Active Record

```
Request → Route → Controller → Model (Active Record) → Database
                      ↓
               Response
```

### Model (Active Record)

Models handle their own persistence - no session passing required.

```python
# app/models/post.py
from app.models.base import BaseModel
from app.models.concerns import HasScopes, GuardsAttributes

class Post(BaseModel, HasScopes, GuardsAttributes, table=True):
    __tablename__ = "posts"

    title: str = Field(max_length=200)
    body: str = Field(sa_column=Column(Text))
    user_id: int = Field(foreign_key="users.id")

    # Mass assignment protection
    _fillable = ['title', 'body', 'user_id']
    _guarded = ['id', 'created_at', 'updated_at', 'deleted_at']

    # Query scopes
    @classmethod
    def scope_published(cls, query):
        return query.where(cls.published == True)
```

### Controller (Active Record)

Controllers use Active Record methods - no session dependency needed.

```python
# app/controllers/post_controller.py
class PostController:
    @staticmethod
    async def create(data: PostCreate) -> Post:
        return await Post.create(**data.model_dump())

    @staticmethod
    async def update(id: int, data: PostUpdate) -> Post:
        post = await Post.find_or_fail(id)
        await post.update(**data.model_dump(exclude_unset=True))
        return post

    @staticmethod
    async def delete(id: int) -> dict:
        post = await Post.find_or_fail(id)
        await post.delete()  # Soft delete
        return {"message": "Post deleted successfully"}
```

### View (Route with Model Binding)

Routes use Route Model Binding to auto-resolve models from `{id}` params.

```python
# app/routes/post_routes.py
from app.utils.binding import bind_or_fail, bind_trashed

@router.get("/{id}")
async def get_post(post: Post = bind_or_fail(Post)):
    return post  # Auto-resolved from {id}

@router.put("/{id}")
async def update_post(
    post: Post = bind_or_fail(Post),
    data: PostUpdate
):
    await post.update(**data.model_dump(exclude_unset=True))
    return post

@router.post("/{id}/restore")
async def restore_post(post: Post = bind_trashed(Post)):
    await post.restore()
    return post
```

## Service Layer (Optional)

For complex business logic, add a service layer that uses Active Record internally.

```
Route → Service → Model (Active Record) → Database
```

### Service

Business logic using Active Record - no repository dependency needed.

```python
# app/services/post_service.py
class PostService:
    """
    Service for Post business logic.
    Uses Active Record pattern internally.
    """

    @staticmethod
    async def create(data: PostCreate) -> Post:
        """Create with business logic"""
        # Add business logic before creation
        post_data = data.model_dump()
        post_data['slug'] = slugify(post_data['title'])
        return await Post.create(**post_data)

    @staticmethod
    async def publish(id: int) -> Post:
        """Publish a post with validation"""
        post = await Post.find_or_fail(id)
        if not post.body:
            raise BadRequestException("Cannot publish post without body")
        await post.update(
            published=True,
            published_at=datetime.utcnow()
        )
        return post

    @staticmethod
    async def get_published(page: int = 1, per_page: int = 20):
        """Get published posts using query scopes"""
        return await Post.query().published().latest().paginate(page, per_page)
```

## Repository (Optional)

Repositories are **optional**. Prefer Query Scopes for simple queries.

```python
# app/repositories/post_repository.py
class PostRepository:
    """
    Use repositories only for:
    - Complex queries that don't fit as scopes
    - Custom caching logic
    - Multi-model operations
    - Testing with mocks
    """

    @staticmethod
    async def find_published():
        """Better as a query scope on the model"""
        return await Post.query().published().get()

    @staticmethod
    async def find_by_slug(slug: str):
        """Better as a query scope on the model"""
        return await Post.first_where(slug=slug)
```

::: tip Prefer Query Scopes
For simple queries, add scopes to your model instead of creating a repository:

```python
class Post(BaseModel, HasScopes, table=True):
    @classmethod
    def scope_published(cls, query):
        return query.where(cls.published == True)

# Usage
posts = await Post.query().published().latest().get()
```
:::

## Soft Delete Pattern

All models support soft deletion via `deleted_at` timestamp (enabled by default).

### Active Record Usage

```python
# Soft delete (default)
await post.delete()

# Hard delete (permanent)
await post.delete(force=True)

# Check if deleted
if post.is_deleted:
    print("Post has been soft deleted")

# Restore
await post.restore()
```

### Querying with Soft Deletes

```python
# Normal queries exclude soft-deleted records
posts = await Post.query().get()  # Only non-deleted

# Include soft-deleted records
posts = await Post.query().with_trashed().get()

# Only soft-deleted records
posts = await Post.query().only_trashed().get()

# Find including trashed
post = await Post.query().with_trashed().where(id=1).first()
```

### Route for Restore

```python
from app.utils.binding import bind_trashed

@router.post("/{id}/restore")
async def restore_post(post: Post = bind_trashed(Post)):
    """Restore a soft-deleted post"""
    await post.restore()
    return post
```

## FormRequest Validation

Laravel-style declarative validation using FormRequest classes.

```python
from app.validation import FormRequest, validated

class CreatePostRequest(FormRequest):
    rules = {
        'title': 'required|max:200',
        'body': 'required',
        'slug': 'required|unique:posts',
    }

    messages = {
        'title.required': 'Please provide a title.',
        'slug.unique': 'This slug is already taken.',
    }

    def authorize(self, user=None) -> bool:
        return user is not None

# Usage in routes
@router.post("/")
async def create(request: CreatePostRequest = validated(CreatePostRequest)):
    return await Post.create(**request.validated_data)
```

## Dependency Injection

FastAPI's dependency system with Active Record (no session passing required).

```python
# Current user authentication
async def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    # Validate token and return user
    return await User.find_or_fail(user_id)

# Route with dependencies
@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    return success_response(data=current_user)

# Combined with Route Model Binding
@router.put("/{id}")
async def update(
    post: Post = bind_or_fail(Post),  # Auto-resolved
    request: UpdatePostRequest = validated(UpdatePostRequest),  # Validated
    current_user: User = Depends(get_current_active_user)  # Authenticated
):
    await post.update(**request.validated_data)
    return post
```

## Response Pattern

Consistent API responses.

```python
# Success
{
    "success": true,
    "data": {...},
    "message": "Operation successful"
}

# Error
{
    "success": false,
    "error": {
        "message": "Not found",
        "code": "NOT_FOUND"
    }
}

# Paginated
{
    "success": true,
    "data": [...],
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 100,
        "pages": 5,
        "has_next": true,
        "has_prev": false
    }
}
```

## Exception Handling

Custom exceptions with automatic HTTP responses.

```python
# app/utils/exceptions.py
class NotFoundException(BaseAPIException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404
        )

# Usage
raise NotFoundException("Post not found")
```

## When to Use Each Pattern

### Active Record + Controller (Recommended Default)

Use for most projects:
- CRUD operations
- Standard business logic
- Small to large projects
- Rapid development

```bash
fastpy make:resource Post -f title:string:required -m -p
```

### Add Service Layer (Complex Business Logic)

When you need:
- Complex business rules
- Multi-step operations
- Side effects (emails, notifications)
- Logic reuse across controllers

```bash
fastpy make:resource Post -f title:string:required -m -p
fastpy make:service Post
```

### Add Repository (Rarely Needed)

Only when you need:
- Complex queries that don't fit as scopes
- Custom caching logic
- Multi-model transactions
- Testing with mocks

::: tip Default to Query Scopes
Most queries can be expressed as model scopes, making repositories unnecessary:

```python
# Instead of repository
posts = await Post.query().published().popular(1000).latest().get()
```
:::
