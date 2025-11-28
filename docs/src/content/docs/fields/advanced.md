---
title: Advanced Field Types
description: Email, URL, JSON, UUID, money, and other specialized types
---

## Contact Types

### email

Email address with automatic validation.

```bash
-f email:email:required,unique
-f contact_email:email:nullable
```

**Generated code:**
```python
from pydantic import EmailStr

email: EmailStr = Field(unique=True)
```

### phone

Phone number field.

```bash
-f phone:phone:nullable
-f mobile:phone:required
```

**Generated code:**
```python
phone: Optional[str] = Field(default=None, max_length=20)
```

### url

URL with validation.

```bash
-f website:url:nullable
-f callback_url:url:required
```

**Generated code:**
```python
from pydantic import HttpUrl

website: Optional[str] = Field(default=None, max_length=500)
```

---

## Data Types

### json

JSON/dictionary field.

```bash
-f metadata:json:nullable
-f settings:json:required
```

**Generated code:**
```python
from sqlalchemy import JSON

metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))
```

### uuid

UUID field for unique identifiers.

```bash
-f uuid:uuid:required,unique
-f external_id:uuid:nullable
```

**Generated code:**
```python
from uuid import UUID

uuid: UUID = Field(unique=True)
```

---

## Money & Numbers

### money

Currency amount with 2 decimal places.

```bash
-f price:money:required,ge:0
-f total:money:required
-f discount:money:nullable,ge:0
```

**Generated code:**
```python
from decimal import Decimal

price: Decimal = Field(ge=0, decimal_places=2)
```

### decimal

Precise decimal for calculations.

```bash
-f amount:decimal:required
-f tax_rate:decimal:required,ge:0,le:100
```

**Generated code:**
```python
amount: Decimal = Field(decimal_places=4)
```

---

## Web Types

### slug

URL-friendly slug.

```bash
-f slug:slug:required,unique
```

**Generated code:**
```python
slug: str = Field(max_length=255, unique=True, regex=r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
```

### ip

IP address (v4 or v6).

```bash
-f ip_address:ip:nullable
-f last_login_ip:ip:nullable
```

**Generated code:**
```python
ip_address: Optional[str] = Field(default=None, max_length=45)
```

### color

Hex color code.

```bash
-f theme_color:color:nullable
-f brand_color:color:required
```

**Generated code:**
```python
theme_color: Optional[str] = Field(default=None, max_length=7, regex=r'^#[0-9A-Fa-f]{6}$')
```

---

## File Types

### file

File path reference.

```bash
-f document:file:nullable
-f attachment:file:nullable
```

**Generated code:**
```python
document: Optional[str] = Field(default=None, max_length=500)
```

### image

Image path reference.

```bash
-f avatar:image:nullable
-f cover_image:image:nullable
```

**Generated code:**
```python
avatar: Optional[str] = Field(default=None, max_length=500)
```

---

## Real-World Examples

### E-commerce Product

```bash
python cli.py make:model Product \
  -f name:string:required,max:255 \
  -f slug:slug:required,unique \
  -f price:money:required,ge:0 \
  -f sku:string:required,unique \
  -f image:image:nullable \
  -f metadata:json:nullable \
  -m
```

### User Account

```bash
python cli.py make:model Account \
  -f uuid:uuid:required,unique \
  -f email:email:required,unique \
  -f phone:phone:nullable \
  -f website:url:nullable \
  -f avatar:image:nullable \
  -f last_login_ip:ip:nullable \
  -m
```
