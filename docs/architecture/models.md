# Models & Concerns

Fastpy models extend SQLModel with Laravel-style concerns (traits) for enhanced functionality.

## Base Model

All models inherit from `BaseModel` which provides:

```python
from app.models.base import BaseModel

class Post(BaseModel, table=True):
    __tablename__ = "posts"

    title: str = Field(max_length=200)
    body: str = Field(sa_column=Column(Text))
```

### Standard Fields

Every model automatically includes:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Auto-incrementing primary key |
| `created_at` | `datetime` | Timestamp on creation |
| `updated_at` | `datetime` | Timestamp on update |
| `deleted_at` | `datetime?` | Soft delete timestamp |

### Built-in Methods

```python
# Soft delete
post.soft_delete()
await session.commit()

# Restore
post.restore()
await session.commit()

# Check if deleted
if post.is_deleted:
    print("Post is soft deleted")

# Update timestamps
post.touch()
```

## Active Record Methods

Models support Active Record-style operations:

```python
# Create
user = await User.create(name="John", email="john@example.com")

# Find
user = await User.find(1)                          # Returns None if not found
user = await User.find_or_fail(1)                  # Raises NotFoundException

# Query
users = await User.where(active=True)              # List of matching records
user = await User.first_where(email="john@example.com")
user = await User.first_or_fail(email="john@example.com")

# Update
user.name = "Jane"
await user.save()

await user.update(name="Jane", email="jane@example.com")

# Delete
await user.delete()              # Soft delete
await user.delete(force=True)    # Hard delete
```

## Model Concerns

Mix in Laravel-style functionality to your models:

```python
from app.models.base import BaseModel
from app.models.concerns import (
    HasCasts, HasAttributes, HasEvents, HasScopes, GuardsAttributes
)

class Post(BaseModel, HasCasts, HasAttributes, HasEvents, HasScopes, GuardsAttributes, table=True):
    __tablename__ = "posts"

    title: str
    body: str
    settings: Optional[str] = None
    is_published: bool = False
    views: int = 0
```

## HasCasts

Auto-convert database values to Python types:

```python
class Post(BaseModel, HasCasts, table=True):
    _casts = {
        'settings': 'json',        # JSON string <-> dict
        'is_active': 'boolean',    # 1/0 <-> True/False
        'metadata': 'dict',        # Ensure dict type
        'tags': 'list',            # Ensure list type
        'price': 'decimal:2',      # Decimal with 2 places
        'published_at': 'datetime',
    }
```

### Usage

```python
post.settings = {'featured': True}  # Stored as JSON string
print(post.settings)                 # Returns dict: {'featured': True}
```

### Available Cast Types

| Cast Type | Description |
|-----------|-------------|
| `boolean` | Convert to `True`/`False` |
| `integer` | Convert to `int` |
| `float` | Convert to `float` |
| `string` | Convert to `str` |
| `json` | JSON encode/decode |
| `dict` | Ensure dict type |
| `list` | Ensure list type |
| `date` | Convert to `date` object |
| `datetime` | Convert to `datetime` object |
| `decimal:N` | Decimal with N places |

## HasAttributes

Computed properties and value transformers:

```python
from app.models.concerns import accessor, mutator

class User(BaseModel, HasAttributes, table=True):
    first_name: str
    last_name: str
    password: str

    # Virtual attributes to include in serialization
    _appends = ['full_name']
    _hidden = ['password']

    @accessor
    def full_name(self) -> str:
        """Computed property."""
        return f"{self.first_name} {self.last_name}"

    @mutator('password')
    def hash_password(self, value: str) -> str:
        """Transform value before storing."""
        from app.utils.auth import get_password_hash
        return get_password_hash(value)
```

### Usage

```python
user.full_name          # "John Doe" (computed)
user.password = "secret" # Automatically hashed
user.to_dict()          # Includes full_name, excludes password
```

### Configuration

| Property | Description |
|----------|-------------|
| `_appends` | Virtual attributes to include in serialization |
| `_hidden` | Attributes to exclude from serialization |
| `_visible` | Only include these attributes in serialization |

## HasEvents

Hook into model lifecycle:

```python
from app.models.concerns import HasEvents, ModelObserver

class UserObserver(ModelObserver):
    def creating(self, user):
        user.uuid = str(uuid4())

    def created(self, user):
        send_welcome_email(user)

    def updating(self, user):
        pass

    def updated(self, user):
        pass

    def deleting(self, user):
        # Return False to cancel deletion
        if user.is_admin:
            return False
        return True

    def deleted(self, user):
        pass

class User(BaseModel, HasEvents, table=True):
    @classmethod
    def booted(cls):
        cls.observe(UserObserver())

        # Or inline handlers:
        cls.creating(lambda u: setattr(u, 'uuid', str(uuid4())))
```

### Available Events

