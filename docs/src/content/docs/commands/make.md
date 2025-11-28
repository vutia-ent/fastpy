---
title: Make Commands
description: Generate models, controllers, routes, and more
---

import { Tabs, TabItem } from '@astrojs/starlight/components';

## make:resource

Generate a complete resource with model, controller, and routes.

```bash
python cli.py make:resource <Name> [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `-f`, `--field` | Field definition (can be used multiple times) |
| `-m`, `--migration` | Generate migration file |
| `-p`, `--protected` | Add authentication to routes |
| `-i`, `--interactive` | Interactive field creation |

### Examples

```bash
# Basic resource
python cli.py make:resource Post

# With fields and migration
python cli.py make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -m

# Protected routes with migration
python cli.py make:resource Product \
  -f name:string:required \
  -f price:money:required,ge:0 \
  -m -p

# Interactive mode
python cli.py make:resource Category -i -m
```

---

## make:model

Generate a SQLModel class.

```bash
python cli.py make:model <Name> [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `-f`, `--field` | Field definition |
| `-m`, `--migration` | Generate migration file |

### Example

```bash
python cli.py make:model Product \
  -f name:string:required,max:255 \
  -f description:text:nullable \
  -f price:decimal:required,ge:0 \
  -f stock:integer:required,ge:0 \
  -f sku:string:required,unique \
  -m
```

### Generated Code

```python
from typing import Optional
from sqlmodel import Field
from app.models.base import BaseModel


class Product(BaseModel, table=True):
    __tablename__ = "products"

    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    sku: str = Field(max_length=255, unique=True)
```

---

## make:controller

Generate a controller class with CRUD operations.

```bash
python cli.py make:controller <Name>
```

### Example

```bash
python cli.py make:controller Product
```

### Generated Code

```python
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.product import Product


class ProductController:
    @staticmethod
    async def get_all(session: AsyncSession):
        result = await session.execute(
            select(Product).where(Product.deleted_at.is_(None))
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int):
        result = await session.execute(
            select(Product).where(Product.id == id, Product.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    # ... create, update, delete methods
```

---

## make:route

Generate route definitions.

```bash
python cli.py make:route <Name> [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--protected` | Add authentication requirement |

### Example

```bash
python cli.py make:route Product --protected
```

---

## make:service

Generate a service class for business logic.

```bash
python cli.py make:service <Name>
```

### Example

```bash
python cli.py make:service Order
```

---

## make:repository

Generate a repository class for data access.

```bash
python cli.py make:repository <Name>
```

---

## make:middleware

Generate custom middleware.

```bash
python cli.py make:middleware <Name>
```

### Example

```bash
python cli.py make:middleware Logging
```

---

## make:seeder

Generate a database seeder.

```bash
python cli.py make:seeder <Name>
```

---

## make:test

Generate a test file with fixtures.

```bash
python cli.py make:test <Name>
```

---

## make:factory

Generate a test factory for creating test data.

```bash
python cli.py make:factory <Name>
```

---

## make:enum

Generate an enum class.

```bash
python cli.py make:enum <Name>
```

### Example

```bash
python cli.py make:enum OrderStatus
```

---

## make:exception

Generate a custom exception class.

```bash
python cli.py make:exception <Name>
```

### Example

```bash
python cli.py make:exception PaymentFailed
```
