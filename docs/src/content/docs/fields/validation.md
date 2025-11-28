---
title: Validation Rules
description: All available validation rules for field definitions
---

Validation rules are added after the field type, separated by commas.

## Syntax

```
name:type:rule1,rule2,rule3
```

## Nullability Rules

### required

Field cannot be null.

```bash
-f title:string:required
-f email:email:required
```

### nullable

Field can be null.

```bash
-f bio:text:nullable
-f phone:phone:nullable
```

---

## Uniqueness & Indexing

### unique

Field must have unique values.

```bash
-f email:email:required,unique
-f slug:slug:required,unique
-f sku:string:required,unique
```

### index

Create database index for faster queries.

```bash
-f status:string:index
-f created_at:datetime:index
```

---

## Length Constraints

### max:N

Maximum length (strings) or value (numbers).

```bash
-f title:string:required,max:200
-f name:string:required,max:100
-f rating:integer:required,max:5
```

### min:N

Minimum length (strings) or value (numbers).

```bash
-f body:text:required,min:50
-f password:string:required,min:8
-f age:integer:required,min:0
```

---

## Numeric Constraints

### ge:N / gte:N

Greater than or equal to.

```bash
-f price:money:required,ge:0
-f quantity:integer:required,ge:1
-f rating:float:required,ge:0
```

### le:N / lte:N

Less than or equal to.

```bash
-f rating:integer:required,le:5
-f discount:float:required,le:100
-f priority:integer:required,le:10
```

### gt:N

Greater than (not equal).

```bash
-f age:integer:required,gt:0
-f price:money:required,gt:0
```

### lt:N

Less than (not equal).

```bash
-f discount:float:required,lt:100
```

---

## Relationships

### foreign:table.column

Define a foreign key relationship.

```bash
-f user_id:integer:required,foreign:users.id
-f category_id:integer:nullable,foreign:categories.id
-f author_id:integer:required,foreign:users.id
```

**Generated code:**
```python
user_id: int = Field(foreign_key="users.id")
```

---

## Combining Rules

Rules can be combined freely:

```bash
# Required, unique email
-f email:email:required,unique

# Required string with length limits
-f title:string:required,min:5,max:200

# Required positive number
-f price:money:required,ge:0

# Nullable with index
-f status:string:nullable,index

# Foreign key, required
-f user_id:integer:required,foreign:users.id

# Complex validation
-f rating:float:required,ge:0,le:5
-f percentage:integer:required,ge:0,le:100
```

---

## Examples by Use Case

### Blog Post

```bash
python cli.py make:model Post \
  -f title:string:required,min:5,max:200 \
  -f slug:slug:required,unique \
  -f body:text:required,min:100 \
  -f excerpt:text:nullable,max:300 \
  -f published:boolean:required \
  -f author_id:integer:required,foreign:users.id \
  -m
```

### Product with Inventory

```bash
python cli.py make:model Product \
  -f name:string:required,max:255 \
  -f sku:string:required,unique \
  -f price:money:required,ge:0 \
  -f cost:money:nullable,ge:0 \
  -f stock:integer:required,ge:0 \
  -f min_stock:integer:required,ge:0 \
  -f category_id:integer:nullable,foreign:categories.id \
  -m
```

### User Registration

```bash
python cli.py make:model User \
  -f name:string:required,min:2,max:100 \
  -f email:email:required,unique \
  -f password:string:required,min:8,max:72 \
  -f phone:phone:nullable \
  -f is_active:boolean:required \
  -m
```
