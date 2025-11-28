# Advanced Field Types

Specialized field types with built-in validation and formatting.

## email

Email address with validation.

```bash
-f email:email:required,unique
```

### Generated Code

```python
from pydantic import EmailStr

email: EmailStr = Field(unique=True, index=True)
```

### Validation

Automatically validates:
- Contains `@` symbol
- Valid domain format
- No invalid characters

## url

URL with validation.

```bash
-f website:url:nullable
-f callback_url:url:required
```

### Generated Code

```python
from pydantic import HttpUrl

website: Optional[HttpUrl] = None
```

## uuid

UUID for identifiers.

```bash
-f public_id:uuid:unique
```

### Generated Code

```python
from uuid import UUID, uuid4

public_id: UUID = Field(default_factory=uuid4, unique=True)
```

### Use Cases

- Public-facing IDs (hide auto-increment)
- Distributed systems
- API identifiers

## decimal

Precise decimal numbers.

```bash
-f price:decimal:required
-f tax_rate:decimal:nullable
```

### Generated Code

```python
from decimal import Decimal
from sqlalchemy import Column, Numeric

price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
```

### With Precision

```bash
-f amount:decimal:required  # Default: 10,2
```

## money

Currency amounts (alias for decimal with 2 places).

```bash
-f price:money:required,min:0
-f discount:money:nullable
```

### Generated Code

```python
from decimal import Decimal

price: Decimal = Field(ge=Decimal('0'), decimal_places=2)
```

## percent

Percentage values (0-100).

```bash
-f discount_percent:percent:default:0
-f tax_rate:percent:required
```

### Generated Code

```python
from decimal import Decimal

discount_percent: Decimal = Field(default=Decimal('0'), ge=0, le=100)
```

## date

Date without time.

```bash
-f birth_date:date:nullable
-f due_date:date:required
```

### Generated Code

```python
from datetime import date

birth_date: Optional[date] = None
due_date: date
```

## time

Time without date.

```bash
-f start_time:time:required
-f end_time:time:required
```

### Generated Code

```python
from datetime import time

start_time: time
end_time: time
```

## phone

Phone number with validation.

```bash
-f phone:phone:nullable
-f mobile:phone:required
```

### Generated Code

```python
phone: Optional[str] = Field(max_length=20, regex=r'^\+?[1-9]\d{1,14}$')
```

## slug

URL-friendly slug.

```bash
-f slug:slug:required,unique,index
```

### Generated Code

```python
slug: str = Field(unique=True, index=True, regex=r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
```

### Auto-Generation

Consider auto-generating from title:

```python
from slugify import slugify

class PostService(BaseService):
    async def before_create(self, data: dict) -> dict:
        if 'slug' not in data and 'title' in data:
            data['slug'] = slugify(data['title'])
        return data
```

## ip

IP address (v4 or v6).

```bash
-f ip_address:ip:nullable
-f last_login_ip:ip:nullable
```

### Generated Code

```python
from ipaddress import IPv4Address, IPv6Address
from typing import Union

ip_address: Optional[Union[IPv4Address, IPv6Address]] = None
```

## json

JSON/JSONB data.

```bash
-f metadata:json:nullable
-f settings:json:default:{}
```

### Generated Code

```python
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

metadata: Optional[dict] = Field(sa_column=Column(JSONB))
```

### Use Cases

```bash
-f preferences:json:nullable     # User preferences
-f attributes:json:nullable      # Product attributes
-f translations:json:nullable    # i18n content
```

## color

Hex color code.

```bash
-f primary_color:color:default:#000000
-f background_color:color:nullable
```

### Generated Code

```python
primary_color: str = Field(default='#000000', regex=r'^#[0-9A-Fa-f]{6}$')
```

## file

File path/URL.

```bash
-f document:file:nullable
-f attachment:file:nullable
```

### Generated Code

```python
document: Optional[str] = Field(max_length=500)
```

## image

Image path/URL (alias for file with image validation).

```bash
-f avatar:image:nullable
-f cover_image:image:nullable
```

### Generated Code

```python
avatar: Optional[str] = Field(max_length=500)
```

## Foreign Keys

Reference other tables.

```bash
-f user_id:integer:foreign:users.id
-f category_id:integer:foreign:categories.id,nullable
```

### Generated Code

```python
from sqlalchemy import ForeignKey

user_id: int = Field(foreign_key="users.id")
category_id: Optional[int] = Field(foreign_key="categories.id", nullable=True)
```

### With Relationships

```python
from sqlmodel import Relationship

class Post(BaseModel, table=True):
    user_id: int = Field(foreign_key="users.id")
    user: Optional["User"] = Relationship(back_populates="posts")
```
