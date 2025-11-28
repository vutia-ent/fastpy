---
title: Basic Field Types
description: String, number, boolean, and date field types
---

## String Types

### string

Short text field, maps to VARCHAR(255).

```bash
-f title:string:required,max:200
-f name:string:required,min:2,max:100
```

**Generated code:**
```python
title: str = Field(max_length=200)
```

### text

Long text field, maps to TEXT.

```bash
-f body:text:required
-f description:text:nullable,min:50
```

**Generated code:**
```python
body: str = Field(sa_column=Column(Text))
```

---

## Numeric Types

### integer

Whole numbers.

```bash
-f quantity:integer:required,ge:0
-f age:integer:required,ge:0,le:150
-f priority:integer:required,ge:1,le:10
```

**Generated code:**
```python
quantity: int = Field(ge=0)
age: int = Field(ge=0, le=150)
```

### float

Decimal numbers.

```bash
-f rating:float:required,ge:0,le:5
-f percentage:float:required,ge:0,le:100
```

**Generated code:**
```python
rating: float = Field(ge=0, le=5)
```

---

## Boolean Type

### boolean

True/False values.

```bash
-f published:boolean:required
-f is_active:boolean:required
-f email_verified:boolean:nullable
```

**Generated code:**
```python
published: bool = Field(default=False)
is_active: bool = Field(default=True)
```

---

## Date & Time Types

### datetime

Full date and time.

```bash
-f published_at:datetime:nullable
-f scheduled_for:datetime:required
```

**Generated code:**
```python
published_at: Optional[datetime] = Field(default=None)
```

### date

Date only (no time component).

```bash
-f birth_date:date:required
-f expiry_date:date:nullable
```

**Generated code:**
```python
birth_date: date
expiry_date: Optional[date] = Field(default=None)
```

### time

Time only (no date component).

```bash
-f start_time:time:required
-f end_time:time:required
```

**Generated code:**
```python
start_time: time
end_time: time
```

---

## Examples

### User Profile

```bash
python cli.py make:model Profile \
  -f user_id:integer:required,unique,foreign:users.id \
  -f bio:text:nullable,max:500 \
  -f birth_date:date:nullable \
  -f is_public:boolean:required \
  -m
```

### Product

```bash
python cli.py make:model Product \
  -f name:string:required,max:255 \
  -f description:text:nullable \
  -f price:float:required,ge:0 \
  -f stock:integer:required,ge:0 \
  -f available:boolean:required \
  -m
```
