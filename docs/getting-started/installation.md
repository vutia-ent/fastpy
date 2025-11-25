# Installation

This guide covers the complete installation process for FastCLI and the FastAPI starter template.

## Prerequisites

Before installing, ensure you have the following:

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.9+ | `python --version` |
| pip | Latest | `pip --version` |
| PostgreSQL | 12+ | `psql --version` |
| MySQL (alternative) | 5.7+ | `mysql --version` |

## Automated Setup (Recommended)

The easiest way to get started is using our intelligent setup script:

```bash
# Clone the repository
git clone https://github.com/veke/api.git
cd api

# Run the setup script
./setup.sh
```

### What the Setup Script Does

The setup script provides a guided, interactive experience:

!!! success "System Checks"
    - Validates Python 3.9+ is installed
    - Checks database servers (PostgreSQL/MySQL)
    - Verifies database existence
    - Detects existing installations

!!! success "Automated Installation"
    - Creates virtual environment
    - Upgrades pip to latest version
    - Installs all dependencies
    - Logs operations to `setup.log`

!!! success "Smart Configuration"
    - Creates `.env` from template
    - Interactive database selection
    - Generates secure JWT secret key
    - macOS and Linux compatible

!!! success "Database Setup"
    - Tests database connectivity
    - Offers to create database automatically
    - Runs Alembic migrations
    - Provides helpful error messages

## Manual Setup

If you prefer manual installation:

### 1. Clone and Create Virtual Environment

```bash
# Clone the repository
git clone https://github.com/veke/api.git
cd api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your settings
nano .env  # or use your preferred editor
```

### 4. Database Setup

=== "PostgreSQL"

    ```bash
    # Create database
    createdb veke_db

    # Or using psql
    psql -U postgres -c "CREATE DATABASE veke_db;"
    ```

    Configure `.env`:
    ```env
    DB_DRIVER=postgresql
    DATABASE_URL=postgresql://postgres:password@localhost:5432/veke_db
    ```

=== "MySQL"

    ```bash
    # Login to MySQL
    mysql -u root -p

    # Create database
    CREATE DATABASE veke_db;
    exit;
    ```

    Configure `.env`:
    ```env
    DB_DRIVER=mysql
    DATABASE_URL=mysql://root:password@localhost:3306/veke_db
    ```

### 5. Run Migrations

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 6. Verify Installation

```bash
# List CLI commands
python cli.py list

# Start development server
python cli.py serve
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see the API documentation.

## Platform-Specific Notes

### macOS

If you encounter issues with `mysqlclient`:

```bash
# Install MySQL development headers
brew install mysql

# Add to PATH
export PATH="/usr/local/opt/mysql/bin:$PATH"

# Then install
pip install mysqlclient
```

### Linux (Ubuntu/Debian)

```bash
# PostgreSQL development headers
sudo apt-get install libpq-dev

# MySQL development headers
sudo apt-get install libmysqlclient-dev
```

### Windows

!!! warning "Windows Users"
    We recommend using WSL (Windows Subsystem for Linux) for the best experience.

    ```powershell
    # Install WSL
    wsl --install

    # Then follow Linux instructions
    ```

## Troubleshooting

### Common Issues

??? question "Error: `No module named 'greenlet'`"
    ```bash
    pip install greenlet==3.2.4
    ```

??? question "Error: `bcrypt` module issues"
    ```bash
    pip install bcrypt==4.2.1 passlib==1.7.4
    ```

??? question "Error: `psycopg2` installation fails"
    ```bash
    # macOS
    brew install postgresql

    # Linux
    sudo apt-get install libpq-dev

    pip install psycopg2-binary
    ```

??? question "Error: `mysqlclient` installation fails"
    ```bash
    # macOS
    brew install mysql

    # Linux
    sudo apt-get install libmysqlclient-dev

    pip install mysqlclient
    ```

### View Setup Logs

If installation fails, check the setup log:

```bash
cat setup.log
```

## Next Steps

Once installed, proceed to:

- [Quick Start Guide](quickstart.md) - Create your first resource
- [Configuration](configuration.md) - Configure your application
- [CLI Commands](../commands/overview.md) - Explore all commands
