# Field Types Overview

FastCLI supports 15+ field types with automatic validation generation.

## Field Definition Syntax

Fields are defined using the format:

```
name:type:rule1,rule2,rule3
```

### Examples

```bash
# Simple field
-f title:string:required

# Field with max length
-f title:string:required,max:200

# Field with min and max
-f body:text:required,min:50,max:5000

# Numeric field with range
-f price:float:required,ge:0,le:9999.99

# Foreign key
-f user_id:integer:required,foreign:users.id
```

## Field Type Categories

### Basic Types

| Type | Python Type | Description |
|------|-------------|-------------|
| `string` | `str` | Short text (max 255 by default) |
| `text` | `str` | Long text |
| `integer` | `int` | Whole numbers |
| `float` | `float` | Decimal numbers |
| `boolean` | `bool` | True/False |

[Learn more about Basic Types](basic.md)

### Date & Time Types

| Type | Python Type | Description |
|------|-------------|-------------|
| `datetime` | `datetime` | Date and time |
| `date` | `date` | Date only |
| `time` | `time` | Time only |

### Specialized String Types

| Type | Python Type | Description |
|------|-------------|-------------|
| `email` | `EmailStr` | Validated email |
| `url` | `str` | URL string |
| `slug` | `str` | URL-friendly slug |
| `phone` | `str` | Phone number |
| `ip` | `str` | IP address |
| `color` | `str` | Hex color code |

### File Types

| Type | Python Type | Description |
|------|-------------|-------------|
| `file` | `str` | File path |
| `image` | `str` | Image path |

### Advanced Types

| Type | Python Type | Description |
|------|-------------|-------------|
| `uuid` | `UUID` | UUID identifier |
| `json` | `dict` | JSON data |
| `decimal` | `Decimal` | Precise decimal |
| `money` | `Decimal` | Currency amount |
| `percent` | `Decimal` | Percentage |

[Learn more about Advanced Types](advanced.md)

## Validation Rules

| Rule | Description | Example |
|------|-------------|---------|
| `required` | Cannot be null | `title:string:required` |
| `nullable` | Can be null | `bio:text:nullable` |
| `unique` | Unique constraint | `email:email:unique` |
| `index` | Database index | `status:string:index` |
| `max:N` | Maximum length/value | `title:string:max:200` |
| `min:N` | Minimum length/value | `body:text:min:50` |
| `ge:N` | Greater than or equal | `price:float:ge:0` |
| `le:N` | Less than or equal | `rating:integer:le:5` |
| `gt:N` | Greater than | `age:integer:gt:0` |
| `lt:N` | Less than | `discount:float:lt:100` |
| `foreign:table.col` | Foreign key | `user_id:integer:foreign:users.id` |

[Learn more about Validation Rules](validation.md)

## Quick Reference

### Common Patterns

```bash
# Blog post
-f title:string:required,max:200
-f slug:slug:required,unique
-f body:text:required
-f published:boolean:required
-f author_id:integer:required,foreign:users.id

# Product
-f name:string:required,max:255
-f price:money:required,ge:0
-f stock:integer:required,ge:0
-f sku:string:required,unique

# User profile
-f bio:text:nullable,max:1000
-f avatar:image:nullable
-f website:url:nullable
-f phone:phone:nullable

# Order
-f total:money:required,ge:0
-f status:string:required,index
-f notes:text:nullable
-f user_id:integer:required,foreign:users.id
```

### Type Selection Guide

| Need | Use Type | Example |
|------|----------|---------|
| Short text | `string` | Names, titles |
| Long text | `text` | Descriptions, content |
| Whole numbers | `integer` | Counts, quantities |
| Decimals | `float` | Ratings, coordinates |
| Precise decimals | `decimal` | Financial calculations |
| Money | `money` | Prices, totals |
| Percentages | `percent` | Discounts, rates |
| Yes/No | `boolean` | Flags, toggles |
| Timestamps | `datetime` | Created at, updated at |
| Dates only | `date` | Birth dates, due dates |
| Times only | `time` | Opening hours |
| Email addresses | `email` | Contact emails |
| Web links | `url` | Websites, links |
| URL slugs | `slug` | SEO-friendly URLs |
| Phone numbers | `phone` | Contact numbers |
| IP addresses | `ip` | Client IPs, server IPs |
| Colors | `color` | Theme colors |
| File paths | `file` | Documents |
| Image paths | `image` | Avatars, photos |
| Unique IDs | `uuid` | External references |
| Structured data | `json` | Metadata, settings |

## Generated Code Example

For field definition:
```bash
-f title:string:required,max:200
```

### Model Field

```python
class Post(BaseModel, table=True):
    title: str = Field(nullable=False, max_length=200)
```

### Create Schema

```python
class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
```

### Update Schema

```python
class PostUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
```

### Read Schema

```python
class PostRead(BaseModel):
    title: str
```

## Next Steps

- [Basic Types](basic.md) - String, integer, float, boolean
- [Advanced Types](advanced.md) - UUID, JSON, money, decimal
- [Validation Rules](validation.md) - All validation options
