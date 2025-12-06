# Implementation Plan: Laravel-Style Request Validation for Fastpy

## Executive Summary

This plan introduces a Laravel-inspired request validation system that transforms verbose validation patterns into clean, declarative FormRequest classes. The goal is to reduce 40+ lines of boilerplate into 5 lines of elegant code.

---

## The Vision

### Before (Current Pattern)
```python
# 40+ lines across 3 files
@router.post("/contacts", response_model=ContactRead, status_code=201)
async def create_contact(
    contact_data: ContactCreate,
    session: AsyncSession = Depends(get_session)
):
    # Manual uniqueness check
    existing = await session.execute(
        select(Contact).where(Contact.email == contact_data.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email exists")

    contact = Contact(
        name=contact_data.name,
        email=contact_data.email,
        phone=contact_data.phone,
    )
    session.add(contact)
    await session.flush()
    await session.refresh(contact)
    return contact
```

### After (Proposed Pattern)
```python
# 5 lines total
@router.post("/contacts", status_code=201)
async def create_contact(request: CreateContactRequest = validated(CreateContactRequest)):
    return await Contact.create(**request.validated_data)

# Where CreateContactRequest is:
class CreateContactRequest(FormRequest):
    rules = {
        'name': 'required|max:255',
        'email': 'required|email|unique:contacts',
        'phone': 'nullable|max:20',
    }
```

---

## Phase 1: Validation Rules Engine

### 1.1 Rule Parser

**File:** `app/validation/rules.py`

```python
from typing import List, Any, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC, abstractmethod


class Rule(ABC):
    """Base class for validation rules."""

    name: str
    params: List[str]

    def __init__(self, params: List[str] = None):
        self.params = params or []

    @abstractmethod
    async def validate(
        self,
        field: str,
        value: Any,
        data: Dict[str, Any],
        session: AsyncSession
    ) -> Optional[str]:
        """
        Validate the field value.

        Returns:
            None if valid, error message string if invalid.
        """
        pass

    def get_message(self, field: str, **kwargs) -> str:
        """Get the default error message for this rule."""
        return f"The {field} field is invalid."


class RuleParser:
    """Parse Laravel-style validation rules into Rule objects."""

    _registry: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str, rule_class: type):
        """Register a rule class."""
        cls._registry[name] = rule_class

    @classmethod
    def parse(cls, rules_string: str) -> List[Rule]:
        """
        Parse a rules string into Rule objects.

        Example:
            'required|email|max:255' -> [RequiredRule(), EmailRule(), MaxRule(['255'])]
        """
        rules = []
        for rule_def in rules_string.split('|'):
            rule_def = rule_def.strip()
            if not rule_def:
                continue

            if ':' in rule_def:
                name, params_str = rule_def.split(':', 1)
                params = params_str.split(',')
            else:
                name = rule_def
                params = []

            rule_class = cls._registry.get(name)
            if rule_class:
                rules.append(rule_class(params))
            else:
                raise ValueError(f"Unknown validation rule: {name}")

        return rules

    @classmethod
    async def validate_field(
        cls,
        field: str,
        value: Any,
        rules_string: str,
        data: Dict[str, Any],
        session: AsyncSession,
        custom_messages: Dict[str, str] = None
    ) -> List[str]:
        """Validate a single field against its rules."""
        errors = []
        rules = cls.parse(rules_string)

        # Check if field is nullable and value is None
        is_nullable = any(r.name == 'nullable' for r in rules)
        if is_nullable and value is None:
            return []

        for rule in rules:
            if rule.name == 'nullable':
                continue

            error = await rule.validate(field, value, data, session)
            if error:
                # Check for custom message
                message_key = f"{field}.{rule.name}"
                if custom_messages and message_key in custom_messages:
                    error = custom_messages[message_key]
                errors.append(error)

        return errors
```

### 1.2 Built-in Validators

**File:** `app/validation/validators.py`

**Presence Rules:**
| Rule | Description | Example |
|------|-------------|---------|
| `required` | Field must be present and not empty | `'name': 'required'` |
| `nullable` | Field can be null/None | `'phone': 'nullable'` |
| `present` | Field must be present (can be empty) | `'bio': 'present'` |
| `filled` | If present, cannot be empty | `'nickname': 'filled'` |

**Type Rules:**
| Rule | Description | Example |
|------|-------------|---------|
| `string` | Must be a string | `'name': 'string'` |
| `integer` | Must be an integer | `'age': 'integer'` |
| `numeric` | Must be numeric | `'price': 'numeric'` |
| `boolean` | Must be boolean | `'active': 'boolean'` |
| `array` | Must be a list | `'tags': 'array'` |

