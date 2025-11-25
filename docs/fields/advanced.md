# Advanced Field Types

Specialized field types for complex data requirements.

## uuid

UUID (Universally Unique Identifier) field.

### Usage

```bash
-f uuid:uuid:required,unique
-f external_id:uuid:nullable
```

### Generated Code

```python
from uuid import UUID

# Model
uuid: UUID = Field(nullable=False, unique=True)

# Create Schema
uuid: UUID

# Update Schema
uuid: Optional[UUID] = None
```

### Real Examples

```bash
# Primary identifier
-f uuid:uuid:required,unique

# External reference
-f external_id:uuid:nullable

# API key reference
-f api_key_id:uuid:required
```

---

## decimal

Precise decimal field for financial calculations.

### Usage

```bash
-f amount:decimal:required
-f rate:decimal:required,ge:0,le:1
```

### Generated Code

```python
from decimal import Decimal

# Model
amount: Decimal = Field(nullable=False, decimal_places=2)

# Create Schema
amount: Decimal = Field(ge=0)

# Update Schema
amount: Optional[Decimal] = Field(default=None, ge=0)
```

### Real Examples

```bash
# Financial amount
-f amount:decimal:required,ge:0

# Interest rate
-f rate:decimal:required,ge:0,le:1

# Tax rate
-f tax_rate:decimal:required,ge:0
```

---

## money

Currency amount field (uses Decimal with 2 decimal places).

### Usage

```bash
-f price:money:required
-f total:money:required,ge:0
-f discount:money:nullable
```

### Generated Code

```python
from decimal import Decimal

# Model
price: Decimal = Field(nullable=False, decimal_places=2)

# Create Schema
price: Decimal = Field(ge=0, decimal_places=2)

# Update Schema
price: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
```

### Real Examples

```bash
# Product price
-f price:money:required,ge:0

# Order total
-f total:money:required,ge:0
-f subtotal:money:required,ge:0
-f tax:money:required,ge:0

# Discount amount
-f discount:money:nullable,ge:0

# Shipping cost
-f shipping:money:nullable,ge:0
```

---

## percent

Percentage field (0-100 or 0-1 decimal).

### Usage

```bash
-f discount:percent:required
-f completion:percent:required,ge:0,le:100
```

### Generated Code

```python
from decimal import Decimal

# Model
discount: Decimal = Field(nullable=False, ge=0, le=100)

# Create Schema
discount: Decimal = Field(ge=0, le=100)

# Update Schema
discount: Optional[Decimal] = Field(default=None, ge=0, le=100)
```

### Real Examples

```bash
# Discount percentage
-f discount_percent:percent:required,ge:0,le:100

# Progress completion
-f progress:percent:required,ge:0,le:100

# Tax percentage
-f tax_percent:percent:required,ge:0

# Commission rate
-f commission:percent:required,ge:0,le:50
```

---

## date

Date-only field (no time component).

### Usage

```bash
-f birth_date:date:required
-f due_date:date:nullable
```

### Generated Code

```python
from datetime import date

# Model
birth_date: date = Field(nullable=False)

# Create Schema
birth_date: date

# Update Schema
birth_date: Optional[date] = None
```

### Real Examples

```bash
# Birth date
-f birth_date:date:required

# Due date
-f due_date:date:nullable

# Event date
-f event_date:date:required

# Expiration date
-f expiry_date:date:nullable
```

---

## time

Time-only field (no date component).

### Usage

```bash
-f start_time:time:required
-f opening_time:time:nullable
```

### Generated Code

```python
from datetime import time

# Model
start_time: time = Field(nullable=False)

# Create Schema
start_time: time

# Update Schema
start_time: Optional[time] = None
```

### Real Examples

```bash
# Business hours
-f opens_at:time:required
-f closes_at:time:required

# Event time
-f start_time:time:required
-f end_time:time:required

# Reminder time
-f reminder_time:time:nullable
```

---

## email

Email address with validation.

### Usage

```bash
-f email:email:required,unique
-f contact_email:email:nullable
```

### Generated Code

```python
from pydantic import EmailStr

# Model
email: str = Field(nullable=False, unique=True)

# Create Schema
email: EmailStr

# Update Schema
email: Optional[EmailStr] = None
```

### Real Examples

```bash
# User email
-f email:email:required,unique

# Contact email
-f contact_email:email:nullable

# Billing email
-f billing_email:email:nullable

# Support email
-f support_email:email:nullable
```

---

## url

URL string field.

### Usage

```bash
-f website:url:nullable
-f callback_url:url:required
```

### Generated Code

```python
# Model
website: Optional[str] = Field(default=None, nullable=True)

# Create Schema
website: Optional[str] = None  # Validated as URL

# Update Schema
website: Optional[str] = None
```

