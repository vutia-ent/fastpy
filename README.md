# VE.KE API

A production-ready FastAPI starter template with SQLModel, PostgreSQL/MySQL support, JWT authentication, and MVC architecture. Features include soft deletes, automatic timestamps, a powerful CLI for code generation, and a clean folder structure.

## Features

- ✅ FastAPI with async/await support
- ✅ SQLModel (SQLAlchemy + Pydantic) for database models
- ✅ **PostgreSQL OR MySQL** support (configurable)
- ✅ Alembic for database migrations
- ✅ **JWT Authentication** (register, login, protected routes)
- ✅ **Powerful CLI** (`python cli.py make:model`, `make:controller`, etc.)
- ✅ MVC architecture (models, controllers, routes)
- ✅ Base model with `id`, `created_at`, `updated_at`, `deleted_at` (soft deletes)
- ✅ Clean naming conventions (snake_case, plural table names)
- ✅ Password hashing with bcrypt
- ✅ CORS middleware configured
- ✅ Environment-based configuration

## Prerequisites

- Python 3.9 or higher
- PostgreSQL 12+ OR MySQL 5.7+ (MySQL 8.0+ recommended)
- pip

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd api

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Note for MySQL users on macOS:**
If you encounter issues installing `mysqlclient`, you may need:
```bash
brew install mysql
export PATH="/usr/local/opt/mysql/bin:$PATH"
pip install mysqlclient
```

### 2. Database Setup

**For PostgreSQL:**
```bash
# Create database
createdb veke_db

# OR using psql
psql -U postgres
CREATE DATABASE veke_db;
\q
```

**For MySQL:**
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE veke_db;

# Verify database was created
SHOW DATABASES;

# Exit MySQL
exit;
```

**Important MySQL Notes:**
- Make sure your MySQL server is running
- Note your MySQL username and password for the `.env` file
- Default MySQL credentials are usually `root` with your MySQL root password

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

**PostgreSQL example:**
```env
DB_DRIVER=postgresql
DATABASE_URL=postgresql://username:password@localhost:5432/veke_db
```

**MySQL example:**
```env
DB_DRIVER=mysql
DATABASE_URL=mysql://root:password@localhost:3306/veke_db
```

### 4. Run Migrations

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

**Common Migration Issues:**

**PostgreSQL:**
- Error `FATAL: password authentication failed` → Check credentials in `.env`
- Error `database does not exist` → Create database first: `createdb dbname`

**MySQL:**
- Error `Access denied for user` → Verify username/password in `.env`
- Error `No module named 'MySQLdb'` → Run `pip install mysqlclient`
- Error `Can't connect to MySQL server` → Start MySQL: `mysql.server start`

### 5. Start the Server

```bash
uvicorn main:app --reload
```

The API will be available at:
- **API Root**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc

## CLI Commands

This starter includes a powerful CLI for rapid development:

```bash
# List all commands
python cli.py list

# Create a model
python cli.py make:model BlogPost
python cli.py make:model BlogPost --migration  # Create model + migration

# Create a controller
python cli.py make:controller BlogPost

# Create routes
python cli.py make:route BlogPost

# Create everything at once (model + controller + routes)
python cli.py make:resource BlogPost
python cli.py make:resource BlogPost --migration
```

After installation, you can also use the `artisan` command:
```bash
artisan make:model Post
artisan make:resource Comment -m
```

## Project Structure

```
.
├── app/
│   ├── config/
│   │   └── settings.py          # Application settings
│   ├── controllers/
│   │   ├── user_controller.py   # Business logic
│   │   └── auth_controller.py   # Authentication logic
│   ├── database/
│   │   └── connection.py        # Database connection & session
│   ├── models/
│   │   ├── base.py              # Base model with timestamps & soft deletes
│   │   └── user.py              # User model
│   ├── routes/
│   │   ├── user_routes.py       # User API routes
│   │   └── auth_routes.py       # Auth API routes
│   ├── middleware/              # Custom middleware
│   └── utils/
│       └── auth.py              # JWT utilities & password hashing
├── alembic/
│   ├── versions/                # Migration files
│   └── env.py                   # Alembic configuration
├── tests/                       # Test files
├── cli.py                       # Code generation CLI
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project configuration
├── alembic.ini                 # Alembic configuration
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info (protected)

### Users (Protected)
- `GET /api/users` - Get all users (excludes soft-deleted)
- `GET /api/users/{id}` - Get user by ID
- `POST /api/users` - Create new user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Soft delete user
- `POST /api/users/{id}/restore` - Restore soft-deleted user

## Authentication

### Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=securepassword123"
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

### Access Protected Routes
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Database Migrations

```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# Rollback to specific revision
alembic downgrade <revision_id>
```

## Development

### Code Formatting

```bash
black .
```

### Linting

```bash
ruff check .

