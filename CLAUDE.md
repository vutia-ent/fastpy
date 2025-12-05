# Project Overview

Production-ready FastAPI starter with SQLModel, PostgreSQL/MySQL support, JWT authentication, MVC architecture, and FastCLI code generator.

## Technology Stack

- **Framework**: FastAPI (async/await)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL OR MySQL
- **Authentication**: JWT with bcrypt, refresh tokens
- **Migrations**: Alembic
- **CLI**: FastCLI (code generator)
- **Testing**: pytest + pytest-asyncio + factory-boy

## Development Commands

```bash
# Activate virtual environment (required before running commands)
source venv/bin/activate

# Start development server
fastpy serve
# Or: uvicorn main:app --reload

# List all routes
fastpy route:list
```

## Code Generation (FastCLI)

Generated code uses **Active Record pattern**, **Route Model Binding**, and **Model Concerns** by default.

```bash
# Generate complete resource (model + controller + routes)
# Includes: Active Record, Route Model Binding, Model Concerns (HasScopes, GuardsAttributes)
fastpy make:resource Post -f title:string:required,max:200 -f body:text:required -m -p

# Individual generators
fastpy make:model Post -f title:string:required -m      # Model + Concerns + migration
fastpy make:controller Post                              # Controller (Active Record)
fastpy make:route Post --protected                       # Routes (with binding + auth)
fastpy make:service Post                                 # Service class
fastpy make:repository Post                              # Repository class
fastpy make:middleware Logging                           # Middleware
fastpy make:test Post                                    # Test file
fastpy make:factory Post                                 # Test factory
fastpy make:seeder Post                                  # Database seeder
fastpy make:enum Status -v active -v inactive            # Enum
fastpy make:exception PaymentFailed -s 400               # Custom exception

# Disable defaults (legacy mode)
fastpy make:model Post --no-concerns                     # Without Model Concerns
fastpy make:route Post --no-binding                      # Without Route Model Binding

# List all commands
fastpy list
```

## Global CLI Commands

```bash
# Project creation
fastpy new my-project                    # Create new Fastpy project
fastpy new my-project --branch dev       # From specific branch

# AI-powered code generation
fastpy ai "Create a blog with posts"     # Natural language generation
fastpy ai "Add comments to posts" -e     # Execute commands automatically

# Configuration & diagnostics
fastpy config                            # Show current config
fastpy config --init                     # Create config file
fastpy init                              # Initialize Fastpy config
fastpy doctor                            # Diagnose environment issues

# Utilities
fastpy version                           # Show CLI version
fastpy upgrade                           # Update CLI to latest
fastpy docs                              # Open documentation
fastpy libs                              # List available facades
fastpy libs http --usage                 # Show facade usage examples
```

## Setup Commands

Setup commands for initializing a new Fastpy project.

```bash
# Full interactive setup (after venv is created)
fastpy setup                             # Complete setup wizard

# Individual setup steps
fastpy setup:env                         # Initialize .env from .env.example
fastpy setup:db                          # Configure database connection
fastpy setup:db -d mysql                 # Specify database driver
fastpy setup:db -d postgresql            # PostgreSQL
fastpy setup:db -d sqlite                # SQLite (development only)
fastpy setup:secret                      # Generate secure JWT secret key
fastpy setup:hooks                       # Install pre-commit hooks

# Admin user creation
fastpy make:admin                        # Create super admin (interactive)
fastpy make:admin -n "Admin" -e admin@example.com -p secretpass -y

# Database setup (migrations)
fastpy db:setup                          # Run migrations (auto-generate if needed)
```

## Deployment Commands

Deploy your FastAPI application to production with Nginx, SSL, and systemd.

### Quick Start Deployment

```bash
# 1. Initialize deployment config
fastpy deploy:init

# 2. Add frontend domains for CORS
fastpy domain:add https://app.example.com --frontend
fastpy domain:add https://admin.example.com --frontend

# 3. Deploy everything (requires sudo on server)
sudo fastpy deploy:run --apply
```

### Deployment Commands Reference