**Size Rules:**
| Rule | Description | Example |
|------|-------------|---------|
| `max:N` | Maximum length/value | `'name': 'max:255'` |
| `min:N` | Minimum length/value | `'password': 'min:8'` |
| `size:N` | Exact length/value | `'code': 'size:6'` |
| `between:min,max` | Between min and max | `'age': 'between:18,100'` |

**Format Rules:**
| Rule | Description | Example |
|------|-------------|---------|
| `email` | Valid email format | `'email': 'email'` |
| `url` | Valid URL format | `'website': 'url'` |
| `uuid` | Valid UUID format | `'id': 'uuid'` |
| `regex:pattern` | Match regex | `'code': 'regex:^[A-Z]{3}$'` |
| `alpha` | Only letters | `'name': 'alpha'` |
| `alpha_num` | Letters and numbers | `'username': 'alpha_num'` |
| `alpha_dash` | Letters, numbers, dashes | `'slug': 'alpha_dash'` |

**Database Rules (Async):**
| Rule | Description | Example |
|------|-------------|---------|
| `unique:table,column,{ignore}` | Must be unique | `'email': 'unique:users,email,{id}'` |
| `exists:table,column` | Must exist | `'user_id': 'exists:users,id'` |

**Comparison Rules:**
| Rule | Description | Example |
|------|-------------|---------|
| `same:field` | Must match field | `'password_confirm': 'same:password'` |
| `different:field` | Must differ from field | `'new_email': 'different:email'` |
| `confirmed` | Must have `{field}_confirmation` | `'password': 'confirmed'` |
| `gt:field` | Greater than field | `'max': 'gt:min'` |
| `gte:field` | Greater than or equal | `'end': 'gte:start'` |
| `lt:field` | Less than field | `'min': 'lt:max'` |
| `lte:field` | Less than or equal | `'start': 'lte:end'` |

**Inclusion Rules:**
| Rule | Description | Example |
|------|-------------|---------|
| `in:a,b,c` | Must be in list | `'status': 'in:active,pending,closed'` |
| `not_in:a,b,c` | Must not be in list | `'role': 'not_in:admin,super'` |

**Conditional Rules:**
| Rule | Description | Example |
|------|-------------|---------|
| `required_if:field,value` | Required if field equals value | `'reason': 'required_if:status,rejected'` |
| `required_unless:field,value` | Required unless field equals value | `'phone': 'required_unless:contact,email'` |
| `required_with:fields` | Required if any field present | `'city': 'required_with:address'` |
| `required_without:fields` | Required if any field absent | `'email': 'required_without:phone'` |

**Password Rules:**
| Rule | Description | Example |
|------|-------------|---------|
| `password` | Meets password requirements | `'password': 'password'` |

---

## Phase 2: FormRequest Base Class

**File:** `app/validation/form_request.py`

```python
from typing import Dict, List, Any, Optional, ClassVar
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.validation.rules import RuleParser


class FormRequest(PydanticBaseModel):
    """
    Laravel-style form request with validation rules.

    Usage:
        class CreateContactRequest(FormRequest):
            rules: ClassVar[Dict[str, str]] = {
                'name': 'required|max:255',
                'email': 'required|email|unique:contacts',
            }

            messages: ClassVar[Dict[str, str]] = {
                'email.unique': 'This email is already registered.',
            }
    """

    # Class-level configuration (override in subclasses)
    rules: ClassVar[Dict[str, str]] = {}
    messages: ClassVar[Dict[str, str]] = {}
    attributes: ClassVar[Dict[str, str]] = {}

    # Instance state
    _validated_data: Dict[str, Any] = {}
    _errors: Dict[str, List[str]] = {}
    _session: Optional[AsyncSession] = None
    _user: Optional[Any] = None
    _raw_data: Dict[str, Any] = {}

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

    def authorize(self, user: Optional[Any] = None) -> bool:
        """
        Override to add authorization logic.
        Return False to reject with 403 Forbidden.
        """
        return True

    async def validate(self) -> bool:
        """Run all validation rules."""
        self._errors = {}
        self._validated_data = {}

        # Prepare data
        data = self.prepare_for_validation(self._raw_data.copy())

        # Get rules (support both dict and method)
        rules = self.get_rules() if callable(getattr(self, 'get_rules', None)) else self.rules

        for field, rules_string in rules.items():
            value = data.get(field)
            field_errors = await RuleParser.validate_field(
                field=field,
                value=value,
                rules_string=rules_string,
                data=data,
                session=self._session,
                custom_messages=self.messages
            )

            if field_errors:
                self._errors[field] = field_errors
            else:
                self._validated_data[field] = value

        if self._errors:
            self.failed_validation()
        else:
            self.passed_validation()

        return not self._errors

    @property
    def validated_data(self) -> Dict[str, Any]:
        """Return only validated fields."""
        return self._validated_data

    @property
    def errors(self) -> Dict[str, List[str]]:
        """Return validation errors by field."""
        return self._errors

    def fails(self) -> bool:
        """Return True if validation failed."""
        return bool(self._errors)

    def passed(self) -> bool:
        """Return True if validation passed."""
        return not self._errors

    # Hooks for customization
    def prepare_for_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data before validation (e.g., trim strings)."""
        return data

    def passed_validation(self) -> None:
        """Called after successful validation."""
        pass

    def failed_validation(self) -> None:
        """Called after failed validation."""
        pass
```