| Event | Description |
|-------|-------------|
| `creating` | Before a new model is saved |
| `created` | After a new model is saved |
| `updating` | Before an existing model is updated |
| `updated` | After an existing model is updated |
| `saving` | Before any save (create or update) |
| `saved` | After any save (create or update) |
| `deleting` | Before a model is deleted |
| `deleted` | After a model is deleted |
| `restoring` | Before a soft-deleted model is restored |
| `restored` | After a soft-deleted model is restored |

## HasScopes

Reusable query constraints:

```python
class Post(BaseModel, HasScopes, table=True):
    @classmethod
    def scope_published(cls, query):
        return query.where(cls.is_published == True)

    @classmethod
    def scope_popular(cls, query, min_views: int = 1000):
        return query.where(cls.views >= min_views)

    @classmethod
    def scope_by_author(cls, query, author_id: int):
        return query.where(cls.author_id == author_id)
```

### Usage

```python
# Fluent query building
posts = await Post.query().published().popular(5000).latest().get()
posts = await Post.query().by_author(1).paginate(page=2, per_page=20)

# With soft deletes
posts = await Post.query().with_trashed().get()   # Include deleted
posts = await Post.query().only_trashed().get()   # Only deleted
```

### QueryBuilder Methods

| Method | Description |
|--------|-------------|
| `where(**kwargs)` | Filter by conditions |
| `where_in(field, values)` | Filter where field in values |
| `where_null(field)` | Filter where field is null |
| `where_not_null(field)` | Filter where field is not null |
| `order_by(field, direction)` | Order results |
| `latest(field='created_at')` | Order by newest first |
| `oldest(field='created_at')` | Order by oldest first |
| `limit(n)` | Limit results |
| `offset(n)` | Skip results |
| `get()` | Execute and get all results |
| `first()` | Get first result |
| `count()` | Count results |
| `exists()` | Check if any results exist |
| `paginate(page, per_page)` | Paginate results |
| `with_trashed()` | Include soft-deleted |
| `only_trashed()` | Only soft-deleted |

## GuardsAttributes

Protect against mass assignment vulnerabilities:

```python
class User(BaseModel, GuardsAttributes, table=True):
    # Whitelist: only these can be mass-assigned
    _fillable = ['name', 'email', 'password']

    # OR blacklist: everything except these
    _guarded = ['is_admin', 'role']
```

### Usage

```python
# Safe mass assignment
user = await User.create(**request.validated_data)  # Only fillable fields
user.fill(name="John", is_admin=True)               # is_admin ignored

# Bypass protection when needed
user.force_fill(is_admin=True)

# Temporarily disable protection
from app.models.concerns import Unguarded
with Unguarded(User):
    await User.create(is_admin=True)
```

### Configuration

| Property | Description |
|----------|-------------|
| `_fillable` | Whitelist of mass-assignable fields |
| `_guarded` | Blacklist of protected fields |

::: warning
Use either `_fillable` OR `_guarded`, not both. `_fillable` is recommended for explicit control.
:::

## Combining Concerns

Mix multiple concerns for powerful models:

```python
from app.models.base import BaseModel
from app.models.concerns import (
    HasCasts, HasAttributes, HasEvents, HasScopes, GuardsAttributes
)

class Post(
    BaseModel,
    HasCasts,
    HasAttributes,
    HasEvents,
    HasScopes,
    GuardsAttributes,
    table=True
):
    __tablename__ = "posts"

    title: str
    slug: str
    body: str
    settings: Optional[str] = None
    is_published: bool = False
    published_at: Optional[datetime] = None
    author_id: int
    views: int = 0

    # Casts
    _casts = {
        'settings': 'json',
        'published_at': 'datetime',
    }

    # Attributes
    _appends = ['excerpt', 'reading_time']
    _hidden = []

    # Guards
    _fillable = ['title', 'body', 'settings']

    @accessor
    def excerpt(self) -> str:
        return self.body[:200] + '...' if len(self.body) > 200 else self.body

    @accessor
    def reading_time(self) -> int:
        words = len(self.body.split())
        return max(1, words // 200)

    @mutator('title')
    def set_title(self, value: str) -> str:
        # Auto-generate slug when title is set
        self.slug = slugify(value)
        return value

    @classmethod
    def scope_published(cls, query):
        return query.where(cls.is_published == True)

    @classmethod
    def scope_by_author(cls, query, author_id: int):
        return query.where(cls.author_id == author_id)

    @classmethod
    def booted(cls):
        cls.creating(lambda p: setattr(p, 'views', 0))
```

### Usage

```python
# Create with mass assignment protection
post = await Post.create(
    title="My Post",
    body="Content here...",
    settings={'featured': True},
    is_admin=True  # Ignored - not fillable
)

# Query with scopes
posts = await Post.query().published().by_author(1).latest().get()

# Access computed properties
print(post.excerpt)       # "Content here..."
print(post.reading_time)  # 1

# Settings auto-cast to dict
print(post.settings['featured'])  # True
```
