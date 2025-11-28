# Validation Rules

Complete reference for field validation rules.

## required

Field must have a value (not null).

```bash
-f title:string:required
```

### Generated Code

```python
title: str  # No Optional, no default
```

## nullable

Field can be null.

```bash
-f bio:text:nullable
-f deleted_at:datetime:nullable
```

### Generated Code

```python
from typing import Optional

bio: Optional[str] = None
deleted_at: Optional[datetime] = None
```

## unique

Create unique constraint.

```bash
-f email:email:unique
-f sku:string:unique
```

### Generated Code

```python
email: str = Field(unique=True)
```

### Composite Unique

For multi-column uniqueness, add constraint manually:

```python
from sqlalchemy import UniqueConstraint

class OrderItem(BaseModel, table=True):
    __table_args__ = (
        UniqueConstraint('order_id', 'product_id', name='unique_order_product'),
    )
```

## index

Create database index for faster queries.

```bash
-f email:email:index
-f slug:slug:unique,index
```

### Generated Code

```python
email: str = Field(index=True)
```

### When to Index

- Columns used in `WHERE` clauses
- Columns used in `ORDER BY`
- Foreign key columns
- Columns used in `JOIN` conditions

## max:N

Maximum length (strings) or value (numbers).

```bash
-f title:string:max:200
-f age:integer:max:150
-f rating:float:max:5
```

### Generated Code

```python
# String
title: str = Field(max_length=200)

# Integer
age: int = Field(le=150)

# Float
rating: float = Field(le=5.0)
```

## min:N

Minimum length (strings) or value (numbers).

```bash
-f password:string:min:8
-f age:integer:min:0
-f price:decimal:min:0
```

### Generated Code

```python
# String - uses validator
password: str = Field(min_length=8)

# Integer
age: int = Field(ge=0)

# Decimal
price: Decimal = Field(ge=Decimal('0'))
```

## default:V

Set default value.

```bash
-f status:string:default:draft
-f is_active:boolean:default:true
-f count:integer:default:0
-f role:string:default:user
```

### Generated Code

```python
status: str = Field(default="draft")
is_active: bool = Field(default=True)
count: int = Field(default=0)
role: str = Field(default="user")
```

### Special Defaults

```bash
# Current timestamp
-f created_at:datetime:default:now

# Empty JSON
-f metadata:json:default:{}

# Empty array (JSON)
-f tags:json:default:[]
```

## foreign:table.column

Create foreign key relationship.

```bash
-f user_id:integer:foreign:users.id
-f category_id:integer:foreign:categories.id,nullable
```

### Generated Code

```python
user_id: int = Field(foreign_key="users.id")
category_id: Optional[int] = Field(foreign_key="categories.id", nullable=True)
```

### Cascade Options

Add cascade behavior manually:

```python
from sqlalchemy import ForeignKey

user_id: int = Field(
    sa_column=Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE")
    )
)
```

## Combining Rules

Rules can be combined with commas:

```bash
# Required, unique, with max length
-f email:email:required,unique,max:255

# Nullable with default
-f role:string:nullable,default:user

# Required, indexed, with constraints
-f price:decimal:required,index,min:0

# Foreign key, nullable
-f parent_id:integer:foreign:categories.id,nullable
```

## Rule Precedence

1. `required` and `nullable` are mutually exclusive
2. `default` makes field optional (not required)
3. `unique` implies `index` in most cases
4. Type-specific validation is always applied

## Validation Examples

### User Model

```bash
python cli.py make:model User \
  -f email:email:required,unique,index \
  -f password:string:required,min:8 \
  -f username:string:required,unique,max:50 \
  -f is_active:boolean:default:true \
  -f role:string:default:user \
  -f email_verified_at:datetime:nullable
```

### Product Model

```bash
python cli.py make:model Product \
  -f name:string:required,max:200 \
  -f sku:string:required,unique,max:50 \
  -f price:money:required,min:0 \
  -f sale_price:money:nullable \
  -f quantity:integer:default:0,min:0 \
  -f is_active:boolean:default:true \
  -f category_id:integer:foreign:categories.id
```

### Order Model

```bash
python cli.py make:model Order \
  -f order_number:string:required,unique,index \
  -f user_id:integer:required,foreign:users.id \
  -f status:string:default:pending \
  -f total:money:required,min:0 \
  -f notes:text:nullable \
  -f shipped_at:datetime:nullable \
  -f delivered_at:datetime:nullable
```