```bash
# Initialization
fastpy deploy:init                       # Interactive setup wizard
fastpy deploy:init -d api.example.com    # Quick setup with domain
fastpy deploy:init -d api.example.com -p 8000 -y  # Non-interactive

# Individual components
fastpy deploy:nginx                      # Generate Nginx config
sudo fastpy deploy:nginx --apply         # Apply Nginx config
sudo fastpy deploy:ssl                   # Setup Let's Encrypt SSL
fastpy deploy:systemd                    # Generate systemd service
sudo fastpy deploy:systemd --apply       # Install and start service

# Status and checks
fastpy deploy:status                     # Show deployment status
fastpy deploy:check                      # Check server requirements
sudo fastpy deploy:install               # Install missing requirements
```

### Domain Management (CORS)

```bash
# Add domains for CORS
fastpy domain:add https://frontend.example.com
fastpy domain:add https://mobile-app.example.com --frontend
fastpy domain:add localhost:3000         # Auto-adds http://

# Manage domains
fastpy domain:list                       # List all configured domains
fastpy domain:remove https://old.example.com
```

### Environment Variables

```bash
fastpy env:set DATABASE_URL=postgresql://user:pass@localhost/db
fastpy env:set DEBUG=false
fastpy env:set SECRET_KEY=your-secret-key
fastpy env:get DATABASE_URL
fastpy env:list                          # List all (secrets masked)
```

### Service Management

```bash
sudo fastpy service:start               # Start the application
sudo fastpy service:stop                # Stop the application
sudo fastpy service:restart             # Restart (after code changes)
fastpy service:status                   # Check service status
fastpy service:logs                     # View recent logs
fastpy service:logs -f                  # Follow logs in real-time
fastpy service:logs -n 100              # Last 100 lines
```

### Deployment Configuration

Configuration is stored in `.fastpy/deploy.json`:

```json
{
  "app_name": "my-api",
  "domain": "api.example.com",
  "port": 8000,
  "workers": 4,
  "allowed_origins": ["https://app.example.com"],
  "frontend_domains": ["https://dashboard.example.com"],
  "ssl_enabled": true,
  "ssl_type": "letsencrypt",
  "ssl_email": "admin@example.com",
  "user": "www-data",
  "use_gunicorn": true
}
```

### Generated Files

| File | Purpose |
|------|---------|
| `.fastpy/deploy.json` | Deployment configuration |
| `.fastpy/nginx/{app}.conf` | Nginx reverse proxy config |
| `.fastpy/systemd/{app}.service` | Systemd service file |

### Nginx Features

Generated Nginx config includes:
- Reverse proxy to Gunicorn/Uvicorn
- WebSocket support (`/ws` endpoint)
- SSL/TLS with Let's Encrypt (A+ rating)
- Security headers (HSTS, X-Frame-Options, etc.)
- Gzip compression
- Static file serving with caching
- CORS preflight handling

### Systemd Service Features

Generated service includes:
- Gunicorn with Uvicorn workers (or direct Uvicorn)
- Auto-restart on failure
- Security hardening (NoNewPrivileges, PrivateTmp)
- Environment file support
- Logging to `/var/log/{app}/`

## Database Commands

```bash
fastpy db:migrate                         # Run pending migrations
fastpy db:migrate -m "Add posts"          # Generate + run migrations
fastpy db:make "Add slug to posts"        # Generate migration only
fastpy db:rollback                        # Rollback one migration
fastpy db:rollback --steps 3              # Rollback multiple
fastpy db:fresh                           # Drop all & re-migrate
fastpy db:seed                            # Run all seeders
fastpy db:seed --seeder User --count 50   # Run specific seeder
```

## Field Definition Syntax

**Format:** `name:type:rules`

**Field Types:**
string, text, integer, bigint, float, decimal, money, percent, boolean, datetime, date, time, email, url, uuid, json, phone, slug, ip, color, file, image

**Validation Rules:**
- `required` - Field cannot be null
- `nullable` - Field can be null
- `unique` - Unique constraint
- `index` - Database index
- `max:N` - Maximum length/value
- `min:N` - Minimum length/value
- `ge:N` / `gte:N` - Greater than or equal
- `le:N` / `lte:N` - Less than or equal
- `gt:N` - Greater than
- `lt:N` - Less than
- `foreign:table.column` - Foreign key
- `default:value` - Default value

**Examples:**
```bash
-f title:string:required,max:200
-f price:decimal:required,ge:0
-f user_id:integer:required,foreign:users.id
-f email:email:required,unique
-f published_at:datetime:nullable
```

