#!/bin/bash

# Fastpy Setup Script
# This script automates the setup process for the FastAPI starter template

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/setup.log"

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "[INFO] $1" >> "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "[SUCCESS] $1" >> "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "[WARNING] $1" >> "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[ERROR] $1" >> "$LOG_FILE"
}

print_header() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  $1${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

print_step() {
    echo -e "${CYAN}➜${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version compatibility
check_python_version() {
    local version=$1
    local major=$(echo "$version" | cut -d. -f1)
    local minor=$(echo "$version" | cut -d. -f2)

    if [ "$major" -eq 3 ] && [ "$minor" -ge 9 ]; then
        return 0
    else
        return 1
    fi
}

# Check if database server is running
check_database_server() {
    local db_type=$1

    if [ "$db_type" = "postgresql" ]; then
        if command_exists psql; then
            if psql -U postgres -c "SELECT 1" >/dev/null 2>&1 || \
               psql -h localhost -c "SELECT 1" >/dev/null 2>&1; then
                return 0
            fi
        fi
        return 1
    elif [ "$db_type" = "mysql" ]; then
        if command_exists mysql; then
            if mysql -e "SELECT 1" >/dev/null 2>&1; then
                return 0
            fi
        fi
        return 1
    fi
    return 1
}

# Extract database name from URL
extract_db_name() {
    local url=$1
    echo "$url" | sed -E 's|.*[:/]([^/?]+)(\?.*)?$|\1|'
}

# Check if database exists
check_database_exists() {
    local db_type=$1
    local db_name=$2
    local db_host=$3
    local db_port=$4
    local db_user=$5
    local db_pass=$6

    if [ "$db_type" = "postgresql" ]; then
        if [ -z "$db_pass" ]; then
            if psql -h "$db_host" -p "$db_port" -U "$db_user" -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw "$db_name"; then
                return 0
            fi
        else
            if PGPASSWORD="$db_pass" psql -h "$db_host" -p "$db_port" -U "$db_user" -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw "$db_name"; then
                return 0
            fi
        fi
    elif [ "$db_type" = "mysql" ]; then
        if [ -z "$db_pass" ]; then
            if mysql -h "$db_host" -P "$db_port" -u "$db_user" -e "USE $db_name" 2>/dev/null; then
                return 0
            fi
        else
            if mysql -h "$db_host" -P "$db_port" -u "$db_user" -p"$db_pass" -e "USE $db_name" 2>/dev/null; then
                return 0
            fi
        fi
    fi
    return 1
}

# Create database if it doesn't exist
create_database() {
    local db_type=$1
    local db_name=$2
    local db_host=$3
    local db_port=$4
    local db_user=$5
    local db_pass=$6

    print_info "Creating database '$db_name'..."

    if [ "$db_type" = "postgresql" ]; then
        if [ -z "$db_pass" ]; then
            if createdb -h "$db_host" -p "$db_port" -U "$db_user" "$db_name" 2>/dev/null; then
                print_success "Database '$db_name' created successfully"
                return 0
            fi
        else
            if PGPASSWORD="$db_pass" createdb -h "$db_host" -p "$db_port" -U "$db_user" "$db_name" 2>/dev/null; then
                print_success "Database '$db_name' created successfully"
                return 0
            fi
        fi
        print_warning "Could not create database. You may need to create it manually."
        return 1
    elif [ "$db_type" = "mysql" ]; then
        if [ -z "$db_pass" ]; then
            if mysql -h "$db_host" -P "$db_port" -u "$db_user" -e "CREATE DATABASE IF NOT EXISTS \`$db_name\`" 2>/dev/null; then
                print_success "Database '$db_name' created successfully"
                return 0
            fi
        else
            if mysql -h "$db_host" -P "$db_port" -u "$db_user" -p"$db_pass" -e "CREATE DATABASE IF NOT EXISTS \`$db_name\`" 2>/dev/null; then
                print_success "Database '$db_name' created successfully"
                return 0
            fi
        fi
        print_warning "Could not create database. You may need to create it manually."
        return 1
    fi
}

# Cleanup function for errors
cleanup_on_error() {
    print_error "Setup failed! Check $LOG_FILE for details."
    exit 1
}

trap cleanup_on_error ERR

# Main setup function
main() {
    # Initialize log file
    echo "=== Fastpy Setup Log - $(date) ===" > "$LOG_FILE"

    print_header "Fastpy Setup"
    print_info "Log file: $LOG_FILE"

    # Check if running in project directory
    if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ]; then
        print_error "Please run this script from the project root directory."
        exit 1
    fi

    # Check Python version
    print_step "Step 1: Checking Python version"
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.9 or higher."
        echo "Visit: https://www.python.org/downloads/"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    if check_python_version "$PYTHON_VERSION"; then
        print_success "Python $PYTHON_VERSION found (compatible)"
    else
        print_error "Python 3.9+ required, but found $PYTHON_VERSION"
        exit 1
    fi

    # Create virtual environment
    print_step "Step 2: Setting up virtual environment"
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists."
        read -p "Do you want to recreate it? [y/N]: " recreate_venv
        recreate_venv=${recreate_venv:-n}
        if [ "$recreate_venv" = "y" ] || [ "$recreate_venv" = "Y" ]; then
            print_info "Removing existing virtual environment..."
            rm -rf venv
            python3 -m venv venv
            print_success "Virtual environment recreated"
        else
            print_info "Using existing virtual environment"
        fi
    else
        python3 -m venv venv
        print_success "Virtual environment created"
    fi

    # Activate virtual environment
    print_info "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"

    # Upgrade pip
    print_step "Step 3: Upgrading pip"
    if pip install --upgrade pip >> "$LOG_FILE" 2>&1; then
        print_success "pip upgraded to $(pip --version | cut -d' ' -f2)"
    else
        print_warning "Could not upgrade pip, continuing anyway..."
    fi

    # Database selection (ask early to install only needed dependencies)
    print_step "Step 4: Select database"
    echo ""
    echo "Which database will you use?"
    echo "  1) MySQL (recommended)"
    echo "  2) PostgreSQL"
    echo "  3) SQLite (for development/testing only)"
    echo ""
    read -p "Enter your choice [1-3] (default: 1): " db_choice
    db_choice=${db_choice:-1}

    case $db_choice in
        1)
            DB_DRIVER="mysql"
            DB_PACKAGE="mysqlclient pymysql"
            print_success "MySQL selected"
            ;;
        2)
            DB_DRIVER="postgresql"
            DB_PACKAGE="psycopg2-binary"
            print_success "PostgreSQL selected"
            ;;
        3)
            DB_DRIVER="sqlite"
            DB_PACKAGE="aiosqlite"
            print_success "SQLite selected"
            ;;
        *)
            print_warning "Invalid choice. Defaulting to MySQL."
            DB_DRIVER="mysql"
            DB_PACKAGE="mysqlclient pymysql"
            ;;
    esac

    # Install dependencies
    print_step "Step 5: Installing dependencies"
    print_info "This may take a few minutes..."

    # Handle platform-specific dependencies for macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command_exists brew; then
            # Install database-specific dependencies
            if [ "$DB_DRIVER" = "postgresql" ]; then
                if ! command_exists pg_config; then
                    print_info "Installing PostgreSQL client via Homebrew..."
                    if brew install libpq >> "$LOG_FILE" 2>&1; then
                        print_success "PostgreSQL client installed"
                    else
                        print_warning "Could not install libpq automatically."
                        print_info "Run manually: brew install libpq"
                    fi
                fi
                # Set paths for psycopg2 compilation
                if [ -d "/opt/homebrew/opt/libpq/bin" ]; then
                    export PATH="/opt/homebrew/opt/libpq/bin:$PATH"
                    export LDFLAGS="-L/opt/homebrew/opt/libpq/lib"
                    export CPPFLAGS="-I/opt/homebrew/opt/libpq/include"
                elif [ -d "/usr/local/opt/libpq/bin" ]; then
                    export PATH="/usr/local/opt/libpq/bin:$PATH"
                    export LDFLAGS="-L/usr/local/opt/libpq/lib"
                    export CPPFLAGS="-I/usr/local/opt/libpq/include"
                fi
            elif [ "$DB_DRIVER" = "mysql" ]; then
                if ! brew list mysql-client &>/dev/null && ! brew list mysql &>/dev/null; then
                    print_info "Installing MySQL client via Homebrew..."
                    if brew install mysql-client >> "$LOG_FILE" 2>&1; then
                        print_success "MySQL client installed"
                    else
                        print_warning "Could not install mysql-client automatically."
                        print_info "Run manually: brew install mysql-client"
                    fi
                fi
                # Set paths for mysqlclient compilation
                if [ -d "/opt/homebrew/opt/mysql-client/bin" ]; then
                    export PATH="/opt/homebrew/opt/mysql-client/bin:$PATH"
                    export LDFLAGS="-L/opt/homebrew/opt/mysql-client/lib"
                    export CPPFLAGS="-I/opt/homebrew/opt/mysql-client/include"
                elif [ -d "/usr/local/opt/mysql-client/bin" ]; then
                    export PATH="/usr/local/opt/mysql-client/bin:$PATH"
                    export LDFLAGS="-L/usr/local/opt/mysql-client/lib"
                    export CPPFLAGS="-I/usr/local/opt/mysql-client/include"
                fi
            fi
            # SQLite needs no additional dependencies on macOS
        else
            if [ "$DB_DRIVER" != "sqlite" ]; then
                print_warning "Homebrew not found. You may need to install database dependencies manually."
                print_info "Install Homebrew: https://brew.sh"
            fi
        fi
    fi

    # Install core dependencies (without database drivers)
    print_info "Installing core dependencies..."
    if pip install --default-timeout=120 greenlet bcrypt passlib >> "$LOG_FILE" 2>&1; then
        print_success "Critical dependencies installed"
    else
        print_warning "Some critical dependencies may have issues. Check $LOG_FILE"
    fi

    # Create a temporary requirements file without database-specific packages
    print_info "Installing main dependencies..."
    grep -v "psycopg2\|mysqlclient\|pymysql\|aiosqlite" requirements.txt > /tmp/requirements_core.txt 2>/dev/null || cp requirements.txt /tmp/requirements_core.txt

    if pip install --default-timeout=120 -r /tmp/requirements_core.txt >> "$LOG_FILE" 2>&1; then
        print_success "Core dependencies installed"
    else
        print_error "Failed to install core dependencies. Check $LOG_FILE for details."
        exit 1
    fi

    # Install selected database driver
    print_info "Installing $DB_DRIVER database driver..."
    if pip install --default-timeout=120 $DB_PACKAGE >> "$LOG_FILE" 2>&1; then
        print_success "$DB_DRIVER driver installed ($DB_PACKAGE)"
    else
        print_error "Failed to install $DB_DRIVER driver."
        if [ "$DB_DRIVER" = "postgresql" ]; then
            print_info "Fix: brew install libpq && pip install psycopg2-binary"
        elif [ "$DB_DRIVER" = "mysql" ]; then
            print_info "Fix: brew install mysql-client && pip install mysqlclient"
        fi
        exit 1
    fi

    # Install dev dependencies
    print_info "Installing dev dependencies..."
    if pip install -e ".[dev]" >> "$LOG_FILE" 2>&1; then
        print_success "Dev dependencies installed"
    else
        print_warning "Failed to install dev dependencies. You can install them later with: pip install -e \".[dev]\""
    fi

    # Setup .env file
    print_step "Step 6: Configuring environment"
    if [ -f ".env" ]; then
        print_warning ".env file already exists."
        read -p "Do you want to reconfigure it? [y/N]: " reconfig_env
        reconfig_env=${reconfig_env:-n}
        if [ "$reconfig_env" = "y" ] || [ "$reconfig_env" = "Y" ]; then
            mv .env .env.backup.$(date +%s)
            print_info "Existing .env backed up"
            cp .env.example .env
        else
            print_info "Keeping existing .env file"
            SKIP_ENV_CONFIG=true
        fi
    else
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success ".env file created from .env.example"
        else
            print_error ".env.example not found!"
            exit 1
        fi
    fi

    if [ "$SKIP_ENV_CONFIG" != "true" ]; then
        # Database configuration (using selection from Step 4)
        print_header "Database Configuration"

        DB_NAME="fastpy_db"

        if [ "$DB_DRIVER" = "postgresql" ]; then
            DEFAULT_URL="postgresql://postgres:password@localhost:5432/$DB_NAME"

            # Check if PostgreSQL is installed
            if ! command_exists psql; then
                print_warning "PostgreSQL client not found."
                print_info "macOS: brew install postgresql"
                print_info "Ubuntu: sudo apt-get install postgresql-client"
            else
                if check_database_server "postgresql"; then
                    print_success "PostgreSQL server is running"
                else
                    print_warning "PostgreSQL server may not be running"
                    print_info "macOS: brew services start postgresql"
                    print_info "Linux: sudo service postgresql start"
                fi
            fi

        elif [ "$DB_DRIVER" = "mysql" ]; then
            DEFAULT_URL="mysql://root:password@localhost:3306/$DB_NAME"

            # Check if MySQL is installed
            if ! command_exists mysql; then
                print_warning "MySQL client not found."
                print_info "macOS: brew install mysql"
                print_info "Ubuntu: sudo apt-get install mysql-client"
            else
                if check_database_server "mysql"; then
                    print_success "MySQL server is running"
                else
                    print_warning "MySQL server may not be running"
                    print_info "macOS: mysql.server start or brew services start mysql"
                    print_info "Linux: sudo service mysql start"
                fi
            fi

        elif [ "$DB_DRIVER" = "sqlite" ]; then
            DEFAULT_URL="sqlite:///./fastpy.db"
            print_info "SQLite will create a local database file: fastpy.db"
        fi

        if [ "$DB_DRIVER" = "sqlite" ]; then
            # SQLite - just set the URL
            db_url=$DEFAULT_URL

            # Update .env file
            if [ -f ".env" ]; then
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    sed -i '' "s|^DB_DRIVER=.*|DB_DRIVER=$DB_DRIVER|" .env
                    sed -i '' "s|^DATABASE_URL=.*|DATABASE_URL=$db_url|" .env
                else
                    sed -i "s|^DB_DRIVER=.*|DB_DRIVER=$DB_DRIVER|" .env
                    sed -i "s|^DATABASE_URL=.*|DATABASE_URL=$db_url|" .env
                fi
                print_success "SQLite configuration saved to .env"
            fi
        else
            # PostgreSQL or MySQL
            echo ""
            echo "Configure database connection:"
            echo ""

            # Database host
            if [ "$DB_DRIVER" = "postgresql" ]; then
                DEFAULT_HOST="localhost"
                DEFAULT_PORT="5432"
                DEFAULT_USER="postgres"
            else
                DEFAULT_HOST="localhost"
                DEFAULT_PORT="3306"
                DEFAULT_USER="root"
            fi

            read -p "Database host (default: $DEFAULT_HOST): " db_host
            db_host=${db_host:-$DEFAULT_HOST}

            read -p "Database port (default: $DEFAULT_PORT): " db_port
            db_port=${db_port:-$DEFAULT_PORT}

            read -p "Database username (default: $DEFAULT_USER): " db_user
            db_user=${db_user:-$DEFAULT_USER}

            read -sp "Database password: " db_password
            echo ""

            read -p "Database name (default: $DB_NAME): " custom_db_name
            if [ ! -z "$custom_db_name" ]; then
                DB_NAME="$custom_db_name"
            fi

            # Build database URL
            if [ -z "$db_password" ]; then
                db_url="$DB_DRIVER://$db_user@$db_host:$db_port/$DB_NAME"
            else
                db_url="$DB_DRIVER://$db_user:$db_password@$db_host:$db_port/$DB_NAME"
            fi

            echo ""
            print_info "Database URL: $DB_DRIVER://$db_user:****@$db_host:$db_port/$DB_NAME"

            # Update .env file
            if [ -f ".env" ]; then
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    sed -i '' "s|^DB_DRIVER=.*|DB_DRIVER=$DB_DRIVER|" .env
                    sed -i '' "s|^DATABASE_URL=.*|DATABASE_URL=$db_url|" .env
                else
                    sed -i "s|^DB_DRIVER=.*|DB_DRIVER=$DB_DRIVER|" .env
                    sed -i "s|^DATABASE_URL=.*|DATABASE_URL=$db_url|" .env
                fi
                print_success "Database configuration saved to .env"
            fi

            # Check if database exists
            if check_database_exists "$DB_DRIVER" "$DB_NAME" "$db_host" "$db_port" "$db_user" "$db_password"; then
                print_success "Database '$DB_NAME' already exists"
            else
                print_warning "Database '$DB_NAME' does not exist"
                read -p "Do you want to create it now? [Y/n]: " create_db
                create_db=${create_db:-y}
                if [ "$create_db" = "y" ] || [ "$create_db" = "Y" ]; then
                    create_database "$DB_DRIVER" "$DB_NAME" "$db_host" "$db_port" "$db_user" "$db_password"
                fi
            fi
        fi

        # Generate secret key
        print_step "Step 7: Generating secret key"
        if command_exists openssl; then
            SECRET_KEY=$(openssl rand -hex 32)
            if [ -f ".env" ]; then
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    sed -i '' "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
                else
                    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
                fi
                print_success "Secure secret key generated and saved"
            fi
        else
            print_warning "openssl not found. Using default secret key."
            print_warning "IMPORTANT: Update SECRET_KEY in .env before deploying to production!"
        fi
    fi

    # Database migration
    if [ "$SKIP_DB_SETUP" != "true" ]; then
        print_header "Database Migration"
        read -p "Do you want to run database migrations now? [Y/n]: " run_migrations
        run_migrations=${run_migrations:-y}

        if [ "$run_migrations" = "y" ] || [ "$run_migrations" = "Y" ]; then
            # Check if migrations exist
            if [ ! -d "alembic/versions" ] || [ -z "$(ls -A alembic/versions 2>/dev/null)" ]; then
                print_info "Generating initial migration..."
                if alembic revision --autogenerate -m "Initial migration" >> "$LOG_FILE" 2>&1; then
                    print_success "Initial migration generated"
                else
                    print_error "Failed to generate migration. Check $LOG_FILE"
                fi
            else
                print_info "Migrations already exist"
            fi

            # Run migrations
            print_info "Running database migrations..."
            if alembic upgrade head >> "$LOG_FILE" 2>&1; then
                print_success "Database migrations completed successfully"
            else
                print_error "Migration failed. Please check:"
                print_info "1. Database server is running"
                print_info "2. Database credentials in .env are correct"
                print_info "3. Database exists"
                print_info "Check $LOG_FILE for detailed error information"
            fi
        else
            print_info "Skipping migrations. Run 'alembic upgrade head' when ready."
        fi

        # Create super admin user
        if [ "$run_migrations" = "y" ] || [ "$run_migrations" = "Y" ]; then
            echo ""
            read -p "Do you want to create a super admin user? [Y/n]: " create_admin
            create_admin=${create_admin:-y}
            if [ "$create_admin" = "y" ] || [ "$create_admin" = "Y" ]; then
                print_header "Create Super Admin User"

                read -p "Admin name (default: Admin): " admin_name
                admin_name=${admin_name:-Admin}

                read -p "Admin email: " admin_email
                while [ -z "$admin_email" ]; do
                    print_warning "Email is required"
                    read -p "Admin email: " admin_email
                done

                read -sp "Admin password (min 8 chars): " admin_password
                echo ""
                while [ ${#admin_password} -lt 8 ]; do
                    print_warning "Password must be at least 8 characters"
                    read -sp "Admin password (min 8 chars): " admin_password
                    echo ""
                done

                # Create admin user via Python
                print_info "Creating super admin user..."
                if python -c "
import asyncio
from app.database.connection import get_session, engine
from app.models.user import User
from app.utils.auth import get_password_hash
from sqlmodel import select
from datetime import datetime, timezone

async def create_admin():
    async with engine.begin() as conn:
        pass

    from sqlalchemy.ext.asyncio import AsyncSession
    async with AsyncSession(engine) as session:
        # Check if user already exists
        result = await session.execute(select(User).where(User.email == '$admin_email'))
        existing = result.scalar_one_or_none()

        if existing:
            print('User with this email already exists')
            return False

        # Create user
        user = User(
            name='$admin_name',
            email='$admin_email',
            password=get_password_hash('$admin_password'),
            email_verified_at=datetime.now(timezone.utc).isoformat()
        )
        session.add(user)
        await session.commit()
        print(f'Super admin created: $admin_email')
        return True

asyncio.run(create_admin())
" >> "$LOG_FILE" 2>&1; then
                    print_success "Super admin user created: $admin_email"
                else
                    print_error "Failed to create admin user. Check $LOG_FILE"
                fi
            fi
        fi
    fi

    # Setup pre-commit hooks (optional)
    print_header "Code Quality Setup"
    read -p "Do you want to set up pre-commit hooks? [Y/n]: " setup_precommit
    setup_precommit=${setup_precommit:-y}
    if [ "$setup_precommit" = "y" ] || [ "$setup_precommit" = "Y" ]; then
        if command_exists git && [ -d ".git" ]; then
            print_info "Installing pre-commit hooks..."
            if pre-commit install >> "$LOG_FILE" 2>&1; then
                print_success "Pre-commit hooks installed"
            else
                print_warning "Failed to install pre-commit hooks"
            fi
        else
            print_warning "Not a git repository. Skipping pre-commit setup."
        fi
    fi

    # Test installation
    print_header "Verifying Installation"
    print_info "Running quick verification..."

    if python -c "import fastapi; import sqlmodel; import alembic" 2>/dev/null; then
        print_success "Core packages verified"
    else
        print_warning "Some core packages may not be installed correctly"
    fi

    # AI Assistant Configuration
    print_header "AI Assistant Configuration"
    echo ""
    echo -e "${CYAN}Select an AI assistant to configure (optional):${NC}"
    echo "  1) Claude (CLAUDE.md)"
    echo "  2) GitHub Copilot (.github/copilot-instructions.md)"
    echo "  3) Cursor (.cursorrules)"
    echo "  4) Google Gemini (.gemini/instructions.md)"
    echo "  5) Skip"
    echo ""
    read -p "Select option [1-5] (default: 5): " ai_choice
    ai_choice=${ai_choice:-5}

    case $ai_choice in
        1)
            print_info "Generating Claude configuration..."
            python cli.py init:ai claude 2>/dev/null || fastpy init:ai claude
            ;;
        2)
            print_info "Generating GitHub Copilot configuration..."
            python cli.py init:ai copilot 2>/dev/null || fastpy init:ai copilot
            ;;
        3)
            print_info "Generating Cursor configuration..."
            python cli.py init:ai cursor 2>/dev/null || fastpy init:ai cursor
            ;;
        4)
            print_info "Generating Gemini configuration..."
            python cli.py init:ai gemini 2>/dev/null || fastpy init:ai gemini
            ;;
        5)
            print_info "Skipping AI assistant configuration"
            echo -e "  You can configure later with: ${YELLOW}fastpy init:ai${NC}"
            ;;
        *)
            print_info "Skipping AI assistant configuration"
            ;;
    esac

    # Setup complete
    print_header "Setup Complete!"
    echo ""
    echo -e "${GREEN}✓${NC} Your Fastpy project is ready to use!"
    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo -e "  1. Activate virtual environment: ${YELLOW}source venv/bin/activate${NC}"
    if [ "$run_migrations" != "y" ] && [ "$run_migrations" != "Y" ]; then
        echo -e "  2. Run database migrations: ${YELLOW}alembic upgrade head${NC}"
    fi
    echo -e "  3. Start the development server:"
    echo -e "     ${YELLOW}fastpy serve${NC}"
    echo -e "     Or: ${YELLOW}uvicorn main:app --reload${NC}"
    echo -e "  4. Visit API docs: ${BLUE}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${CYAN}Useful Commands:${NC}"
    echo -e "  ${YELLOW}fastpy make:resource Post -m${NC}  - Generate model, controller & routes"
    echo -e "  ${YELLOW}pytest${NC}                               - Run tests"
    echo -e "  ${YELLOW}black .${NC}                              - Format code"
    echo -e "  ${YELLOW}ruff check .${NC}                         - Lint code"
    echo ""
    echo -e "${CYAN}Documentation:${NC}"
    echo -e "  - README.md - Complete setup and usage guide"
    echo -e "  - API Docs - http://localhost:8000/docs (after starting server)"
    echo ""
    print_success "Setup completed successfully!"
    print_info "Log saved to: $LOG_FILE"
}

# Run main function
main
