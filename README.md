# VE.KE API

A production-ready FastAPI starter template with SQLModel, PostgreSQL/MySQL support, JWT authentication, and MVC architecture. Features **FastCLI** - an intelligent code generator with automatic validation, AI assistant integration, and one-command setup.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-00C7B7.svg)](https://fastapi.tiangolo.com)
[![SQLModel](https://img.shields.io/badge/SQLModel-0.0.22-red.svg)](https://sqlmodel.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents

- [Key Features](#-key-features)
- [Quick Start](#-quick-start-tldr)
- [FastCLI - Code Generation](#fastcli---code-generation-tool)
- [Setup Instructions](#detailed-setup)
- [API Endpoints](#api-endpoints)
- [Testing](#running-tests)
- [Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## 🚀 Key Features

### **FastCLI - Intelligent Code Generator**
- 🎯 **Field-based generation**: Define models with simple syntax: `title:string:required,max:200`
- ✨ **Automatic validation**: Pydantic rules generated from field definitions
- 🤖 **AI Integration**: Generate config files for Claude, Copilot, Gemini, Cursor
- 💬 **Interactive mode**: Guided field creation with prompts
- 🔗 **Foreign keys**: Automatic relationship setup
- 📦 **Smart imports**: Auto-adds EmailStr, datetime, JSON when needed
- ⚡ **One command**: Generate model + controller + routes + migration

### **Database & ORM**
- ✅ **SQLModel** (SQLAlchemy + Pydantic) for type-safe models
- ✅ **PostgreSQL OR MySQL** support (configurable via .env)
- ✅ **Alembic** migrations with auto-generation
- ✅ **Soft deletes** via `deleted_at` timestamp
- ✅ **Auto timestamps**: `created_at`, `updated_at` on all models
- ✅ **Async operations**: Full async/await support

### **Authentication & Security**
- 🔐 **JWT tokens** with configurable expiration
- 🔒 **Bcrypt** password hashing (compatible versions)
- 👤 **Protected routes** with dependency injection
- 🛡️ **CORS** middleware configured
- ✅ **Password validation**: Min 8, max 72 characters

### **Architecture & Code Quality**
- 🏗️ **MVC pattern**: Models, Controllers, Routes separation
- 📝 **Base model**: Automatic id, timestamps, soft deletes
- 🎨 **Naming conventions**: snake_case tables, PascalCase models
- 🧪 **Testing**: pytest, faker, factory-boy included
- ✨ **Code quality**: black, ruff, mypy, pre-commit hooks
- 📚 **Type hints**: Full type safety with mypy

### **Developer Experience**
- 🎬 **One-command setup**: `./setup.sh` with intelligent detection
- 📦 **Essential packages**: File uploads, email validation, timezones, templates
- 📖 **Auto-generated docs**: Swagger UI & ReDoc
- 🔍 **Detailed logging**: Setup logs for troubleshooting
- 🌐 **Environment-based**: Easy configuration via .env

## Prerequisites

- Python 3.9 or higher
- PostgreSQL 12+ OR MySQL 5.7+ (MySQL 8.0+ recommended)
- pip

## ⚡ Quick Start (TL;DR)

```bash
# Clone and setup
git clone <your-repo-url> && cd api
./setup.sh

# Generate a resource with FastCLI
fastcli make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -f author_id:integer:foreign:users.id \
  -m -p

# Run migrations and start
alembic upgrade head
uvicorn main:app --reload
```

Visit: http://localhost:8000/docs 🚀

## 🎯 Why This Starter?

**This isn't just another FastAPI template.** It's a complete development system that:

- ⚡ **Saves hours**: One command generates models, controllers, routes, and migrations
- 🤖 **AI-ready**: Built-in configs for Claude, Copilot, Gemini, Cursor
- 🛡️ **Production-ready**: JWT auth, soft deletes, migrations, testing - all configured
- 🎨 **Best practices**: MVC architecture, type safety, async operations
- 📦 **Batteries included**: Essential packages for real-world apps
- 🔧 **Zero-config setup**: `./setup.sh` handles everything

**Compare:**

| Traditional Approach | With FastCLI |
|---------------------|--------------|
| 30+ mins: Manual model setup | ⚡ 30 seconds: One command |
| Write validation rules manually | ✨ Auto-generated from fields |
| Setup auth from scratch | 🔐 JWT ready out of the box |
| Configure database manually | 🗄️ Interactive setup wizard |
| Research best practices | 📚 Built-in conventions |

### 📦 What's Included

```
🎯 FastCLI Code Generator
   ├── Field-based model generation
   ├── Automatic Pydantic validation
   ├── Interactive & command-line modes
   └── AI assistant configurations

🗄️ Database Layer
   ├── SQLModel ORM (type-safe)
   ├── PostgreSQL & MySQL support
   ├── Alembic migrations
   ├── Soft deletes
   └── Auto timestamps

🔐 Authentication System
   ├── JWT token generation
   ├── Bcrypt password hashing
   ├── Protected routes
   └── User registration/login

🏗️ Architecture
   ├── MVC pattern
   ├── Async/await throughout
   ├── Dependency injection
   └── RESTful API design

🧪 Quality Assurance
   ├── pytest with async support
   ├── black (formatting)
   ├── ruff (linting)
   ├── mypy (type checking)
   ├── pre-commit hooks
   └── Factory fixtures

🚀 Developer Tools
   ├── One-command setup script
   ├── Auto-generated API docs
   ├── Environment configuration
   ├── Docker examples
   └── CI/CD templates
```

## Detailed Setup

### Automated Setup (Recommended)

The easiest way to set up the project is using our intelligent automated setup script:

```bash
# Clone the repository
git clone <your-repo-url>
cd api

# Run the setup script
./setup.sh
```

#### What the Setup Script Does

The setup script provides a **guided, interactive setup experience** with the following features:

**System Checks:**
- ✅ Validates Python 3.9+ is installed and compatible
- ✅ Checks if database servers (PostgreSQL/MySQL) are running
- ✅ Verifies database existence and offers to create it
- ✅ Detects existing installations and offers upgrade options

**Automated Installation:**
- ✅ Creates/recreates virtual environment (with confirmation)
- ✅ Upgrades pip to latest version
- ✅ Installs all core dependencies
- ✅ Installs dev dependencies (testing, linting, formatting)
- ✅ Logs all operations to `setup.log` for troubleshooting

**Smart Configuration:**
- ✅ Creates `.env` from `.env.example` (backs up existing files)
- ✅ Interactive database selection (PostgreSQL, MySQL, or skip)
- ✅ Customizable database name and connection URL
- ✅ Generates cryptographically secure JWT secret key
- ✅ macOS and Linux compatible (detects OS for proper commands)

**Database Setup:**
- ✅ Checks database server availability
- ✅ Tests if database already exists
- ✅ Offers to create database automatically
- ✅ Generates and runs Alembic migrations
- ✅ Provides helpful error messages with fix suggestions

**Code Quality:**
- ✅ Optional pre-commit hooks installation
- ✅ Verifies core package installation
- ✅ Provides helpful next steps and useful commands

**Error Handling:**
- ✅ Comprehensive error messages with solutions
- ✅ Detailed logging for debugging (saved to `setup.log`)
- ✅ Graceful fallbacks for missing dependencies
- ✅ Clear instructions for manual fixes when needed

#### Setup Script Features

**Interactive Prompts:**
- Choose database type (PostgreSQL/MySQL)
- Custom database name
- Recreate existing virtual environment
- Reconfigure existing `.env` file
- Run migrations immediately or later
- Install pre-commit hooks

**Smart Defaults:**
- PostgreSQL: `postgresql://postgres:password@localhost:5432/veke_db`
- MySQL: `mysql://root:password@localhost:3306/veke_db`
- Press Enter to use defaults, or provide custom values

**Logging:**
All operations are logged to `setup.log` for troubleshooting. If anything goes wrong, check this file for detailed error information.

### Manual Setup

If you prefer to set up manually:

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

### 2. Database Setup (Manual Setup Only)

**Note:** If you used `setup.sh`, database configuration is already done. Skip to step 5.

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

### 3. Environment Configuration (Manual Setup Only)

**Note:** If you used `setup.sh`, .env is already configured. Skip to step 5.

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

### 4. Run Migrations (Manual Setup Only)

**Note:** If you used `setup.sh`, migrations may already be applied. Skip to step 5.

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

**Alembic Migrations:**
- Error `name 'sqlmodel' is not defined` in migration file:
  - Add `import sqlmodel` at the top of the migration file
  - This happens when Alembic generates migrations with SQLModel types

**AsyncIO/Greenlet:**
- Error `No module named 'greenlet'` → Run `pip install greenlet`
- This is required for async SQLAlchemy operations

### 5. Start the Server

```bash
uvicorn main:app --reload
```

The API will be available at:
- **API Root**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc

## FastCLI - Code Generation Tool

This starter includes **FastCLI**, a powerful code generation tool with automatic validation:

### AI Assistant Integration

FastCLI can generate AI-specific configuration files for your preferred coding assistant:

```bash
# Generate config for your AI assistant
fastcli init:ai              # Interactive mode
fastcli init:ai claude       # Claude Code (CLAUDE.md)
fastcli init:ai copilot      # GitHub Copilot (.github/copilot-instructions.md)
fastcli init:ai gemini       # Google Gemini (.gemini/instructions.md)
fastcli init:ai cursor       # Cursor AI (.cursorrules)
```

Each AI config file includes:
- ✅ Project overview and tech stack
- ✅ FastCLI commands and syntax
- ✅ Naming conventions and architecture patterns
- ✅ Common development workflows
- ✅ Code generation guidelines
- ✅ Testing and deployment commands

This helps your AI assistant understand your project structure and generate code that follows your conventions!

### Quick Examples

```bash
# List all commands with examples
fastcli list

# Create a blog post with intelligent field definitions
fastcli make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -f published:boolean:required \
  -f author_id:integer:required,foreign:users.id \
  -m -p

# Interactive mode (guided field creation)
fastcli make:resource Comment -i -m

# Create model only with validations
fastcli make:model Product \
  -f name:string:required,max:255 \
  -f price:float:required,ge:0 \
  -f email:email:required,unique \
  -m
```

### Field Definition Syntax

**Format:** `name:type:rules`

**Available Field Types:**
- `string` - Short text (max 255 chars by default)
- `text` - Long text
- `integer` - Whole numbers
- `float` - Decimal numbers
- `boolean` - True/False
- `datetime` - Date and time
- `email` - Email with validation
- `url` - URL string
- `json` - JSON data

**Available Validation Rules:**
- `required` - Field cannot be null
- `nullable` - Field can be null (default)
- `unique` - Unique constraint at database level
- `index` - Create database index
- `max:N` - Maximum length/value
- `min:N` - Minimum length/value
- `ge:N` / `gte:N` - Greater than or equal to
- `le:N` / `lte:N` - Less than or equal to
- `gt:N` - Greater than
- `lt:N` - Less than
- `foreign:table.column` - Foreign key constraint

### Real-World Examples

**1. Blog System:**
```bash
# Create Post model with validations
fastcli make:resource Post \
  -f title:string:required,max:200,min:5 \
  -f slug:string:required,unique,max:200 \
  -f body:text:required,min:50 \
  -f excerpt:text:nullable,max:500 \
  -f published_at:datetime:nullable \
  -f author_id:integer:required,foreign:users.id \
  -m -p
```

This generates:
- ✅ SQLModel with proper field types and constraints
- ✅ Pydantic schemas with automatic validations
- ✅ Create schema: `title` must be 5-200 chars, `body` min 50 chars
- ✅ Update schema: All fields optional
- ✅ Read schema: Includes timestamps
- ✅ Controller with full CRUD operations
- ✅ Protected routes (authentication required)
- ✅ Migration files ready

**2. E-commerce Product:**
```bash
fastcli make:model Product \
  -f name:string:required,max:255 \
  -f description:text:nullable \
  -f price:float:required,ge:0 \
  -f stock:integer:required,ge:0 \
  -f sku:string:required,unique,max:50 \
  -f category_id:integer:required,foreign:categories.id \
  -m
```

**3. User Profile:**
```bash
fastcli make:resource Profile \
  -f user_id:integer:required,unique,foreign:users.id \
  -f bio:text:nullable,max:1000 \
  -f avatar_url:url:nullable \
  -f website:url:nullable \
  -f phone:string:nullable,max:20 \
  -m -p
```

**4. Interactive Mode:**
```bash
fastcli make:resource Category -i

# Then follow prompts:
# Field definition: name:string:required,unique,max:100
# ✓ Added field: name (string)
# Field definition: description:text:nullable
# ✓ Added field: description (text)
# Field definition: [press Enter to finish]
```

### CLI Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `init:ai` | Generate AI assistant config | `fastcli init:ai claude` |
| `make:model` | Create model with validations | `fastcli make:model Post -f title:string:required,max:200 -m` |
| `make:controller` | Create controller | `fastcli make:controller Post` |
| `make:route` | Create routes | `fastcli make:route Post --protected` |
| `make:resource` | Create all at once | `fastcli make:resource Post -i -m -p` |
| `list` | Show all commands | `fastcli list` |

### CLI Options

- `-f, --field` - Define a field (use multiple times)
- `-i, --interactive` - Interactive mode with prompts
- `-m, --migration` - Generate migration after creation
- `-p, --protected` - Add authentication to routes

### What Gets Generated

When you run `fastcli make:resource Post -f title:string:required,max:200 -f body:text:required -m -p`:

**1. Model** (`app/models/post.py`):
```python
class Post(BaseModel, table=True):
    __tablename__ = "posts"
    title: str = Field(nullable=False, max_length=200)
    body: str = Field(nullable=False)

class PostCreate(BaseModel):
    # Validation rules automatically applied
    title: str = Field(min_length=1, max_length=200)
    body: str

class PostUpdate(BaseModel):
    # All optional for partial updates
    title: Optional[str] = Field(default=None, max_length=200)
    body: Optional[str] = Field(default=None)

class PostRead(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime
```

**2. Controller** (`app/controllers/post_controller.py`):
- Full CRUD operations
- Soft delete support
- Async database operations
- Error handling

**3. Routes** (`app/routes/post_routes.py`):
- RESTful endpoints
- Protected with authentication (if `-p` used)
- Proper response models
- Pagination support

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

### Important Notes

**Password Requirements:**
- Minimum 8 characters (defined in User model)
- Maximum 72 characters (bcrypt limitation)
- Automatically hashed using bcrypt before storage

**Bcrypt Compatibility:**
- This project uses `bcrypt==4.2.1` with `passlib==1.7.4`
- These versions are tested and compatible
- If you encounter bcrypt errors, ensure you have these exact versions

**Token Management:**
- JWT tokens expire after 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Tokens include user email in the `sub` (subject) claim
- Use `Authorization: Bearer <token>` header for protected endpoints

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

## Essential Packages Included

This starter includes carefully selected packages for production-ready FastAPI applications:

### Core Framework
- **fastapi** - Modern async web framework with automatic API docs
- **uvicorn** - Lightning-fast ASGI server
- **pydantic** - Data validation with type hints
- **pydantic[email]** - Email validation support

### HTTP & File Operations
- **httpx** - Async HTTP client for making API calls
- **aiofiles** - Async file operations (reading/writing files)
- **python-multipart** - Form data & file upload support

### Database
- **sqlmodel** - ORM combining SQLAlchemy + Pydantic
- **alembic** - Database migration tool
- **PostgreSQL drivers**: psycopg2-binary (sync), asyncpg (async)
- **MySQL drivers**: mysqlclient (sync), aiomysql (async)

### Authentication & Security
- **python-jose** - JWT token creation and validation
- **passlib** - Password hashing library
- **bcrypt** - Secure password hashing algorithm

### Utilities
- **python-dateutil** - Powerful date/time parsing and manipulation
- **pytz** - Timezone support for datetime operations
- **python-slugify** - Generate URL-friendly slugs from text
- **jinja2** - Template engine for emails and HTML rendering

### Testing (Dev Dependencies)
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Code coverage reports
- **faker** - Generate realistic fake data for tests
- **factory-boy** - Create test fixtures and mock objects

### Code Quality (Dev Dependencies)
- **black** - Code formatter
- **ruff** - Fast Python linter
- **mypy** - Static type checker
- **pre-commit** - Git hooks for code quality checks

### Optional Packages
See `requirements.txt` for optional packages you can uncomment as needed:
- **emails** - Email sending
- **redis** - Caching with Redis
- **celery** - Background task processing
- **pillow** - Image processing
- **sentry-sdk** - Error tracking
- **slowapi** - Rate limiting
- **markdown** - Markdown rendering in API docs

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

## Troubleshooting

### Setup Script Issues

**Setup script fails with "Permission denied":**
```bash
chmod +x setup.sh
./setup.sh
```

**Setup script logs show dependency installation errors:**
- Check `setup.log` for detailed error messages
- Common causes:
  - Missing system libraries (MySQL/PostgreSQL dev headers)
  - Insufficient disk space
  - Network connectivity issues
- Try manual installation: `pip install -r requirements.txt`

**Database creation fails:**
- **PostgreSQL**: Ensure you have superuser privileges or use existing database
  ```bash
  # Check if PostgreSQL is running
  psql -U postgres -c "SELECT 1"

  # Create database manually
  createdb -U postgres veke_db
  ```
- **MySQL**: Check user privileges
  ```bash
  # Login to MySQL
  mysql -u root -p

  # Create database manually
  CREATE DATABASE veke_db;
  GRANT ALL PRIVILEGES ON veke_db.* TO 'your_user'@'localhost';
  ```

**"Python 3.9+ required" error:**
- Install Python 3.9 or higher
- macOS: `brew install python@3.11`
- Ubuntu: `sudo apt-get install python3.11`
- Verify: `python3 --version`

**Secret key generation fails (no openssl):**
- Install openssl:
  - macOS: `brew install openssl`
  - Ubuntu: `sudo apt-get install openssl`
- Or manually generate a key:
  ```bash
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```

**Setup completes but migrations fail:**
- Check database credentials in `.env`
- Verify database server is running
- Check `setup.log` for specific SQL errors
- Try running migrations manually: `alembic upgrade head`

### Installation Issues

**`mysqlclient` fails to install on macOS:**
```bash
# Install MySQL development headers
brew install mysql

# Add MySQL to PATH
export PATH="/usr/local/opt/mysql/bin:$PATH"

# Then install
pip install mysqlclient
```

**`psycopg2-binary` fails to install:**
```bash
# On macOS
brew install postgresql

# On Ubuntu/Debian
sudo apt-get install libpq-dev
```

### Runtime Errors

**Error: `No module named 'greenlet'`**
```bash
pip install greenlet==3.2.4
```

**Error: `ValueError: the greenlet library is required`**
- Make sure `greenlet` is installed
- Restart your server after installation

**Error: `password cannot be longer than 72 bytes`**
- This is a bcrypt limitation
- Ensure passwords are ≤72 characters
- The error may also indicate bcrypt version mismatch
- Use `bcrypt==4.2.1` with `passlib==1.7.4`

**Error: `module 'bcrypt' has no attribute '__about__'`**
```bash
# Fix: Use compatible versions
pip install bcrypt==4.2.1 passlib==1.7.4
```

**Error: `name 'sqlmodel' is not defined` in Alembic migration**
- Open the migration file in `alembic/versions/`
- Add `import sqlmodel` at the top with other imports
- This happens because Alembic doesn't auto-import SQLModel types

### Database Connection Issues

**MySQL: `Can't connect to MySQL server`**
```bash
# macOS
mysql.server start

# Linux
sudo service mysql start

# Verify MySQL is running
mysql -u root -p -e "SELECT 1;"
```

**PostgreSQL: `FATAL: password authentication failed`**
- Check your `DATABASE_URL` in `.env`
- Verify credentials with: `psql -U username -d database`

**MySQL: `Access denied for user 'root'@'localhost'`**
- Verify password in `.env`
- Test connection: `mysql -u root -p`
- Make sure `DB_DRIVER=mysql` matches your DATABASE_URL

### API Errors

**401 Unauthorized on protected endpoints:**
- Check that token is included: `Authorization: Bearer <token>`
- Verify token hasn't expired (30-minute default)
- Ensure token was obtained from `/api/auth/login`

**500 Internal Server Error:**
- Check server logs with `uvicorn main:app --reload`
- Common causes:
  - Database connection issues
  - Missing environment variables
  - Incompatible package versions

### Development Tips

**Uvicorn not reloading on changes:**
- Make sure you're using `--reload` flag
- Check that changes are saved
- Restart server manually if needed

**Database changes not reflected:**
```bash
# Generate new migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

**Clear all data and start fresh:**
```bash
# Drop all tables
alembic downgrade base

# Re-run migrations
alembic upgrade head
```

## Advanced Setup Options

### Customizing the Setup Script

The `setup.sh` script can be customized for your specific needs:

**Environment Variables:**
Set these before running `setup.sh` to skip prompts:
```bash
export VEKE_DB_TYPE=postgresql
export VEKE_DB_NAME=custom_db
export VEKE_SKIP_MIGRATIONS=true
./setup.sh
```

**Viewing Setup Logs:**
```bash
# View the complete setup log
cat setup.log

# Watch log in real-time during setup
tail -f setup.log
```

**Re-running Setup:**
The script intelligently detects existing installations:
- Existing `.env` files are backed up as `.env.backup.TIMESTAMP`
- Virtual environment can be recreated or reused
- Database migrations are skipped if already applied

### Docker Setup (Optional)

For containerized deployment, create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations and start server
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/veke_db
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=veke_db
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### CI/CD Integration

**GitHub Actions example** (`.github/workflows/test.yml`):
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -e ".[dev]"

    - name: Run tests
      run: pytest
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
```

### Performance Tuning

**For production deployments:**

1. **Use Gunicorn with Uvicorn workers:**
```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **Database connection pooling** (add to `app/database/connection.py`):
```python
engine = create_async_engine(
    database_url,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

3. **Enable async database connections:**
Already configured for async with `asyncpg` (PostgreSQL) and `aiomysql` (MySQL)

## Contributing

This is a starter template. Feel free to customize the structure and add features as needed.

**Contributions welcome:**
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## License

MIT