## Project Architecture

```
app/
├── config/           # Application settings (settings.py)
├── controllers/      # Business logic (CRUD operations)
├── database/         # DB connection and session management
├── enums/            # Enum definitions
├── middleware/       # Custom middleware
│   ├── request_id.py   # X-Request-ID tracking
│   ├── timing.py       # X-Response-Time header
│   └── rate_limit.py   # Sliding window rate limiting
├── models/           # SQLModel models with Pydantic schemas
├── repositories/     # Data access layer (BaseRepository)
├── routes/           # API route definitions
├── seeders/          # Database seeders
├── services/         # Business logic services (BaseService)
└── utils/
    ├── auth.py         # JWT & password hashing
    ├── exceptions.py   # Custom exceptions
    ├── logger.py       # Structured logging
    ├── pagination.py   # Pagination utilities
    └── responses.py    # Standard response format

tests/
├── conftest.py       # Pytest fixtures
├── factories.py      # Test data factories
└── test_*.py         # Test files
```

## Naming Conventions

- **Tables**: plural, snake_case (`users`, `blog_posts`)
- **Models**: singular, PascalCase (`User`, `BlogPost`)
- **Files**: snake_case (`user_controller.py`)
- **Controllers**: `{Model}Controller`
- **Routes**: `{model}_routes.py`

## Base Model Features

All models inherit from `BaseModel` which provides:
- `id` - Auto-incrementing primary key
- `created_at` - Timestamp on creation
- `updated_at` - Timestamp on update
- `deleted_at` - Soft delete timestamp
- `soft_delete()` - Soft delete method
- `restore()` - Restore soft deleted record
- `is_deleted` - Property to check if deleted
- `touch()` - Update timestamps

### Active Record Methods

```python
# Create
user = await User.create(name="John", email="john@example.com")

# Find
user = await User.find(1)                          # Returns None if not found
user = await User.find_or_fail(1)                  # Raises NotFoundException

# Query
users = await User.where(active=True)              # List of matching records
user = await User.first_where(email="john@example.com")
user = await User.first_or_fail(email="john@example.com")

# Update
user.name = "Jane"
await user.save()

await user.update(name="Jane", email="jane@example.com")

# Delete
await user.delete()              # Soft delete
await user.delete(force=True)    # Hard delete
```

## Model Concerns (Laravel-style Traits)

Mix in Laravel-style functionality to your models:

```python
from app.models.base import BaseModel
from app.models.concerns import (
    HasCasts, HasAttributes, HasEvents, HasScopes, GuardsAttributes
)

class Post(BaseModel, HasCasts, HasAttributes, HasEvents, HasScopes, GuardsAttributes, table=True):
    # ... model definition
```

### Attribute Casting

Auto-convert database values to Python types:

```python
class Post(BaseModel, HasCasts, table=True):
    _casts = {
        'settings': 'json',        # JSON string <-> dict
        'is_active': 'boolean',    # 1/0 <-> True/False
        'metadata': 'dict',        # Ensure dict type
        'tags': 'list',            # Ensure list type
        'price': 'decimal:2',      # Decimal with 2 places
        'published_at': 'datetime',
    }

# Usage
post.settings = {'featured': True}  # Stored as JSON string
print(post.settings)                 # Returns dict: {'featured': True}
```

**Available cast types:** `boolean`, `integer`, `float`, `string`, `json`, `dict`, `list`, `date`, `datetime`, `decimal:N`

### Accessors and Mutators

Computed properties and value transformers:

```python
from app.models.concerns import accessor, mutator

class User(BaseModel, HasAttributes, table=True):
    first_name: str
    last_name: str
    password: str

    # Virtual attributes to include in serialization
    _appends = ['full_name']
    _hidden = ['password']

    @accessor
    def full_name(self) -> str:
        """Computed property."""
        return f"{self.first_name} {self.last_name}"

    @mutator('password')
    def hash_password(self, value: str) -> str:
        """Transform value before storing."""
        from app.utils.auth import get_password_hash
        return get_password_hash(value)

# Usage
user.full_name          # "John Doe"
user.password = "secret" # Automatically hashed
user.to_dict()          # Includes full_name, excludes password
```

### Model Events

Hook into model lifecycle:

```python
from app.models.concerns import HasEvents, ModelObserver

class UserObserver(ModelObserver):
    def creating(self, user):
        user.uuid = str(uuid4())

    def created(self, user):
        send_welcome_email(user)

    def deleting(self, user):
        # Return False to cancel deletion
        if user.is_admin:
            return False
        return True

class User(BaseModel, HasEvents, table=True):
    @classmethod
    def booted(cls):
        cls.observe(UserObserver())

        # Or inline handlers:
        cls.creating(lambda u: setattr(u, 'uuid', str(uuid4())))
```

**Events:** `creating`, `created`, `updating`, `updated`, `saving`, `saved`, `deleting`, `deleted`, `restoring`, `restored`

### Query Scopes

Reusable query constraints:

```python
class Post(BaseModel, HasScopes, table=True):
    @classmethod
    def scope_published(cls, query):
        return query.where(cls.is_published == True)

    @classmethod
    def scope_popular(cls, query, min_views: int = 1000):
        return query.where(cls.views >= min_views)

    @classmethod
    def scope_by_author(cls, query, author_id: int):
        return query.where(cls.author_id == author_id)

# Fluent query building
posts = await Post.query().published().popular(5000).latest().get()
posts = await Post.query().by_author(1).paginate(page=2, per_page=20)

# With soft deletes
posts = await Post.query().with_trashed().get()   # Include deleted
posts = await Post.query().only_trashed().get()   # Only deleted
```

**QueryBuilder methods:** `where()`, `where_in()`, `where_null()`, `order_by()`, `latest()`, `oldest()`, `limit()`, `offset()`, `get()`, `first()`, `count()`, `exists()`, `paginate()`

### Mass Assignment Protection

Protect against mass assignment vulnerabilities:

```python
class User(BaseModel, GuardsAttributes, table=True):
    # Whitelist: only these can be mass-assigned
    _fillable = ['name', 'email', 'password']

    # OR blacklist: everything except these
    _guarded = ['is_admin', 'role']

# Safe mass assignment
user = await User.create(**request.validated_data)  # Only fillable fields
user.fill(name="John", is_admin=True)               # is_admin ignored

# Bypass protection when needed
user.force_fill(is_admin=True)

# Temporarily disable protection
from app.models.concerns import Unguarded
with Unguarded(User):
    await User.create(is_admin=True)
```

## Route Model Binding

Auto-resolve route parameters to model instances:

```python
from app.utils.binding import bind, bind_or_fail, bind_trashed

@router.get("/users/{id}")
async def show_user(user: User = bind(User)):
    return user  # Automatically fetched by ID

@router.get("/posts/{slug}")
async def show_post(post: Post = bind(Post, param="slug", field="slug")):
    return post  # Fetched by slug field

@router.put("/users/{id}")
async def update_user(
    user: User = bind_or_fail(User),
    request: UpdateUserRequest = validated(UpdateUserRequest)
):
    await user.update(**request.validated_data)
    return user

# Include soft-deleted records
@router.post("/posts/{id}/restore")
async def restore_post(post: Post = bind_trashed(Post)):
    await post.restore()
    return post
```

## FormRequest Validation (Laravel-style)

Create form request classes with validation rules:

```bash
# Generate request classes
fastpy make:request CreateContact -f name:required|max:255 -f email:required|email|unique:contacts
fastpy make:request UpdateUser --model User --update

# Or generate with resource (includes Create and Update requests)
fastpy make:resource Contact -f name:string:required -f email:email:required -m -p -v
```

### Using FormRequest in Routes

```python
from app.validation import validated
from app.requests.contact_request import CreateContactRequest, UpdateContactRequest

@router.post("/contacts")
async def create(request: CreateContactRequest = validated(CreateContactRequest)):
    """Create with automatic validation"""
    return await Contact.create(**request.validated_data)

@router.put("/contacts/{id}")
async def update(
    request: UpdateContactRequest = validated(UpdateContactRequest),
    contact: Contact = bind_or_fail(Contact)
):
    """Update with validation + route binding"""
    await contact.update(**request.validated_data)
    return contact
```

### Defining FormRequest Classes

