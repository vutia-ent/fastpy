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

```bash
# Generate complete resource (model + controller + routes)
fastpy make:resource Post -f title:string:required,max:200 -f body:text:required -m -p

# Individual generators
fastpy make:model Post -f title:string:required -m      # Model + migration
fastpy make:controller Post                              # Controller
fastpy make:route Post --protected                       # Routes (with auth)
fastpy make:service Post                                 # Service class
fastpy make:repository Post                              # Repository class
fastpy make:middleware Logging                           # Middleware
fastpy make:test Post                                    # Test file
fastpy make:factory Post                                 # Test factory
fastpy make:seeder Post                                  # Database seeder
fastpy make:enum Status -v active -v inactive            # Enum
fastpy make:exception PaymentFailed -s 400               # Custom exception

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

## Database Commands

```bash
fastpy db:migrate                         # Run migrations
fastpy db:rollback                        # Rollback one migration
fastpy db:rollback --steps 3              # Rollback multiple
fastpy db:fresh                           # Drop all & re-migrate
fastpy db:seed                            # Run all seeders
fastpy db:seed --seeder User --count 50   # Run specific seeder

# Alembic directly
alembic revision --autogenerate -m "Add posts table"
alembic upgrade head
alembic downgrade -1
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

## Fastpy Libs (Laravel-Style Facades)

Fastpy provides Laravel-style facades for common tasks. Import from `fastpy_cli.libs`:

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
