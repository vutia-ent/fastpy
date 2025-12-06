---
title: Installation Guide - Fastpy
description: Learn how to install Fastpy CLI and set up your FastAPI project with PostgreSQL, MySQL, or SQLite database support.
head:
  - - meta
    - name: keywords
      content: Fastpy installation, FastAPI setup, Python API setup, pip install fastpy
---

# Installation

Get Fastpy up and running in your development environment.

## Requirements

- Python 3.9 or higher
- PostgreSQL, MySQL, or SQLite
- Git

## Install Fastpy CLI

::: code-group

```bash [pip]
pip install fastpy-cli
```

```bash [pipx]
pipx install fastpy-cli
```

```bash [Homebrew]
brew tap vutia-ent/tap
brew install fastpy
```

:::

Verify installation:

```bash
fastpy version
```

## Shell Integration (Recommended)

Enable auto-cd and auto-activate for the best experience:

```bash
fastpy shell:install
source ~/.zshrc  # or ~/.bashrc
```

This adds a shell function that automatically:
- Changes into the project directory after `fastpy new`
- Activates the virtual environment after project creation or `fastpy install`

## Create a New Project

### One-Command Setup (Recommended)

Create a fully configured project with one command:

```bash
fastpy new my-api
```

This will:
- Clone the Fastpy template
- Create a virtual environment
- Install all dependencies (auto-installs MySQL client on macOS if needed)
- Run the setup wizard (database, secrets, migrations)
- Display next steps

If you installed shell integration, you'll be automatically placed in the project with venv activated. Otherwise:

```bash
cd my-api
source venv/bin/activate  # Windows: venv\Scripts\activate
fastpy serve              # Start development server
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see your API.

### Step-by-Step Setup

If you prefer more control:

```bash
# Create project
fastpy new my-api
cd my-api

# Install dependencies (creates venv + installs packages + runs setup)
fastpy install

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Start server
fastpy serve
```

### CLI Options

```bash
# Create with automatic setup (default, recommended)
fastpy new my-api

# Skip automatic setup (manual installation)
fastpy new my-api --no-install

# Create without initializing git
fastpy new my-api --no-git

# Create from a specific branch
fastpy new my-api --branch dev

# Install dependencies only (skip setup wizard)
fastpy install --skip-setup

# Skip MySQL packages (for SQLite/PostgreSQL only projects)
fastpy install --skip-mysql

# Use different requirements file
fastpy install -r requirements-dev.txt
```

## Using Git Clone

```bash
# Clone the repository
git clone https://github.com/vutia-ent/fastpy.git my-api
cd my-api

# Install with fastpy install
fastpy install

# Or manually:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
fastpy setup
```

## Setup Commands

The `fastpy setup` wizard will:
- Initialize `.env` from `.env.example`
- Configure database connection
- Generate secure secret key
- Run database migrations
- Create admin user (optional)
- Install pre-commit hooks (optional)

Run individual setup steps:

```bash
fastpy setup:env      # Initialize .env file
fastpy setup:db       # Configure database
fastpy setup:secret   # Generate secret key
fastpy setup:hooks    # Install pre-commit hooks
```

## Database Configuration

### Interactive Setup

```bash
fastpy setup:db
```

### Non-Interactive Setup

```bash
# MySQL
fastpy setup:db -d mysql -h localhost -u root -n mydb -y

# PostgreSQL
fastpy setup:db -d postgresql -h localhost -u postgres -n mydb -y

# SQLite (development)
fastpy setup:db -d sqlite -n dev -y
```

### Manual Configuration

Edit `.env` directly:

```bash
# PostgreSQL
DB_DRIVER=postgresql
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# MySQL
DB_DRIVER=mysql
DATABASE_URL=mysql://user:password@localhost:3306/mydb

# SQLite
DB_DRIVER=sqlite
DATABASE_URL=sqlite:///./app.db
```

## Environment Variables

Example `.env` configuration:

```bash
# Application
APP_NAME="My API"
ENVIRONMENT=development
DEBUG=true

# Database
DB_DRIVER=postgresql
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Authentication
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

::: tip
Use `fastpy setup:secret` to generate a secure secret key automatically.
:::

## Troubleshooting

### pip Not Recognized

Use `pip3` instead:

```bash
pip3 install fastpy-cli
```

Create an alias:

::: code-group

```bash [macOS/Linux]
echo 'alias pip=pip3' >> ~/.zshrc
source ~/.zshrc
```

```powershell [Windows]
# Reinstall Python and check "Add to PATH"
```

:::

### fastpy Command Not Found

The Python scripts directory isn't in your PATH.

::: code-group

```bash [macOS]
echo 'export PATH="'$(python3 -m site --user-base)/bin':$PATH"' >> ~/.zshrc
source ~/.zshrc
```

```bash [Linux]
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

```powershell [Windows]
# Add to PATH via System Properties > Environment Variables
# Path: C:\Users\USERNAME\AppData\Roaming\Python\Python3X\Scripts
```

:::

**Alternatives:**
- Use `pipx install fastpy-cli` (handles PATH automatically)
- Use `brew install vutia-ent/tap/fastpy` (macOS)

### MySQL Client Issues (macOS)

Fastpy automatically offers to install MySQL client on macOS when needed. If you prefer to install manually:

```bash
brew install mysql-client
export PATH="/opt/homebrew/opt/mysql-client/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/mysql-client/lib"
export CPPFLAGS="-I/opt/homebrew/opt/mysql-client/include"
```

Or skip MySQL packages entirely if you're using SQLite or PostgreSQL:

```bash
fastpy install --skip-mysql
```

### bcrypt Issues

```bash
pip install bcrypt==4.2.1 --no-binary bcrypt
```

## Diagnostics

Use `fastpy doctor` to diagnose issues:

```bash
fastpy doctor
```

This checks:
- Python version
- Git installation
- Virtual environment status
- Dependencies (uvicorn, alembic, fastapi, sqlmodel)
- Environment configuration (.env, DATABASE_URL, SECRET_KEY)
- AI provider configuration
- Migration status

## Verify Installation

```bash
# Check CLI version
fastpy version

# Check environment
fastpy doctor

# Start server
fastpy serve
```

## Next Steps

- [Quick Start](/guide/quickstart) - Build your first resource
- [Configuration](/guide/configuration) - Deep dive into settings
- [CLI Commands](/commands/overview) - All available commands
