# Validation Rules

Complete reference for field validation rules.

## Rule Syntax

Rules are added after the field type, separated by commas:

```
name:type:rule1,rule2,rule3
```

### Examples

```bash
# Single rule
-f title:string:required

# Multiple rules
-f title:string:required,max:200,min:5

# Numeric constraints
-f price:float:required,ge:0,le:9999.99

# Unique with index
-f email:email:required,unique,index
```

---

## Required / Nullable

### required

Field cannot be null. Generates `nullable=False` in model.

```bash
-f title:string:required
```

**Generated:**
```python
# Model
title: str = Field(nullable=False)

# Create Schema - field is required
title: str
```

### nullable

Field can be null. Default behavior if neither specified.

```bash
-f description:text:nullable
```

**Generated:**
```python
# Model
description: Optional[str] = Field(default=None, nullable=True)

# Create Schema - field is optional
description: Optional[str] = None
```

---

## String Length

### max:N

Maximum length for strings, maximum value for numbers.

```bash
# String: max 200 characters
-f title:string:required,max:200

# Integer: max value 100
-f rating:integer:required,max:100
```

**Generated:**
```python
# Model
title: str = Field(nullable=False, max_length=200)

# Create Schema
title: str = Field(max_length=200)
```

### min:N

Minimum length for strings, minimum value for numbers.

```bash
# String: min 5 characters
-f title:string:required,min:5

# Integer: min value 1
-f quantity:integer:required,min:1
```

**Generated:**
```python
# Create Schema
title: str = Field(min_length=5)
quantity: int = Field(ge=1)
```

---

## Numeric Constraints

### ge:N (greater than or equal)

Value must be >= N. Alias: `gte:N`

```bash
-f price:float:required,ge:0
-f age:integer:required,ge:18
```

**Generated:**
```python
price: float = Field(ge=0)
age: int = Field(ge=18)
```

### le:N (less than or equal)

Value must be <= N. Alias: `lte:N`

```bash
-f discount:float:required,le:100
-f rating:integer:required,le:5
```

**Generated:**
```python
discount: float = Field(le=100)
rating: int = Field(le=5)
```

### gt:N (greater than)

Value must be > N.

```bash
-f count:integer:required,gt:0
```

**Generated:**
```python
count: int = Field(gt=0)
```

### lt:N (less than)

Value must be < N.

```bash
-f discount:float:required,lt:100
```

**Generated:**
```python
discount: float = Field(lt=100)
```

### Combined Range

```bash
# Rating 1-5
-f rating:integer:required,ge:1,le:5

# Price 0-9999.99
-f price:float:required,ge:0,le:9999.99

# Percentage 0-100
-f discount:percent:required,ge:0,le:100
```

---

## Database Constraints

### unique

Creates unique constraint on the column.

```bash
-f email:email:required,unique
-f sku:string:required,unique
-f slug:slug:required,unique
```

**Generated:**
```python
# Model
email: str = Field(nullable=False, unique=True)
```

### index

Creates database index for faster queries.

```bash
-f status:string:required,index
-f created_at:datetime:required,index
```

**Generated:**
```python
# Model
status: str = Field(nullable=False, index=True)
```

### unique + index

Often used together for searchable unique fields.

```bash
-f email:email:required,unique,index
```

---

## Foreign Keys

### foreign:table.column

Creates foreign key relationship.

```bash
-f user_id:integer:required,foreign:users.id
-f category_id:integer:nullable,foreign:categories.id
-f parent_id:integer:nullable,foreign:posts.id
```

**Generated:**
```python
# Model
user_id: int = Field(nullable=False, foreign_key="users.id")
category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
```

### Common Foreign Key Patterns

```bash
# Required relationship
-f user_id:integer:required,foreign:users.id

# Optional relationship
-f category_id:integer:nullable,foreign:categories.id

# Self-referencing (parent-child)
-f parent_id:integer:nullable,foreign:categories.id

# Multiple foreign keys
-f author_id:integer:required,foreign:users.id
-f reviewer_id:integer:nullable,foreign:users.id
```

---

## Rule Combinations

### Common Patterns

```bash
# Required string with length limit
-f title:string:required,max:200

# Required string with range
-f title:string:required,min:5,max:200

# Unique email
-f email:email:required,unique

# Indexed searchable field
-f status:string:required,index

# Price field
-f price:money:required,ge:0

# Rating 1-5
-f rating:integer:required,ge:1,le:5

# Optional foreign key
-f category_id:integer:nullable,foreign:categories.id

# Required foreign key with index
-f user_id:integer:required,foreign:users.id,index
```

### Complex Examples

```bash
# Blog post
python cli.py make:model Post \
  -f title:string:required,max:200,min:5 \
  -f slug:slug:required,unique,index \
  -f body:text:required,min:50 \
  -f excerpt:text:nullable,max:500 \
  -f views:integer:required,ge:0 \
  -f published:boolean:required \
  -f author_id:integer:required,foreign:users.id

# Product
python cli.py make:model Product \
  -f name:string:required,max:255 \
  -f sku:string:required,unique,max:50 \
  -f price:money:required,ge:0 \
  -f compare_price:money:nullable,ge:0 \
  -f stock:integer:required,ge:0 \
  -f weight:float:nullable,ge:0 \
  -f category_id:integer:required,foreign:categories.id

# User profile
python cli.py make:model Profile \
  -f user_id:integer:required,unique,foreign:users.id \
  -f bio:text:nullable,max:1000 \
  -f website:url:nullable \
  -f phone:phone:nullable \
  -f avatar:image:nullable
```

---

## Validation in Schemas

### Create Schema Validation

Rules generate Pydantic Field validators:

```python
class PostCreate(BaseModel):
    # From: title:string:required,max:200,min:5
    title: str = Field(min_length=5, max_length=200)

    # From: price:money:required,ge:0
    price: Decimal = Field(ge=0)

    # From: rating:integer:required,ge:1,le:5
    rating: int = Field(ge=1, le=5)
```

### Update Schema Validation

Update schemas make all fields optional but keep validations:

```python
class PostUpdate(BaseModel):
    # All optional, but if provided, must be valid
    title: Optional[str] = Field(default=None, min_length=5, max_length=200)
    price: Optional[Decimal] = Field(default=None, ge=0)
    rating: Optional[int] = Field(default=None, ge=1, le=5)
```

---

## Rule Reference Table

| Rule | Applies To | Description | Example |
|------|------------|-------------|---------|
| `required` | All | Cannot be null | `title:string:required` |
| `nullable` | All | Can be null | `bio:text:nullable` |
| `unique` | All | Unique constraint | `email:email:unique` |
| `index` | All | Database index | `status:string:index` |
| `max:N` | string, text | Max length | `title:string:max:200` |
| `min:N` | string, text | Min length | `body:text:min:50` |
| `max:N` | numeric | Max value | `rating:integer:max:5` |
| `min:N` | numeric | Min value | `price:float:min:0` |
| `ge:N` | numeric | >= value | `price:float:ge:0` |
| `le:N` | numeric | <= value | `discount:float:le:100` |
| `gt:N` | numeric | > value | `count:integer:gt:0` |
| `lt:N` | numeric | < value | `discount:float:lt:100` |
| `foreign:t.c` | integer | Foreign key | `user_id:integer:foreign:users.id` |

## Next Steps

- [Field Types Overview](overview.md) - All field types
- [Make Commands](../commands/make.md) - Generate models
- [Examples](../examples/blog.md) - Real-world examples