---

## Phase 3: FastAPI Integration

**File:** `app/validation/dependency.py`

```python
from typing import Type, TypeVar
from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.validation.form_request import FormRequest
from app.utils.exceptions import ValidationException, ForbiddenException

T = TypeVar('T', bound=FormRequest)


def validated(form_request_class: Type[T]):
    """
    FastAPI dependency for form request validation.

    Usage:
        @router.post("/contacts")
        async def store(request: CreateContactRequest = validated(CreateContactRequest)):
            return await Contact.create(**request.validated_data)
    """
    async def dependency(
        request: Request,
        session: AsyncSession = Depends(get_session),
    ) -> T:
        # Parse request body
        try:
            content_type = request.headers.get("content-type", "")
            if content_type.startswith("application/json"):
                body = await request.json()
            else:
                body = dict(await request.form())
        except Exception:
            body = {}

        # Include path and query parameters
        body.update(request.path_params)
        for key, value in request.query_params.items():
            if key not in body:
                body[key] = value

        # Get current user (optional)
        user = getattr(request.state, 'user', None)

        # Create form request instance
        form_request = form_request_class(**body)
        form_request._raw_data = body
        form_request._session = session
        form_request._user = user

        # Authorization check
        if not form_request.authorize(user):
            raise ForbiddenException("This action is unauthorized.")

        # Validate
        await form_request.validate()

        if form_request.fails():
            raise ValidationException(
                message="The given data was invalid.",
                errors=form_request.errors
            )

        return form_request

    return Depends(dependency)
```

### Validation Error Response Format

```json
{
    "success": false,
    "message": "The given data was invalid.",
    "error_code": "VALIDATION_ERROR",
    "errors": {
        "email": [
            "The email field is required.",
            "The email must be a valid email address."
        ],
        "name": [
            "The name field must not be greater than 255 characters."
        ]
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "abc123"
}
```

---

## Phase 4: Active Record Model Enhancements

**File:** `app/models/base.py` (extend existing)

```python
from contextvars import ContextVar
from typing import TypeVar, Type, Optional, List, Any, Dict

T = TypeVar('T', bound='BaseModel')

# Context variable for current session
_current_session: ContextVar[Optional[AsyncSession]] = ContextVar('session', default=None)


class BaseModel(SQLModel):
    """Enhanced base model with Active Record methods."""

    # ... existing code ...

    @classmethod
    async def create(cls: Type[T], session: AsyncSession = None, **data) -> T:
        """Create and save a new instance."""
        session = session or _current_session.get()
        if not session:
            raise RuntimeError("No database session available")

        instance = cls(**data)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance

    @classmethod
    async def find(cls: Type[T], id: int, session: AsyncSession = None) -> Optional[T]:
        """Find by ID (excludes soft deleted)."""
        session = session or _current_session.get()
        query = select(cls).where(cls.id == id)
        if hasattr(cls, 'deleted_at'):
            query = query.where(cls.deleted_at.is_(None))
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_or_fail(cls: Type[T], id: int, session: AsyncSession = None) -> T:
        """Find by ID or raise NotFoundException."""
        instance = await cls.find(id, session)
        if not instance:
            raise NotFoundException(resource=cls.__name__)
        return instance

    @classmethod
    async def where(cls: Type[T], session: AsyncSession = None, **filters) -> List[T]:
        """Find records matching filters."""
        session = session or _current_session.get()
        query = select(cls)
        if hasattr(cls, 'deleted_at'):
            query = query.where(cls.deleted_at.is_(None))
        for field, value in filters.items():
            if hasattr(cls, field):
                query = query.where(getattr(cls, field) == value)
        result = await session.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def first_where(cls: Type[T], session: AsyncSession = None, **filters) -> Optional[T]:
        """Find first matching record."""
        results = await cls.where(session, **filters)
        return results[0] if results else None

    async def save(self: T, session: AsyncSession = None) -> T:
        """Save changes to database."""
        session = session or _current_session.get()
        self.touch()
        session.add(self)
        await session.flush()
        await session.refresh(self)
        return self

    async def update(self: T, session: AsyncSession = None, **data) -> T:
        """Update with new data and save."""
        for field, value in data.items():
            if hasattr(self, field):
                setattr(self, field, value)
        return await self.save(session)

    async def delete(self: T, session: AsyncSession = None, force: bool = False) -> bool:
        """Soft delete (or force delete)."""
        session = session or _current_session.get()
        if force or not hasattr(self, 'deleted_at'):
            await session.delete(self)
        else:
            self.soft_delete()
            session.add(self)
        await session.flush()
        return True
```

