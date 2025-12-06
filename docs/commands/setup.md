# Setup Commands

Setup commands help initialize and configure a new Fastpy project.

## Quick Start

### One-Command Setup (Recommended)

```bash
# Create project with automatic setup
fastpy new my-api --install
cd my-api
source venv/bin/activate
fastpy setup
fastpy serve
```

### Step-by-Step Setup

```bash
# Create project
fastpy new my-api
cd my-api

# Install dependencies (creates venv + installs packages)
fastpy install

# Activate and configure
source venv/bin/activate
fastpy setup
```

## fastpy install

Install project dependencies and set up the development environment. This command automates virtual environment creation and package installation.

```bash
fastpy install
```

### Options

| Option | Description |
|--------|-------------|
| `--skip-setup` | Skip running the interactive setup wizard |
| `--skip-venv` | Skip virtual environment creation |
| `-r, --requirements` | Requirements file to install (default: requirements.txt) |

### Examples

```bash
# Full install with setup wizard
fastpy install

# Install dependencies only (skip setup)
fastpy install --skip-setup

# Use different requirements file
fastpy install -r requirements-dev.txt

# Skip venv creation (use existing environment)
fastpy install --skip-venv
```

### What It Does

1. Creates virtual environment (`venv`) if it doesn't exist
2. Upgrades pip to latest version
3. Installs dependencies from requirements.txt
4. Optionally runs `fastpy setup` wizard

## fastpy setup

Complete interactive project setup wizard. Handles all configuration steps in one command.

```bash
fastpy setup
```

### Options

| Option | Description |
|--------|-------------|
| `--skip-db` | Skip database configuration |
| `--skip-migrations` | Skip running migrations |
| `--skip-admin` | Skip admin user creation |
| `--skip-hooks` | Skip pre-commit hooks installation |

### Example

```bash
# Full setup
fastpy setup

# Setup without migrations (configure manually later)
fastpy setup --skip-migrations

# Minimal setup (just env and secret)
fastpy setup --skip-db --skip-migrations --skip-admin --skip-hooks
```

### What It Does

1. **Environment Setup** - Creates `.env` from `.env.example`
2. **Database Configuration** - Configures database connection
3. **Secret Key** - Generates secure JWT secret
4. **Migrations** - Runs database migrations
5. **Admin User** - Creates super admin account
6. **Pre-commit Hooks** - Installs code quality hooks

## fastpy setup:env

Initialize the `.env` file from `.env.example`.

```bash
fastpy setup:env
```

If `.env` already exists, you'll be prompted to backup and recreate it.

### Example

```bash
$ fastpy setup:env
╭─────────────────────────╮
│ Environment Setup       │
╰─────────────────────────╯
✓ Created .env from .env.example
```

## fastpy setup:db

Configure database connection interactively or via command-line options.

```bash
fastpy setup:db
```

### Supported Databases

| Driver | Package | Use Case |
|--------|---------|----------|
| `mysql` | mysqlclient, pymysql | Production (recommended) |
| `postgresql` | psycopg2-binary | Production |
| `sqlite` | aiosqlite | Development/testing only |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--driver` | `-d` | Database driver (mysql, postgresql, sqlite) |
| `--host` | `-h` | Database host |
| `--port` | `-p` | Database port |
| `--username` | `-u` | Database username |
| `--password` | | Database password |
| `--database` | `-n` | Database name |
| `--no-create` | | Don't auto-create database |
| `--yes` | `-y` | Non-interactive mode |

### Examples

```bash
# Interactive setup
fastpy setup:db

# MySQL with defaults
fastpy setup:db -d mysql

# PostgreSQL with custom database name
fastpy setup:db -d postgresql -n my_app_db

# SQLite for development
fastpy setup:db -d sqlite -n dev_db

# Full non-interactive setup
fastpy setup:db -d mysql -h localhost -p 3306 -u root -n myapp --password secret -y
```

### What It Does

1. Prompts for database driver selection
2. Checks if database server is running
3. Configures connection parameters
4. Updates `DB_DRIVER` and `DATABASE_URL` in `.env`
5. Optionally creates the database if it doesn't exist

## fastpy setup:secret

Generate a secure secret key for JWT token signing.

```bash
fastpy setup:secret
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--length` | `-l` | Secret key length (default: 64) |

### Examples

```bash
# Generate 64-character key (default)
fastpy setup:secret

