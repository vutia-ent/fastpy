# Architectural Patterns

Fastpy implements proven patterns for maintainable, scalable APIs.

## MVC Pattern

The primary architecture follows Model-View-Controller.

```
Request → Route (View) → Controller → Model → Database
                ↓
           Response
```

### Model

Data structure and database representation.

```python
# app/models/post.py
class Post(BaseModel, table=True):
    __tablename__ = "posts"

    title: str = Field(max_length=200)
    body: str = Field(sa_column=Column(Text))
    user_id: int = Field(foreign_key="users.id")
```

### Controller

Business logic and data operations.

```python
# app/controllers/post_controller.py
class PostController:
    @staticmethod
    async def create(session: AsyncSession, data: dict, user_id: int):
        post = Post(**data, user_id=user_id)
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post
```

### View (Route)

HTTP interface and request handling.

```python
# app/routes/post_routes.py
@router.post("/")
async def create_post(
    data: PostCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    post = await PostController.create(session, data.dict(), current_user.id)
    return success_response(data=post, message="Post created")
```

## Service/Repository Pattern

For complex domains, add service and repository layers.

```
Route → Service → Repository → Model → Database
```

### Repository

Pure data access, no business logic.

```python
# app/repositories/post_repository.py
class PostRepository(BaseRepository[Post]):
    model = Post

    async def find_published(self, session: AsyncSession):
        result = await session.execute(
            select(Post)
            .where(Post.published == True)
            .where(Post.deleted_at.is_(None))
            .order_by(Post.published_at.desc())
        )
        return result.scalars().all()

    async def find_by_slug(self, session: AsyncSession, slug: str):
        result = await session.execute(
            select(Post)
            .where(Post.slug == slug)
            .where(Post.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()
```

### Service

Business logic with lifecycle hooks.

```python
# app/services/post_service.py
class PostService(BaseService[Post]):
    model = Post

    def __init__(self):
        self.repository = PostRepository()

    async def before_create(self, data: dict) -> dict:
        # Auto-generate slug
        if 'slug' not in data:
            data['slug'] = slugify(data['title'])
        return data

    async def publish(self, session: AsyncSession, post: Post) -> Post:
        post.published = True
        post.published_at = datetime.utcnow()
        await session.commit()
        return post
```

## Soft Delete Pattern

All models support soft deletion via `deleted_at` timestamp.

```python
class BaseModel(SQLModel):
    deleted_at: Optional[datetime] = None

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()

    def restore(self):
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
```

### Usage

```python
# Soft delete
post.soft_delete()
await session.commit()

# Restore
post.restore()
await session.commit()

# Query (filter deleted)
select(Post).where(Post.deleted_at.is_(None))
```

## Dependency Injection

FastAPI's dependency system for clean, testable code.

```python
# Database session
async def get_session():
    async with async_session() as session:
        yield session

# Current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    # Validate token and return user
    pass

# Route with dependencies
@router.get("/profile")
async def get_profile(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return success_response(data=current_user)
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

### MVC Only (Simple APIs)

- CRUD operations
- Minimal business logic
- Small to medium projects
- Rapid prototyping

### Service/Repository (Complex Domains)

- Complex business rules
- Multiple data sources
- Team projects
- Enterprise applications
- When business logic needs unit testing
