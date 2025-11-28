---
title: Field Types Overview
description: All available field types and their automatic validations
---

Fastpy supports 15+ field types that automatically generate appropriate SQLModel fields and Pydantic validations.

## Field Syntax

```
name:type:rules
```

- **name** - Field name (snake_case)
- **type** - Field type (see table below)
- **rules** - Comma-separated validation rules

## Available Types

| Type | Python Type | SQL Type | Description |
|------|-------------|----------|-------------|
| `string` | `str` | VARCHAR(255) | Short text |
| `text` | `str` | TEXT | Long text |
| `integer` | `int` | INTEGER | Whole numbers |
| `float` | `float` | FLOAT | Decimal numbers |
| `boolean` | `bool` | BOOLEAN | True/False |
| `datetime` | `datetime` | DATETIME | Date and time |
| `date` | `date` | DATE | Date only |
| `time` | `time` | TIME | Time only |
| `email` | `str` | VARCHAR(255) | Email with validation |
| `url` | `str` | VARCHAR(500) | URL with validation |
| `json` | `dict` | JSON | JSON data |
| `uuid` | `UUID` | UUID/VARCHAR | UUID field |
| `decimal` | `Decimal` | DECIMAL | Precise decimal |
| `money` | `Decimal` | DECIMAL(10,2) | Currency amount |
| `phone` | `str` | VARCHAR(20) | Phone number |
| `slug` | `str` | VARCHAR(255) | URL slug |
| `ip` | `str` | VARCHAR(45) | IP address |
| `color` | `str` | VARCHAR(7) | Hex color |
| `file` | `str` | VARCHAR(500) | File path |
| `image` | `str` | VARCHAR(500) | Image path |

## Quick Examples

```bash
# Basic fields
-f name:string:required
-f email:email:required,unique
-f age:integer:required,ge:0,le:150

# Text content
-f title:string:required,max:200
-f body:text:required,min:50

# Numbers
-f price:money:required,ge:0
-f quantity:integer:required,ge:0

# Dates
-f published_at:datetime:nullable
-f birth_date:date:required

# Relationships
-f user_id:integer:required,foreign:users.id
```

See [Basic Types](/fastpy/fields/basic/), [Advanced Types](/fastpy/fields/advanced/), and [Validation Rules](/fastpy/fields/validation/) for detailed documentation.
