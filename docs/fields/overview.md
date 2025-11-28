# Field Types Overview

Fastpy CLI supports a rich set of field types with built-in validation rules.

## Field Definition Syntax

```
name:type:rules
```

- **name** - Field name (snake_case)
- **type** - Field type (see below)
- **rules** - Comma-separated validation rules

## Examples

```bash
# Basic
-f title:string:required

# With max length
-f title:string:required,max:200

# Multiple rules
-f email:email:required,unique,index

# Foreign key
-f user_id:integer:foreign:users.id
```

## Available Types

### Basic Types

| Type | Python Type | SQL Type |
|------|-------------|----------|
| `string` | `str` | `VARCHAR(255)` |
| `text` | `str` | `TEXT` |
| `integer` | `int` | `INTEGER` |
| `float` | `float` | `FLOAT` |
| `boolean` | `bool` | `BOOLEAN` |
| `datetime` | `datetime` | `DATETIME` |

### Advanced Types

| Type | Python Type | Description |
|------|-------------|-------------|
| `email` | `str` | Email with validation |
| `url` | `str` | URL with validation |
| `uuid` | `UUID` | UUID primary/foreign key |
| `decimal` | `Decimal` | Precise decimal |
| `money` | `Decimal` | Currency amount |
| `percent` | `Decimal` | Percentage (0-100) |
| `date` | `date` | Date only |
| `time` | `time` | Time only |
| `phone` | `str` | Phone number |
| `slug` | `str` | URL-friendly slug |
| `ip` | `str` | IP address |
| `json` | `dict` | JSON/JSONB |
| `color` | `str` | Hex color code |
| `file` | `str` | File path |
| `image` | `str` | Image path |

## Validation Rules

| Rule | Description | Example |
|------|-------------|---------|
| `required` | Field cannot be null | `title:string:required` |
| `nullable` | Field can be null | `bio:text:nullable` |
| `unique` | Unique constraint | `email:email:unique` |
| `index` | Create index | `slug:slug:index` |
| `max:N` | Maximum length/value | `title:string:max:200` |
| `min:N` | Minimum length/value | `age:integer:min:0` |
| `default:V` | Default value | `active:boolean:default:true` |
| `foreign:T.C` | Foreign key | `user_id:integer:foreign:users.id` |

## Quick Reference

```bash
# User profile fields
-f username:string:required,unique,max:50,index
-f email:email:required,unique
-f password:string:required,min:8
-f avatar:image:nullable
-f bio:text:nullable,max:500
-f is_active:boolean:default:true
-f role:string:default:user

# Blog post fields
-f title:string:required,max:200
-f slug:slug:required,unique,index
-f body:text:required
-f excerpt:string:nullable,max:300
-f featured_image:image:nullable
-f published:boolean:default:false
-f published_at:datetime:nullable
-f author_id:integer:required,foreign:users.id

# E-commerce fields
-f name:string:required,max:200
-f sku:string:required,unique,max:50
-f price:money:required,min:0
-f sale_price:money:nullable
-f quantity:integer:default:0,min:0
-f weight:decimal:nullable
-f category_id:integer:foreign:categories.id
```

## Next Steps

- [Basic Types](/fields/basic) - Detailed basic type documentation
- [Advanced Types](/fields/advanced) - Complex field types
- [Validation Rules](/fields/validation) - All validation options