# Generate 128-character key for extra security
fastpy setup:secret -l 128
```

### What It Does

1. Generates cryptographically secure random key using Python's `secrets` module
2. Updates `SECRET_KEY` in `.env` file

::: warning Security Note
Always generate a new secret key for production. Never use the default key from `.env.example`.
:::

## fastpy setup:hooks

Install pre-commit hooks for code quality.

```bash
fastpy setup:hooks
```

### Requirements

- Git repository must be initialized (`.git` directory exists)
- `pre-commit` package must be installed
- `.pre-commit-config.yaml` must exist in project root

### What It Does

1. Verifies git repository exists
2. Checks pre-commit is installed
3. Runs `pre-commit install` to set up hooks

### Example

```bash
$ fastpy setup:hooks
╭─────────────────────────────╮
│ Pre-commit Hooks Setup      │
╰─────────────────────────────╯
✓ Pre-commit hooks installed
```

## fastpy make:admin

Create a super admin user for the application.

```bash
fastpy make:admin
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--name` | `-n` | Admin name |
| `--email` | `-e` | Admin email |
| `--password` | `-p` | Admin password (min 8 chars) |
| `--yes` | `-y` | Non-interactive mode |

### Examples

```bash
# Interactive mode
fastpy make:admin

# Non-interactive mode
fastpy make:admin -n "Admin" -e admin@example.com -p "securepass123" -y
```

### Requirements

- Database must be configured (`.env` has `DATABASE_URL`)
- Migrations must be run (users table exists)

### What It Does

1. Prompts for admin name, email, and password
2. Validates password length (minimum 8 characters)
3. Hashes password securely with bcrypt
4. Creates user with `email_verified_at` set (pre-verified)
5. Checks for duplicate email before creation

## fastpy db:setup

Run database migrations with optional auto-generation.

```bash
fastpy db:setup
```

### Options

| Option | Description |
|--------|-------------|
| `--auto-generate/--no-auto-generate` | Auto-generate initial migration if none exist (default: true) |

### Examples

```bash
# Run migrations (auto-generate if needed)
fastpy db:setup

# Run migrations without auto-generation
fastpy db:setup --no-auto-generate
```

### What It Does

1. Checks if migrations exist in `alembic/versions/`
2. If no migrations and `--auto-generate` is true, creates initial migration
3. Runs `fastpy db:migrate` to apply all migrations

## Workflow Examples

### New Project Setup (Recommended)

```bash
# One-command project creation
fastpy new my-api --install
cd my-api
source venv/bin/activate
fastpy setup
fastpy serve
```

### New Project Setup (Step-by-Step)

```bash
# 1. Create project
fastpy new my-api
cd my-api

# 2. Install dependencies
fastpy install

# 3. Activate and run
source venv/bin/activate
fastpy serve
```

### CI/CD Pipeline Setup

```bash
# Non-interactive setup for automation
fastpy setup:env
fastpy setup:db -d postgresql -h $DB_HOST -u $DB_USER -n $DB_NAME --password "$DB_PASS" -y
fastpy setup:secret
fastpy db:setup
```

### Development Environment Reset

```bash
# Reconfigure database
fastpy setup:db -d sqlite -n dev

# Regenerate secret (invalidates all tokens)
fastpy setup:secret

# Run fresh migrations
fastpy db:fresh

# Create new admin
fastpy make:admin
```

## Command Reference

| Command | Description |
|---------|-------------|
| `fastpy install` | Create venv, install deps, run setup |
| `fastpy setup` | Full interactive project setup |
| `fastpy setup:env` | Initialize .env from .env.example |
| `fastpy setup:db` | Configure database connection |
| `fastpy setup:secret` | Generate secure JWT secret key |
| `fastpy setup:hooks` | Install pre-commit hooks |
| `fastpy make:admin` | Create super admin user |
| `fastpy db:setup` | Run database migrations |
