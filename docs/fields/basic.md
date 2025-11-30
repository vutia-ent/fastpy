# Basic Field Types

Core field types for common data storage needs.

## string

Variable-length character string.

```bash
-f name:string:required,max:100
```

### Generated Code

```python
name: str = Field(max_length=100)
```

### SQL Type

- PostgreSQL: `VARCHAR(N)`
- MySQL: `VARCHAR(N)`

### Common Rules

```bash
-f title:string:required,max:200
-f code:string:required,unique,max:10
-f slug:string:index
```

## text

Unlimited length text.

```bash
-f body:text:required
```

### Generated Code

```python
from sqlalchemy import Column, Text

body: str = Field(sa_column=Column(Text))
```

### Use Cases

- Blog post content
- Descriptions
- Comments
- Any long-form text

## integer

Whole numbers.

```bash
-f count:integer:default:0
```

### Generated Code

```python
count: int = Field(default=0)
```

### With Constraints

```bash
-f age:integer:required,min:0,max:150
-f quantity:integer:default:0,min:0
```

```python
age: int = Field(ge=0, le=150)
quantity: int = Field(default=0, ge=0)
```

## float

Floating-point numbers.

```bash
-f rating:float:min:0,max:5
```

### Generated Code

```python
rating: float = Field(ge=0, le=5)
```

::: tip Precision
For financial data, use `decimal` or `money` types instead of `float`.
:::

## boolean

True/false values.

```bash
-f is_active:boolean:default:true
-f is_verified:boolean:default:false
```

### Generated Code

```python
is_active: bool = Field(default=True)
is_verified: bool = Field(default=False)
```

### Naming Conventions

```bash
# Recommended prefixes
-f is_active:boolean       # is_
-f has_permission:boolean  # has_
-f can_edit:boolean        # can_
-f should_notify:boolean   # should_
```

## datetime

Date and time combined.

```bash
-f published_at:datetime:nullable
-f expires_at:datetime:required
```

### Generated Code

```python
from datetime import datetime
from typing import Optional

published_at: Optional[datetime] = None
expires_at: datetime
```

### Automatic Timestamps

The `BaseModel` includes automatic timestamps:

```python
created_at: datetime = Field(default_factory=datetime.utcnow)
updated_at: datetime = Field(default_factory=datetime.utcnow)
```

Update with `model.touch()`.

## Combining Types

```bash
python cli.py make:model Article \
  -f title:string:required,max:200 \
  -f slug:string:required,unique,index \
  -f body:text:required \
  -f views:integer:default:0 \
  -f rating:float:nullable \
  -f is_featured:boolean:default:false \
  -f published_at:datetime:nullable \
  -m
```

### Generated Model

```python
from typing import Optional
from datetime import datetime
from sqlmodel import Field
from sqlalchemy import Column, Text
from app.models.base import BaseModel

class Article(BaseModel, table=True):
    __tablename__ = "articles"

    title: str = Field(max_length=200)
    slug: str = Field(unique=True, index=True)
    body: str = Field(sa_column=Column(Text))
    views: int = Field(default=0)
    rating: Optional[float] = None
    is_featured: bool = Field(default=False)
    published_at: Optional[datetime] = None
```

## Type Defaults

| Type | Default Value | Nullable |
|------|---------------|----------|
| `string` | `""` or required | No |
| `text` | `""` or required | No |
| `integer` | `0` | No |
| `float` | `0.0` | No |
| `boolean` | `False` | No |
| `datetime` | `None` | Yes |

Override with `nullable` or `default:value` rules.