```python
from app.validation.form_request import FormRequest

class CreateContactRequest(FormRequest):
    rules = {
        'name': 'required|max:255',
        'email': 'required|email|unique:contacts',
        'phone': 'nullable|phone',
    }

    messages = {
        'email.unique': 'This email is already registered.',
    }

    def authorize(self, user=None) -> bool:
        return user is not None  # Require authentication

    def prepare_for_validation(self, data: dict) -> dict:
        # Transform data before validation
        if 'email' in data:
            data['email'] = data['email'].lower().strip()
        return data
```

**Available Validation Rules:** `required`, `nullable`, `email`, `url`, `max:N`, `min:N`, `unique:table,column`, `exists:table,column`, `confirmed`, `in:val1,val2`, `numeric`, `integer`, `boolean`, `date`, `phone`, `uuid`, `json`

## Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user (JSON) |
| `/api/auth/login` | POST | Login (form-data, OAuth2) |
| `/api/auth/login/json` | POST | Login (JSON: email, password) |
| `/api/auth/refresh` | POST | Refresh access token |
| `/api/auth/me` | GET | Get current user |
| `/api/auth/change-password` | POST | Change password |
| `/api/auth/forgot-password` | POST | Request password reset |
| `/api/auth/reset-password` | POST | Reset password with token |
| `/api/auth/verify-email` | POST | Verify email address |
| `/api/auth/logout` | POST | Logout |

## Protecting Routes

```python
from app.utils.auth import get_current_active_user
from app.models.user import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"user": current_user}
```

## Standard Response Format

```python
from app.utils.responses import success_response, error_response, paginated_response

# Success
return success_response(data=user, message="User created")

# Error
return error_response(message="Not found", code="NOT_FOUND", status_code=404)

# Paginated
return paginated_response(items=users, page=1, per_page=20, total=100)
```

## Custom Exceptions

```python
from app.utils.exceptions import (
    NotFoundException,          # 404
    BadRequestException,        # 400
    UnauthorizedException,      # 401
    ForbiddenException,         # 403
    ConflictException,          # 409
    ValidationException,        # 422
    RateLimitException,         # 429
    ServiceUnavailableException # 503
)

raise NotFoundException("User not found")
raise ServiceUnavailableException("Database unavailable")
```

## Middleware

### Built-in Middleware

| Middleware | Header | Description |
|------------|--------|-------------|
| `RequestIDMiddleware` | `X-Request-ID` | Unique ID for request tracing |
| `TimingMiddleware` | `X-Response-Time` | Response time in ms |
| `RateLimitMiddleware` | `X-RateLimit-*` | Sliding window rate limiting |

### Request ID Middleware
Adds unique request ID for tracing:
```python
# Access in route
from starlette.requests import Request

@router.get("/")
async def route(request: Request):
    request_id = request.state.request_id
```

### Timing Middleware
Logs slow requests (>1s) and adds `X-Response-Time` header.

### Rate Limit Middleware
Configure in `.env`:
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100    # requests per window
RATE_LIMIT_WINDOW=60       # window in seconds
```

Response headers:
- `X-RateLimit-Limit` - Max requests allowed
- `X-RateLimit-Remaining` - Requests remaining
- `X-RateLimit-Reset` - Seconds until reset

### Creating Custom Middleware
```bash
fastpy make:middleware Logging
```

Example middleware structure:
```python
# app/middleware/logging_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Before request
        response = await call_next(request)
        # After request
        return response
```

Register in `main.py`:
```python
from app.middleware.logging_middleware import LoggingMiddleware
app.add_middleware(LoggingMiddleware)
```

## Health Check Endpoints

- `GET /health/` - Basic health check
- `GET /health/ready` - Readiness (includes DB)
- `GET /health/live` - Liveness probe
- `GET /health/info` - Service information

## Testing

```bash
pytest                              # Run all tests
pytest -v                           # Verbose output
pytest tests/test_auth.py           # Specific file
pytest --cov=app --cov-report=html  # With coverage
```

## Environment Variables

Key settings in `.env`:
- `DB_DRIVER` - postgresql or mysql
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT secret (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiry (default: 30)
- `RATE_LIMIT_ENABLED` - Enable rate limiting
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)

## Fastpy Libs

Fastpy provides clean facades for common tasks. Import from `fastpy_cli.libs`:

```python
from fastpy_cli.libs import Http, Mail, Cache, Storage, Queue, Event, Notify, Hash, Crypt, Job, Notification
```

### Available Facades

| Facade | Description |
|--------|-------------|
| `Http` | HTTP client (GET, POST, PUT, DELETE) |
| `Mail` | Email sending (SMTP, SendGrid, Mailgun, SES) |
| `Cache` | Caching (Memory, File, Redis) |
| `Storage` | File storage (Local, S3, Memory) |
| `Queue` | Job queues (Sync, Memory, Redis, Database) |
| `Event` | Event dispatcher with listeners |
| `Notify` | Multi-channel notifications (Mail, Database, Slack, SMS) |
| `Hash` | Password hashing (bcrypt, argon2, sha256) |
| `Crypt` | Data encryption (Fernet, AES-256-CBC) |

### Http Facade

```python
from fastpy_cli.libs import Http

