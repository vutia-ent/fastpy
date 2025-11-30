# Installation

Get Fastpy up and running in your development environment.

## Requirements

- Python 3.9 or higher
- PostgreSQL or MySQL
- Git

## Quick Install (Recommended)

### Using Fastpy CLI

The fastest way to create a new project:

::: code-group

```bash [pip]
# Install Fastpy CLI globally
pip install fastpy-cli

# Create a new project
fastpy new my-api
```

```bash [pipx]
# Install with pipx (isolated environment)
pipx install fastpy-cli

# Create a new project
fastpy new my-api
```

```bash [Homebrew]
# Add the tap and install
brew tap vutia-ent/tap
brew install fastpy

# Create a new project
fastpy new my-api
```

:::

The `fastpy new` command will:
- Clone the Fastpy template
- Initialize a fresh git repository
- Optionally run the interactive setup

#### CLI Options

```bash
# Create without running interactive setup
fastpy new my-api --no-setup

# Create without initializing git
fastpy new my-api --no-git

# Open documentation
fastpy docs

# Upgrade CLI to latest version
fastpy upgrade
```

### Using Git Clone

```bash
# Clone the repository
git clone https://github.com/vutia-ent/fastpy.git my-api
cd my-api

# Run the automated setup
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Start the development server
python cli.py serve
# Or: uvicorn main:app --reload
```

The setup script will:
- Create a Python virtual environment
- Install all dependencies
- Copy `.env.example` to `.env`
- Initialize the database
- Run initial migrations

## Manual Installation

If you prefer manual setup:

```bash
# Clone the repository
git clone https://github.com/vutia-ent/fastpy.git my-api
cd my-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials
nano .env

# Run migrations
alembic upgrade head
```

## Environment Configuration

Edit your `.env` file with your settings:

```bash
# Application
APP_NAME="My API"
ENVIRONMENT=development
DEBUG=true

# Database (PostgreSQL)
DB_DRIVER=postgresql
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Or MySQL
# DB_DRIVER=mysql
# DATABASE_URL=mysql://user:password@localhost:3306/mydb

# Authentication
SECRET_KEY=your-super-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

::: warning
Always change `SECRET_KEY` to a random value in production. Generate one with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
:::

## Database Setup

### PostgreSQL

```bash
# Create database
createdb mydb

# Or with psql
psql -c "CREATE DATABASE mydb;"
```

### MySQL

```bash
# Create database
mysql -e "CREATE DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Verify Installation

```bash
# Start the development server
python cli.py serve

# Or with uvicorn directly
uvicorn main:app --reload
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see the Swagger documentation.

## macOS Troubleshooting

### MySQL Client Issues

If you encounter `mysqlclient` installation errors on macOS:

```bash
# Install MySQL client via Homebrew
brew install mysql-client

# Add to your shell profile (zsh)
export PATH="/opt/homebrew/opt/mysql-client/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/mysql-client/lib"
export CPPFLAGS="-I/opt/homebrew/opt/mysql-client/include"
```

### bcrypt Issues

For bcrypt compilation errors:

```bash
pip install bcrypt==4.2.1 --no-binary bcrypt
```

## Next Steps

- [Quick Start](/guide/quickstart) - Build your first resource
- [Configuration](/guide/configuration) - Deep dive into settings