# Auto-fix issues
ruff check . --fix
```

### Type Checking

```bash
mypy .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_users.py
```

## Coding Conventions

### Naming Conventions
- **Tables**: Plural, snake_case (e.g., `users`, `blog_posts`)
- **Columns**: snake_case (e.g., `created_at`, `email_verified_at`)
- **Models**: Singular, PascalCase (e.g., `User`, `BlogPost`)

### Base Model Fields
All models inherit from `BaseModel` which includes:
- `id` - Primary key (auto-increment)
- `created_at` - Timestamp (auto-set on create)
- `updated_at` - Timestamp (auto-updated)
- `deleted_at` - Timestamp for soft deletes (nullable)

### Soft Deletes
```python
# Soft delete a user
user.soft_delete()

# Restore a user
user.restore()

# Check if deleted
if user.is_deleted:
    print("User is deleted")
```

## Creating New Resources

### Using CLI (Recommended)

```bash
# Create model, controller, and routes all at once
python cli.py make:resource Post --migration

# Then update main.py to register the routes
```

### Manual Creation

1. **Create model** in `app/models/`:

```python
from sqlmodel import Field
from app.models.base import BaseModel

class Post(BaseModel, table=True):
    __tablename__ = "posts"

    title: str = Field(nullable=False, max_length=255)
    content: str = Field(nullable=False)
    user_id: int = Field(foreign_key="users.id")
```

2. **Import in `alembic/env.py`**:

```python
from app.models.post import Post  # noqa
```

3. **Generate and run migration**:

```bash
alembic revision --autogenerate -m "Create posts table"
alembic upgrade head
```

4. **Create controller and routes** (or use CLI commands)

5. **Register routes in `main.py`**:

```python
from app.routes.post_routes import router as post_router
app.include_router(post_router, prefix="/api/posts", tags=["Posts"])
```

## Database Support

This starter supports both **PostgreSQL** and **MySQL**. Configure in `.env`:

### PostgreSQL
```env
DB_DRIVER=postgresql
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
```

**Required drivers** (automatically installed):
- `psycopg2-binary` - Synchronous driver for Alembic migrations
- `asyncpg` - Async driver for FastAPI application

### MySQL
```env
DB_DRIVER=mysql
DATABASE_URL=mysql://username:password@localhost:3306/dbname
```

**Required drivers** (automatically installed):
- `mysqlclient` - Synchronous driver for Alembic migrations (provides MySQLdb)
- `aiomysql` - Async driver for FastAPI application
- `pymysql` - Alternative driver with pure Python implementation

**Troubleshooting MySQL:**
- Ensure MySQL server is running: `mysql.server start` (macOS) or `sudo service mysql start` (Linux)
- If `mysqlclient` fails to install, install MySQL development headers first
- Test connection: `mysql -u username -p`

## Environment Variables

See `.env.example` for all available configuration options:

- `DB_DRIVER` - Database driver (`postgresql` or `mysql`)
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Secret key for JWT (generate with `openssl rand -hex 32`)
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
- `DEBUG` - Enable debug mode
- `APP_NAME` - Application name
- `APP_VERSION` - Application version

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Generate secure `SECRET_KEY`:
   ```bash
   openssl rand -hex 32
   ```
3. Configure `DATABASE_URL` for production database
4. Update CORS allowed origins in `main.py`
5. Use a production ASGI server like `gunicorn` with `uvicorn` workers:

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Security Best Practices

- ✅ Passwords are hashed using bcrypt
- ✅ JWT tokens for authentication
- ✅ CORS configured (update for production)
- ✅ Soft deletes instead of hard deletes
- ⚠️ Change `SECRET_KEY` in production
- ⚠️ Use HTTPS in production
- ⚠️ Configure CORS allowed origins properly

## Contributing

This is a starter template. Feel free to customize the structure and add features as needed.

## License

MIT
