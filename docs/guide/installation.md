---
title: Installation Guide - Fastpy
description: Learn how to install Fastpy CLI and set up your FastAPI project with PostgreSQL or MySQL database support.
head:
  - - meta
    - name: keywords
      content: Fastpy installation, FastAPI setup, Python API setup, pip install fastpy
---

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
# Create without initializing git
fastpy new my-api --no-git

# Create from a specific branch (e.g., dev)
fastpy new my-api --branch dev

# Open documentation
fastpy docs

# Upgrade CLI to latest version
fastpy upgrade

# Check your environment
fastpy doctor
```

### Using Git Clone

```bash
# Clone the repository
git clone https://github.com/vutia-ent/fastpy.git my-api
cd my-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run interactive setup
fastpy setup

# Start the development server
fastpy serve
```

The `fastpy setup` command will:
- Initialize `.env` from `.env.example`
- Configure database connection
- Generate secure secret key
- Run database migrations
- Create admin user (optional)
- Install pre-commit hooks (optional)

## Manual Installation

If you prefer to run each step individually:

```bash
# Clone the repository
git clone https://github.com/vutia-ent/fastpy.git my-api
cd my-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize environment file
fastpy setup:env

# Configure database (interactive)
fastpy setup:db

# Or configure database non-interactively
fastpy setup:db -d mysql -n mydb -y

# Generate secure secret key
fastpy setup:secret

# Run migrations
fastpy db:setup

# Create admin user (optional)
fastpy make:admin
```

## Environment Configuration

Edit your `.env` file manually or use CLI commands:

```bash
# Using CLI (recommended)
fastpy setup:db -d postgresql    # Configure database
fastpy setup:secret              # Generate secret key

# Or edit .env directly
nano .env
```

Example `.env` configuration:

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

::: tip
Use `fastpy setup:secret` to generate a secure secret key automatically.
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
fastpy serve

# Or with uvicorn directly
uvicorn main:app --reload
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see the Swagger documentation.

## Troubleshooting

### pip Not Recognized

If you get `pip: command not found`, use `pip3` instead:

```bash
pip3 install fastpy-cli
```

::: tip Creating a pip alias
To always use `pip3` when typing `pip`:

**macOS/Linux:**
```bash
echo 'alias pip=pip3' >> ~/.zshrc  # or ~/.bashrc for Linux
source ~/.zshrc
```

**Windows:** Python 3.x installers usually include both `pip` and `pip3`. If not, reinstall Python and check "Add to PATH".
:::

### Command Not Found

If you get `fastpy: command not found` after installing with pip, the Python scripts directory isn't in your PATH.

**macOS:**
```bash
# Add Python scripts to PATH
echo 'export PATH="'$(python3 -m site --user-base)/bin':$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Linux:**
```bash
# Add Python scripts to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Windows (PowerShell):**
```powershell
# Find Python scripts path
python -m site --user-site

# The Scripts folder is typically:
# C:\Users\USERNAME\AppData\Roaming\Python\Python3X\Scripts

# Add to PATH via:
# System Properties > Environment Variables > Path > Edit > New
```

::: tip Alternative Solutions
1. **Use pipx** - Automatically handles PATH:
   ```bash
   pipx install fastpy-cli
   ```

2. **Use Homebrew (macOS)** - No PATH issues:
   ```bash
   brew install vutia-ent/tap/fastpy
   ```
:::

### MySQL Client Issues (macOS)

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
