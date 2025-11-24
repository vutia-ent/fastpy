#!/bin/bash

# VE.KE API Setup Script
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

    if [ "$db_type" = "postgresql" ]; then
        if psql -U postgres -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw "$db_name"; then
            return 0
        fi
    elif [ "$db_type" = "mysql" ]; then
        if mysql -e "USE $db_name" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

# Create database if it doesn't exist
create_database() {
    local db_type=$1
    local db_name=$2

    print_info "Creating database '$db_name'..."

    if [ "$db_type" = "postgresql" ]; then
        if createdb -U postgres "$db_name" 2>/dev/null; then
            print_success "Database '$db_name' created successfully"
            return 0
        else
            print_warning "Could not create database. You may need to create it manually."
            return 1
        fi
    elif [ "$db_type" = "mysql" ]; then
        if mysql -e "CREATE DATABASE IF NOT EXISTS $db_name" 2>/dev/null; then
            print_success "Database '$db_name' created successfully"
            return 0
        else
            print_warning "Could not create database. You may need to create it manually."
            return 1
        fi
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
    echo "=== VE.KE API Setup Log - $(date) ===" > "$LOG_FILE"

    print_header "VE.KE API Setup"
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
        read -p "Do you want to recreate it? (y/n): " recreate_venv
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

    # Install dependencies
    print_step "Step 4: Installing dependencies"
    print_info "This may take a few minutes..."

    if pip install -r requirements.txt >> "$LOG_FILE" 2>&1; then
        print_success "Core dependencies installed"
    else
        print_error "Failed to install dependencies. Check $LOG_FILE for details."
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
    print_step "Step 5: Configuring environment"
    if [ -f ".env" ]; then
        print_warning ".env file already exists."
        read -p "Do you want to reconfigure it? (y/n): " reconfig_env
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
        # Database configuration
        print_header "Database Configuration"
        echo "Which database would you like to use?"
        echo "1) PostgreSQL (recommended for production)"
        echo "2) MySQL"
        echo "3) Skip database configuration"
        read -p "Enter your choice (1-3): " db_choice

        if [ "$db_choice" = "1" ]; then
            DB_DRIVER="postgresql"
            DB_NAME="veke_db"
            DEFAULT_URL="postgresql://postgres:password@localhost:5432/$DB_NAME"
            print_info "PostgreSQL selected"

            # Check if PostgreSQL is installed
            if ! command_exists psql; then
                print_warning "PostgreSQL client not found. Please install PostgreSQL."
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

        elif [ "$db_choice" = "2" ]; then
            DB_DRIVER="mysql"
            DB_NAME="veke_db"
            DEFAULT_URL="mysql://root:password@localhost:3306/$DB_NAME"
            print_info "MySQL selected"

            # Check if MySQL is installed
            if ! command_exists mysql; then
                print_warning "MySQL client not found. Please install MySQL."
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

        elif [ "$db_choice" = "3" ]; then
            print_info "Skipping database configuration"
            SKIP_DB_SETUP=true
        else
            print_warning "Invalid choice. Defaulting to PostgreSQL."
            DB_DRIVER="postgresql"
            DB_NAME="veke_db"
            DEFAULT_URL="postgresql://postgres:password@localhost:5432/$DB_NAME"
        fi

        if [ "$SKIP_DB_SETUP" != "true" ]; then
            # Database name
            read -p "Enter database name (default: $DB_NAME): " custom_db_name
            if [ ! -z "$custom_db_name" ]; then
                DB_NAME="$custom_db_name"
                DEFAULT_URL=$(echo "$DEFAULT_URL" | sed "s|/[^/?]*$|/$DB_NAME|")
            fi

            # Database URL
            echo ""
            echo "Enter your database URL"
            echo "Default: $DEFAULT_URL"
            read -p "Database URL (or press Enter for default): " db_url
            if [ -z "$db_url" ]; then
                db_url=$DEFAULT_URL
            fi

            # Update .env file
            if [ -f ".env" ]; then
                # macOS compatible sed
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
            if check_database_exists "$DB_DRIVER" "$DB_NAME"; then
                print_success "Database '$DB_NAME' already exists"
            else
                print_warning "Database '$DB_NAME' does not exist"
                read -p "Do you want to create it now? (y/n): " create_db
                if [ "$create_db" = "y" ] || [ "$create_db" = "Y" ]; then
                    create_database "$DB_DRIVER" "$DB_NAME"
                fi
            fi
        fi

        # Generate secret key
        print_step "Step 6: Generating secret key"
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
        read -p "Do you want to run database migrations now? (y/n): " run_migrations

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
    fi

    # Setup pre-commit hooks (optional)
    print_header "Code Quality Setup"
    read -p "Do you want to set up pre-commit hooks? (y/n): " setup_precommit
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

    # Setup complete
    print_header "Setup Complete!"
    echo ""
    echo -e "${GREEN}✓${NC} Your VE.KE API is ready to use!"
    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo "  1. Review .env file and update database credentials if needed"
    if [ "$run_migrations" != "y" ] && [ "$run_migrations" != "Y" ]; then
        echo "  2. Run database migrations: ${YELLOW}alembic upgrade head${NC}"
    fi
    echo "  3. Start the development server: ${YELLOW}uvicorn main:app --reload${NC}"
    echo "  4. Visit API docs: ${BLUE}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${CYAN}Useful Commands:${NC}"
    echo "  ${YELLOW}python cli.py make:resource Post -m${NC}  - Generate model, controller & routes"
    echo "  ${YELLOW}pytest${NC}                               - Run tests"
    echo "  ${YELLOW}black .${NC}                              - Format code"
    echo "  ${YELLOW}ruff check .${NC}                         - Lint code"
    echo ""
    echo -e "${CYAN}Documentation:${NC}"
    echo "  - README.md - Complete setup and usage guide"
    echo "  - API Docs - http://localhost:8000/docs (after starting server)"
    echo ""
    print_success "Setup completed successfully!"
    print_info "Log saved to: $LOG_FILE"
}

# Run main function
main