### Session Context Middleware

**File:** `app/middleware/session_context.py`

```python
from starlette.middleware.base import BaseHTTPMiddleware
from app.database.connection import async_session_maker
from app.models.base import _current_session


class SessionContextMiddleware(BaseHTTPMiddleware):
    """Set database session in context for Active Record pattern."""

    async def dispatch(self, request, call_next):
        async with async_session_maker() as session:
            token = _current_session.set(session)
            try:
                response = await call_next(request)
                await session.commit()
                return response
            except Exception:
                await session.rollback()
                raise
            finally:
                _current_session.reset(token)
```

---

## Phase 5: CLI Generator

**Command:** `fastpy make:request`

```bash
# Basic usage
fastpy make:request CreateContact

# With fields
fastpy make:request CreateContact \
    -f name:string:required,max:255 \
    -f email:email:required,unique:contacts \
    -f phone:string:nullable

# For updates (makes fields optional)
fastpy make:request UpdateContact --update

# Generate from model
fastpy make:request CreateUser --model User
```

**Generated file:** `app/requests/create_contact_request.py`

```python
"""CreateContactRequest form request."""
from typing import ClassVar, Dict

from app.validation.form_request import FormRequest


class CreateContactRequest(FormRequest):
    """Form request for contact creation."""

    rules: ClassVar[Dict[str, str]] = {
        "name": "required|max:255",
        "email": "required|email|unique:contacts",
        "phone": "nullable|max:20",
    }

    messages: ClassVar[Dict[str, str]] = {
        # "field.rule": "Custom error message",
    }

    def authorize(self, user=None) -> bool:
        """Determine if user is authorized to make this request."""
        return True
```

---

## Phase 6: Directory Structure

```
app/
├── validation/                    # NEW
│   ├── __init__.py
│   ├── rules.py                   # Rule parser & base Rule class
│   ├── validators.py              # All built-in validators
│   ├── form_request.py            # FormRequest base class
│   ├── dependency.py              # validated() dependency
│   └── exceptions.py              # ValidationException
├── requests/                      # NEW
│   ├── __init__.py
│   ├── auth/
│   │   ├── login_request.py
│   │   └── register_request.py
│   └── user/
│       ├── create_user_request.py
│       └── update_user_request.py
├── middleware/
│   └── session_context.py         # NEW
└── models/
    └── base.py                    # MODIFIED
```

---

## Phase 7: Implementation Sequence

### Step 1: Core Validation (Priority: Critical)
- [ ] Create `app/validation/` directory
- [ ] Implement `Rule` base class and `RuleParser`
- [ ] Implement basic validators: `required`, `nullable`, `max`, `min`, `string`, `integer`

### Step 2: Format Validators (Priority: High)
- [ ] Implement `email`, `url`, `uuid`, `regex`, `alpha`, `alpha_num`
- [ ] Implement `in`, `not_in` validators
- [ ] Implement `same`, `different`, `confirmed`

### Step 3: Database Validators (Priority: High)
- [ ] Implement `unique` validator with ignore_id support
- [ ] Implement `exists` validator
- [ ] Add model registry for table name lookup

### Step 4: FormRequest & Dependency (Priority: Critical)
- [ ] Implement `FormRequest` base class
- [ ] Create `validated()` dependency
- [ ] Update `ValidationException` in exceptions.py