# Basic requests
response = Http.get('https://api.example.com/users')
response = Http.post('https://api.example.com/users', json={'name': 'John'})
response = Http.put(url, json=data)
response = Http.delete(url)

# With authentication
response = Http.with_token('bearer-token').get('/api/protected')
response = Http.with_basic_auth('user', 'pass').get(url)

# With headers
response = Http.with_headers({'X-Custom': 'value'}).get(url)

# Testing (fake responses)
Http.fake({'https://api.example.com/*': {'status': 200, 'json': {'ok': True}}})
response = Http.get('https://api.example.com/test')
Http.assert_sent('https://api.example.com/test')
```

### Mail Facade

```python
from fastpy_cli.libs import Mail

# Send email with template
Mail.to('user@example.com').subject('Welcome!').send('welcome', {'name': 'John'})

# Multiple recipients
Mail.to(['user1@example.com', 'user2@example.com']) \
    .cc('manager@example.com') \
    .bcc('archive@example.com') \
    .subject('Team Update') \
    .send('update', {'message': 'Hello team!'})

# Raw HTML
Mail.to('user@example.com').subject('Hello').html('<h1>Hello World</h1>').send()

# Attachments
Mail.to(email).attach('/path/to/file.pdf').send('invoice', data)

# Use specific driver
Mail.driver('sendgrid').to('user@example.com').send('template', data)
```

### Cache Facade

```python
from fastpy_cli.libs import Cache

# Store value
Cache.put('key', 'value', ttl=3600)  # 1 hour

# Get value
value = Cache.get('key', default='fallback')

# Check existence
if Cache.has('key'):
    print('Key exists')

# Remember (get or compute)
users = Cache.remember('users', lambda: fetch_users_from_db(), ttl=600)

# Delete
Cache.forget('key')
Cache.flush()  # Clear all

# Cache tags (for grouped invalidation)
Cache.tags(['users', 'active']).put('user:1', user_data)
Cache.tags(['users']).flush()  # Clear all user-related cache

# Increment/decrement
Cache.increment('visits')
Cache.decrement('stock', 5)

# Use specific store
Cache.store('redis').put('key', 'value')
```

### Storage Facade

```python
from fastpy_cli.libs import Storage

# Store file
Storage.put('avatars/user.jpg', file_content)

# Get file content
content = Storage.get('avatars/user.jpg')

# Get public URL
url = Storage.url('avatars/user.jpg')

# Check existence
if Storage.exists('avatars/user.jpg'):
    print('File exists')

# Delete
Storage.delete('avatars/user.jpg')

# List files
files = Storage.list('avatars/')

# Copy/move
Storage.copy('source.jpg', 'dest.jpg')
Storage.move('old.jpg', 'new.jpg')

# Use specific disk
Storage.disk('s3').put('backups/data.zip', content)
url = Storage.disk('s3').url('backups/data.zip')
```

### Queue/Jobs Facade

```python
from fastpy_cli.libs import Queue, Job

# Define a job
class SendEmailJob(Job):
    def __init__(self, user_id: int, template: str):
        self.user_id = user_id
        self.template = template

    def handle(self):
        user = get_user(self.user_id)
        send_email(user.email, self.template)

# Push job to queue
Queue.push(SendEmailJob(user_id=1, template='welcome'))

# Delay job (seconds)
Queue.later(60, SendEmailJob(user_id=1, template='reminder'))

