# Basic Field Types

Core field types for common data storage needs.

## string

Short text field, typically up to 255 characters.

### Usage

```bash
-f title:string:required
-f title:string:required,max:200
-f code:string:required,unique
```

### Generated Code

```python
# Model
title: str = Field(nullable=False, max_length=200)

# Create Schema
title: str = Field(min_length=1, max_length=200)

# Update Schema
title: Optional[str] = Field(default=None, max_length=200)
```

### Common Rules

| Rule | Example |
|------|---------|
| Required | `title:string:required` |
| Max length | `title:string:max:100` |
| Min length | `title:string:min:5` |
| Unique | `code:string:unique` |
| Index | `status:string:index` |

### Real Examples

```bash
# Product name
-f name:string:required,max:255

# SKU code
-f sku:string:required,unique,max:50

# Status field
-f status:string:required,index

# Short description
-f summary:string:nullable,max:500
```

---

## text

Long text field for content, descriptions, etc.

### Usage

```bash
-f body:text:required
-f description:text:nullable
-f content:text:required,min:50
```

### Generated Code

```python
# Model
body: str = Field(nullable=False)

# Create Schema
body: str = Field(min_length=50)

# Update Schema
body: Optional[str] = None
```

### Common Rules

| Rule | Example |
|------|---------|
| Required | `body:text:required` |
| Nullable | `description:text:nullable` |
| Min length | `body:text:min:100` |
| Max length | `body:text:max:10000` |

### Real Examples

```bash
# Blog post body
-f body:text:required,min:50

# Product description
-f description:text:nullable,max:5000

# User bio
-f bio:text:nullable,max:1000

# Terms and conditions
-f terms:text:required
```

---

## integer

Whole number field.

### Usage

```bash
-f quantity:integer:required
-f stock:integer:required,ge:0
-f rating:integer:required,ge:1,le:5
```

### Generated Code

```python
# Model
quantity: int = Field(nullable=False)

# Create Schema
quantity: int = Field(ge=0)

# Update Schema
quantity: Optional[int] = Field(default=None, ge=0)
```

### Common Rules

| Rule | Example |
|------|---------|
| Required | `count:integer:required` |
| Min value | `age:integer:ge:0` |
| Max value | `rating:integer:le:5` |
| Range | `rating:integer:ge:1,le:5` |
| Foreign key | `user_id:integer:foreign:users.id` |

### Real Examples

```bash
# Stock quantity
-f stock:integer:required,ge:0

# Age field
-f age:integer:required,ge:0,le:150

# Rating (1-5)
-f rating:integer:required,ge:1,le:5

# Sort order
-f sort_order:integer:nullable,ge:0

# View count
-f views:integer:required,ge:0

# Foreign key
-f category_id:integer:required,foreign:categories.id
```

---

## float

Decimal number field.

### Usage

```bash
-f price:float:required
-f latitude:float:required
-f discount:float:nullable,ge:0,le:100
```

### Generated Code

```python
# Model
price: float = Field(nullable=False)

# Create Schema
price: float = Field(ge=0)

# Update Schema
price: Optional[float] = Field(default=None, ge=0)
```

### Common Rules

| Rule | Example |
|------|---------|
| Required | `price:float:required` |
| Min value | `price:float:ge:0` |
| Max value | `discount:float:le:100` |
| Range | `rating:float:ge:0,le:5` |

### Real Examples

```bash
# Price (use money for currency)
-f price:float:required,ge:0

# Geographic coordinates
-f latitude:float:required
-f longitude:float:required

# Discount percentage
-f discount:float:nullable,ge:0,le:100

# Rating with decimals
-f rating:float:required,ge:0,le:5

# Weight in kg
-f weight:float:nullable,ge:0
```

!!! tip "Use money for currency"
    For currency values, prefer `money` type which uses `Decimal` for precision.

---

## boolean

True/False field.

### Usage

```bash
-f published:boolean:required
-f is_active:boolean:required
-f featured:boolean:nullable
```

### Generated Code

```python
# Model
published: bool = Field(nullable=False)

# Create Schema
published: bool

# Update Schema
published: Optional[bool] = None
```

### Common Rules

| Rule | Example |
|------|---------|
| Required | `active:boolean:required` |
| Nullable | `featured:boolean:nullable` |

### Real Examples

```bash
# Publication status
-f published:boolean:required

# Active flag
-f is_active:boolean:required

# Feature flag
-f featured:boolean:nullable

# Verification status
-f email_verified:boolean:required

# Soft delete alternative
-f is_deleted:boolean:required

# Visibility
-f is_visible:boolean:required
```

---

## datetime

Date and time field.

### Usage

```bash
-f published_at:datetime:nullable
-f starts_at:datetime:required
-f expires_at:datetime:nullable
```

### Generated Code

```python
from datetime import datetime

# Model
published_at: Optional[datetime] = Field(default=None, nullable=True)

# Create Schema
published_at: Optional[datetime] = None

# Update Schema
published_at: Optional[datetime] = None
```

### Common Rules

| Rule | Example |
|------|---------|
| Required | `starts_at:datetime:required` |
| Nullable | `published_at:datetime:nullable` |

### Real Examples

```bash
# Publication date
-f published_at:datetime:nullable

# Event dates
-f starts_at:datetime:required
-f ends_at:datetime:required

# Expiration
-f expires_at:datetime:nullable

# Scheduled actions
-f scheduled_for:datetime:nullable

# Last activity
-f last_login_at:datetime:nullable
```

!!! note "Auto timestamps"
    `created_at` and `updated_at` are automatically added by `BaseModel`.
    You don't need to define them.

---

## Type Comparison

| Type | Python | DB Column | Use Case |
|------|--------|-----------|----------|
| `string` | `str` | VARCHAR(255) | Names, codes, short text |
| `text` | `str` | TEXT | Long content, descriptions |
| `integer` | `int` | INTEGER | Counts, IDs, whole numbers |
| `float` | `float` | FLOAT | Decimals, coordinates |
| `boolean` | `bool` | BOOLEAN | Flags, toggles |
| `datetime` | `datetime` | TIMESTAMP | Dates with time |

## Next Steps

- [Advanced Types](advanced.md) - UUID, JSON, money, decimal
- [Validation Rules](validation.md) - All validation options
- [Make Commands](../commands/make.md) - Generate models