### Real Examples

```bash
# Website
-f website:url:nullable

# Social links
-f twitter_url:url:nullable
-f linkedin_url:url:nullable

# Callback URLs
-f webhook_url:url:required

# Image URLs
-f image_url:url:nullable
```

---

## slug

URL-friendly slug field.

### Usage

```bash
-f slug:slug:required,unique
```

### Generated Code

```python
# Model
slug: str = Field(nullable=False, unique=True, max_length=255)

# Create Schema
slug: str = Field(max_length=255, pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

# Update Schema
slug: Optional[str] = Field(default=None, max_length=255)
```

### Real Examples

```bash
# Post slug
-f slug:slug:required,unique

# Category slug
-f slug:slug:required,unique

# Product slug
-f slug:slug:required,unique,max:100
```

---

## phone

Phone number field.

### Usage

```bash
-f phone:phone:required
-f mobile:phone:nullable
```

### Generated Code

```python
# Model
phone: str = Field(nullable=False, max_length=20)

# Create Schema
phone: str = Field(max_length=20)

# Update Schema
phone: Optional[str] = Field(default=None, max_length=20)
```

### Real Examples

```bash
# Primary phone
-f phone:phone:required

# Mobile number
-f mobile:phone:nullable

# Emergency contact
-f emergency_phone:phone:nullable

# Fax number
-f fax:phone:nullable
```

---

## ip

IP address field (IPv4 or IPv6).

### Usage

```bash
-f ip_address:ip:required
-f last_ip:ip:nullable
```

### Generated Code

```python
# Model
ip_address: str = Field(nullable=False, max_length=45)

# Create Schema
ip_address: str = Field(max_length=45)

# Update Schema
ip_address: Optional[str] = Field(default=None, max_length=45)
```

### Real Examples

```bash
# Client IP
-f client_ip:ip:required

# Last login IP
-f last_login_ip:ip:nullable

# Server IP
-f server_ip:ip:required
```

---

## color

Hex color code field.

### Usage

```bash
-f color:color:required
-f theme_color:color:nullable
```

### Generated Code

```python
# Model
color: str = Field(nullable=False, max_length=7)

# Create Schema
color: str = Field(max_length=7, pattern=r'^#[0-9A-Fa-f]{6}$')

# Update Schema
color: Optional[str] = Field(default=None, max_length=7)
```

### Real Examples

```bash
# Brand color
-f primary_color:color:required
-f secondary_color:color:nullable

# Category color
-f color:color:required

# Theme colors
-f background_color:color:nullable
-f text_color:color:nullable
```

---

## file

File path field.

### Usage

```bash
-f document:file:nullable
-f attachment:file:required
```

### Generated Code

```python
# Model
document: Optional[str] = Field(default=None, nullable=True)

# Create Schema
document: Optional[str] = None

# Update Schema
document: Optional[str] = None
```

### Real Examples

```bash
# Document attachment
-f document:file:nullable

# Resume file
-f resume:file:required

# Contract file
-f contract:file:nullable
```

---

## image

Image path field.

### Usage

```bash
-f avatar:image:nullable
-f cover_image:image:required
```

### Generated Code

```python
# Model
avatar: Optional[str] = Field(default=None, nullable=True)

# Create Schema
avatar: Optional[str] = None

# Update Schema
avatar: Optional[str] = None
```

### Real Examples

```bash
# User avatar
-f avatar:image:nullable

# Product image
-f image:image:required
-f thumbnail:image:nullable

# Cover images
-f cover:image:nullable
-f banner:image:nullable
```

---

## json

JSON data field for flexible structured data.

### Usage

```bash
-f metadata:json:nullable
-f settings:json:required
```

### Generated Code

```python
from typing import Dict, Any

# Model
metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

# Create Schema
metadata: Optional[Dict[str, Any]] = None

# Update Schema
metadata: Optional[Dict[str, Any]] = None
```

### Real Examples

```bash
# Metadata
-f metadata:json:nullable

# User settings
-f settings:json:nullable

# Configuration
-f config:json:required

# Extra attributes
-f attributes:json:nullable
```

---

## Type Comparison

| Type | Python | DB Column | Precision |
|------|--------|-----------|-----------|
| `decimal` | `Decimal` | DECIMAL | High |
| `money` | `Decimal` | DECIMAL(10,2) | 2 places |
| `percent` | `Decimal` | DECIMAL | 0-100 |
| `float` | `float` | FLOAT | Low |

## Next Steps

- [Basic Types](basic.md) - String, integer, float, boolean
- [Validation Rules](validation.md) - All validation options
- [Examples](../examples/blog.md) - Real-world examples