# Chain jobs (run sequentially)
Queue.chain([
    ProcessOrderJob(order_id=1),
    SendConfirmationJob(order_id=1),
    UpdateInventoryJob(order_id=1),
])

# Use specific queue
Queue.on('emails').push(SendEmailJob(user_id=1, template='welcome'))
```

### Event Facade

```python
from fastpy_cli.libs import Event

# Listen to events
Event.listen('user.registered', lambda data: send_welcome_email(data['user']))
Event.listen('order.created', lambda data: notify_admin(data['order']))

# Dispatch event
Event.dispatch('user.registered', {'user': user})

# Wildcard listeners
Event.listen('user.*', lambda data: log_user_activity(data))
Event.listen('*.created', lambda data: log_creation(data))

# Event subscriber class
class UserSubscriber:
    def subscribe(self, events):
        events.listen('user.registered', self.on_registered)
        events.listen('user.deleted', self.on_deleted)

    def on_registered(self, data):
        print(f"User registered: {data['user'].id}")

    def on_deleted(self, data):
        print(f"User deleted: {data['user'].id}")

Event.subscribe(UserSubscriber())
```

### Notifications Facade

```python
from fastpy_cli.libs import Notify, Notification

# Define notification
class OrderShippedNotification(Notification):
    def __init__(self, order):
        self.order = order

    def via(self, notifiable) -> list:
        return ['mail', 'database', 'slack']

    def to_mail(self, notifiable) -> dict:
        return {
            'subject': 'Your order has shipped!',
            'template': 'order_shipped',
            'data': {'order': self.order}
        }

    def to_database(self, notifiable) -> dict:
        return {
            'type': 'order_shipped',
            'data': {'order_id': self.order.id}
        }

    def to_slack(self, notifiable) -> dict:
        return {'text': f'Order #{self.order.id} has shipped!'}

    def to_sms(self, notifiable) -> str:
        return f'Order #{self.order.id} shipped!'

# Send notification
Notify.send(user, OrderShippedNotification(order))

# Send to multiple users
Notify.send(users, OrderShippedNotification(order))

# On-demand (anonymous) notification
Notify.route('mail', 'guest@example.com') \
    .route('slack', '#orders') \
    .notify(OrderShippedNotification(order))
```

### Hash Facade

```python
from fastpy_cli.libs import Hash

# Hash a password
hashed = Hash.make('password')

# Verify password
if Hash.check('password', hashed):
    print('Password is valid!')

# Check if rehash needed (for upgrading security parameters)
if Hash.needs_rehash(hashed):
    new_hash = Hash.make('password')

# Use specific algorithm
hashed = Hash.driver('argon2').make('password')  # argon2 (recommended for new apps)
hashed = Hash.driver('bcrypt').make('password')  # bcrypt (default)
hashed = Hash.driver('sha256').make('password')  # PBKDF2-SHA256 (fallback)

# Configure bcrypt rounds
Hash.configure('bcrypt', {'rounds': 14})
```

### Crypt Facade

```python
from fastpy_cli.libs import Crypt

# Generate encryption key (do once, save to .env)
key = Crypt.generate_key()
# Add to .env: APP_KEY=<key>

# Set key (or use APP_KEY environment variable)
Crypt.set_key(key)

# Encrypt data
encrypted = Crypt.encrypt('secret data')

# Encrypt complex data (auto JSON serialized)
encrypted = Crypt.encrypt({'user_id': 123, 'token': 'abc'})

# Decrypt
data = Crypt.decrypt(encrypted)

# Use specific driver
encrypted = Crypt.driver('aes').encrypt('secret')  # AES-256-CBC
```

### Libs CLI Command

```bash
# List all available libs
fastpy libs

# View lib info and usage examples
fastpy libs http --usage
fastpy libs mail --usage
fastpy libs cache --usage
fastpy libs queue --usage
```

## User-Specific Instructions

- All table Actions should be in an ActionGroup
- Use JSON for all POST/PUT/PATCH request bodies
- Always use async/await for database operations
- Filter soft deletes in queries: `where(Model.deleted_at.is_(None))`
- **Prefer Fastpy libs** over raw implementations for: HTTP requests, email sending, caching, file storage, job queues, events, notifications, password hashing, and encryption
- When generating code that needs any of the above features, use the appropriate facade from `fastpy_cli.libs`
