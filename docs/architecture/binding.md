# Route Model Binding

Route model binding automatically resolves route parameters to model instances, reducing boilerplate code.

## Overview

Instead of manually fetching models by ID in every route:

```python
# Without binding (manual)
@router.get("/users/{id}")
async def show_user(id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

Use route model binding:

```python
# With binding (automatic)
from app.utils.binding import bind_or_fail

@router.get("/users/{id}")
async def show_user(user: User = bind_or_fail(User)):
    return user  # User is automatically fetched by ID
```

## Installation

Route model binding is built into Fastpy. Import from `app.utils.binding`:

```python
from app.utils.binding import bind, bind_or_fail, bind_trashed
```

## Basic Usage

### bind()

Returns `None` if not found:

```python
@router.get("/users/{id}")
async def show_user(user: User = bind(User)):
    if not user:
        return {"message": "User not found"}
    return user
```

### bind_or_fail()

Raises 404 if not found:

```python
@router.get("/users/{id}")
async def show_user(user: User = bind_or_fail(User)):
    return user  # Raises 404 if user doesn't exist
```

### bind_trashed()

Include soft-deleted records:

```python
@router.post("/users/{id}/restore")
async def restore_user(user: User = bind_trashed(User)):
    await user.restore()
    return user
```

## Custom Field Binding

By default, binding uses `id`. Bind by other fields:

```python
# Bind by slug
@router.get("/posts/{slug}")
async def show_post(post: Post = bind(Post, param="slug", field="slug")):
    return post

# Bind by UUID
@router.get("/orders/{uuid}")
async def show_order(order: Order = bind_or_fail(Order, param="uuid", field="uuid")):
    return order

# Bind by email
@router.get("/users/email/{email}")
async def find_by_email(user: User = bind(User, param="email", field="email")):
    return user
```

## With Form Validation

Combine with FormRequest validation:

```python
from app.utils.binding import bind_or_fail
from app.requests.user_request import UpdateUserRequest

@router.put("/users/{id}")
async def update_user(
    user: User = bind_or_fail(User),
    request: UpdateUserRequest = Depends()
):
    await user.update(**request.validated_data)
    return user
```

## CRUD Routes with Binding

Complete example with all CRUD operations:

```python
from fastapi import APIRouter, Depends
from app.utils.binding import bind, bind_or_fail, bind_trashed
from app.models.post import Post, PostCreate, PostUpdate

router = APIRouter()

# List
@router.get("/")
async def list_posts():
    return await Post.query().published().latest().get()

# Create
@router.post("/", status_code=201)
async def create_post(data: PostCreate):
    return await Post.create(**data.model_dump())

# Read
@router.get("/{id}")
async def show_post(post: Post = bind_or_fail(Post)):
    return post

# Update
@router.put("/{id}")
async def update_post(
    data: PostUpdate,
    post: Post = bind_or_fail(Post)
):
    await post.update(**data.model_dump(exclude_unset=True))
    return post

# Delete (soft)
@router.delete("/{id}")
async def delete_post(post: Post = bind_or_fail(Post)):
    await post.delete()
    return {"message": "Post deleted"}

# Restore
@router.post("/{id}/restore")
async def restore_post(post: Post = bind_trashed(Post)):
    await post.restore()
    return post
```

## Generating Routes with Binding

Use the `--binding` flag to generate routes with model binding:

```bash
# Generate routes with binding
fastpy make:route Post --binding

# With authentication
fastpy make:route Post --protected --binding

# Full resource with binding
fastpy make:resource Post -f title:string:required -m -p --binding
```

## How It Works

The binding functions create FastAPI dependencies that:

1. Extract the route parameter (default: `id`)
2. Query the database for the model
3. Handle soft-deleted records appropriately
4. Return the model instance or raise an exception

```python
# Simplified implementation
def bind_or_fail(model_class, param: str = "id", field: str = "id"):
    async def dependency(
        request: Request,
        session: AsyncSession = Depends(get_session)
    ):
        value = request.path_params.get(param)
        instance = await session.execute(
            select(model_class)
            .where(getattr(model_class, field) == value)
            .where(model_class.deleted_at.is_(None))
        )
        result = instance.scalar_one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail=f"{model_class.__name__} not found")
        return result
    return Depends(dependency)
```

## Best Practices

### 1. Use bind_or_fail for Required Resources

```python
# Good - raises 404 automatically
@router.get("/users/{id}")
async def show_user(user: User = bind_or_fail(User)):
    return user

# Avoid - manual checking
@router.get("/users/{id}")
async def show_user(user: User = bind(User)):
    if not user:
        raise HTTPException(status_code=404)  # Redundant
    return user
```

### 2. Use bind for Optional Lookups

```python
# Good - handle missing gracefully
@router.get("/users/email/{email}")
async def find_by_email(user: User = bind(User, param="email", field="email")):
    if not user:
        return {"exists": False}
    return {"exists": True, "user": user}
```

### 3. Use bind_trashed for Restore Operations

```python
# Good - can find soft-deleted records
@router.post("/posts/{id}/restore")
async def restore(post: Post = bind_trashed(Post)):
    await post.restore()
    return post
```

### 4. Combine with Authentication

```python
from app.utils.auth import get_current_active_user

@router.put("/posts/{id}")
async def update_post(
    post: Post = bind_or_fail(Post),
    data: PostUpdate = Depends(),
    current_user: User = Depends(get_current_active_user)
):
    # Check ownership
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await post.update(**data.model_dump(exclude_unset=True))
    return post
```

## Binding Options Reference

| Function | Behavior |
|----------|----------|
| `bind(Model)` | Returns `None` if not found |
| `bind_or_fail(Model)` | Raises 404 if not found |
| `bind_trashed(Model)` | Includes soft-deleted records |
| `bind(Model, field="slug")` | Bind by custom field |
| `bind(Model, param="uuid")` | Use custom route parameter |

Fastpy uses explicit dependency injection for route model binding, which aligns with FastAPI's design philosophy and provides full type safety.