### Step 5: Active Record (Priority: Medium)
- [ ] Add Active Record methods to `BaseModel`
- [ ] Create `SessionContextMiddleware`
- [ ] Update `main.py` integration

### Step 6: CLI & Testing (Priority: Medium)
- [ ] Add `make:request` command
- [ ] Write unit tests for validators
- [ ] Write integration tests for FormRequest
- [ ] Update documentation

---

## Phase 8: Usage Examples

### Creating a Contact

```python
# app/requests/contact/create_contact_request.py
class CreateContactRequest(FormRequest):
    rules = {
        'name': 'required|max:255',
        'email': 'required|email|unique:contacts',
        'phone': 'nullable|max:20',
        'company': 'nullable|max:255',
    }

    messages = {
        'email.unique': 'A contact with this email already exists.',
    }

# app/routes/contact_routes.py
@router.post("/", status_code=201)
async def store(request: CreateContactRequest = validated(CreateContactRequest)):
    contact = await Contact.create(**request.validated_data)
    return contact
```

### Updating a User (with authorization)

```python
# app/requests/user/update_user_request.py
class UpdateUserRequest(FormRequest):
    rules = {
        'name': 'max:255',
        'email': 'email|unique:users,email,{id}',  # Ignore current user's email
        'password': 'min:8|confirmed',
    }

    def authorize(self, user) -> bool:
        # Only allow users to update their own profile
        return user and user.id == self._raw_data.get('id')

# app/routes/user_routes.py
@router.put("/{id}")
async def update(id: int, request: UpdateUserRequest = validated(UpdateUserRequest)):
    user = await User.find_or_fail(id)
    await user.update(**request.validated_data)
    return user
```

### Conditional Validation

```python
class CreateOrderRequest(FormRequest):
    rules = {
        'product_id': 'required|exists:products,id',
        'quantity': 'required|integer|min:1',
        'shipping_method': 'required|in:standard,express,overnight',
        'shipping_address': 'required_if:shipping_method,standard,express',
        'express_instructions': 'required_if:shipping_method,express|max:500',
    }
```

---

## Phase 9: Backwards Compatibility

The implementation maintains **full backwards compatibility**:

1. **Existing Pydantic schemas** continue to work unchanged
2. **Existing controllers** require no modifications
3. **Existing routes** function as before
4. New FormRequest pattern can be adopted **incrementally**

### Migration Example

```python
# Old route (still works)
@router.post("/users")
async def create_old(data: UserCreate, session: AsyncSession = Depends(get_session)):
    return await UserController.create(session, data)

# New route (coexists)
@router.post("/contacts")
async def create_new(request: CreateContactRequest = validated(CreateContactRequest)):
    return await Contact.create(**request.validated_data)
```

---

## Success Metrics

| Metric | Before | After |
|--------|--------|-------|
| Lines per CRUD endpoint | 40+ | 5-10 |
| Validation duplication | High | None |
| Custom error messages | Hard | Easy |
| Database validation (unique) | Manual | Declarative |
| Type safety | Partial | Full |
| IDE autocomplete | Limited | Complete |

---

## Appendix: Validator Implementation Examples

### Required Validator

```python
class RequiredRule(Rule):
    name = "required"

    async def validate(self, field, value, data, session):
        if value is None or value == "" or (isinstance(value, (list, dict)) and len(value) == 0):
            return f"The {field} field is required."
        return None
```

### Unique Validator

```python
class UniqueRule(Rule):
    name = "unique"

    async def validate(self, field, value, data, session):
        if not value:
            return None

        table = self.params[0]
        column = self.params[1] if len(self.params) > 1 else field

        # Handle {id} placeholder for updates
        ignore_id = None
        if len(self.params) > 2:
            id_param = self.params[2]
            if id_param.startswith('{') and id_param.endswith('}'):
                ignore_id = data.get(id_param[1:-1])

        model = get_model_by_table_name(table)
        query = select(model).where(getattr(model, column) == value)

        if ignore_id:
            query = query.where(model.id != ignore_id)

        if hasattr(model, 'deleted_at'):
            query = query.where(model.deleted_at.is_(None))

        result = await session.execute(query)
        if result.scalar_one_or_none():
            return f"The {field} has already been taken."

        return None
```

### Email Validator

```python
class EmailRule(Rule):
    name = "email"

    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    async def validate(self, field, value, data, session):
        if value and not self.EMAIL_REGEX.match(str(value)):
            return f"The {field} must be a valid email address."
        return None
```
