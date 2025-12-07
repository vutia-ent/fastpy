"""
Fastpy Setup CLI Commands.

Provides interactive project setup, database configuration, secret generation,
admin user creation, and pre-commit hooks installation.
"""
import os
import sys
import secrets
import subprocess
import asyncio
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@dataclass
class DatabaseConfig:
    """Database configuration."""
    driver: str
    host: str
    port: int
    username: str
    password: str
    database: str

    @property
    def url(self) -> str:
        """Generate database URL."""
        if self.driver == "sqlite":
            return f"sqlite:///./{self.database}.db"

        if self.password:
            return f"{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        return f"{self.driver}://{self.username}@{self.host}:{self.port}/{self.database}"

    @property
    def masked_url(self) -> str:
        """URL with masked password for display."""
        if self.driver == "sqlite":
            return self.url
        if self.password:
            return f"{self.driver}://{self.username}:****@{self.host}:{self.port}/{self.database}"
        return self.url


def check_command_exists(cmd: str) -> bool:
    """Check if a command exists in PATH."""
    try:
        subprocess.run(
            ["which", cmd],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def run_command(cmd: list, capture: bool = True, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        check=check
    )


def get_env_path() -> Path:
    """Get .env file path."""
    return Path.cwd() / ".env"


def read_env() -> dict:
    """Read .env file into dict."""
    env_path = get_env_path()
    env_vars = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def update_env(key: str, value: str):
    """Update a single key in .env file."""
    env_path = get_env_path()

    if not env_path.exists():
        # Copy from .env.example if exists
        example_path = Path.cwd() / ".env.example"
        if example_path.exists():
            env_path.write_text(example_path.read_text())
        else:
            env_path.write_text("")

    content = env_path.read_text()
    lines = content.split("\n")
    key_found = False

    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            key_found = True
            break

    if not key_found:
        lines.append(f"{key}={value}")

    env_path.write_text("\n".join(lines))


def check_database_server(driver: str) -> Tuple[bool, str]:
    """Check if database server is running."""
    if driver == "postgresql":
        if check_command_exists("psql"):
            try:
                result = run_command(["psql", "-U", "postgres", "-c", "SELECT 1"], check=False)
                if result.returncode == 0:
                    return True, "PostgreSQL server is running"
                # Try with localhost
                result = run_command(["psql", "-h", "localhost", "-c", "SELECT 1"], check=False)
                if result.returncode == 0:
                    return True, "PostgreSQL server is running"
            except Exception:
                pass
        return False, "PostgreSQL server may not be running"

    elif driver == "mysql":
        if check_command_exists("mysql"):
            try:
                result = run_command(["mysql", "-e", "SELECT 1"], check=False)
                if result.returncode == 0:
                    return True, "MySQL server is running"
            except Exception:
                pass
        return False, "MySQL server may not be running"

    return True, "SQLite requires no server"


def check_database_exists(config: DatabaseConfig) -> bool:
    """Check if database exists."""
    if config.driver == "sqlite":
        return Path(f"{config.database}.db").exists()

    if config.driver == "postgresql":
        cmd = ["psql", "-h", config.host, "-p", str(config.port), "-U", config.username, "-lqt"]
        env = os.environ.copy()
        if config.password:
            env["PGPASSWORD"] = config.password
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)
            return config.database in result.stdout
        except Exception:
            return False

    elif config.driver == "mysql":
        cmd = ["mysql", "-h", config.host, "-P", str(config.port), "-u", config.username]
        if config.password:
            cmd.append(f"-p{config.password}")
        cmd.extend(["-e", f"USE {config.database}"])
        try:
            result = subprocess.run(cmd, capture_output=True, check=False)
            return result.returncode == 0
        except Exception:
            return False

    return False


def create_database(config: DatabaseConfig) -> bool:
    """Create database if it doesn't exist."""
    if config.driver == "sqlite":
        return True  # SQLite creates automatically

    console.print(f"[blue]Creating database '{config.database}'...[/blue]")

    if config.driver == "postgresql":
        cmd = ["createdb", "-h", config.host, "-p", str(config.port), "-U", config.username, config.database]
        env = os.environ.copy()
        if config.password:
            env["PGPASSWORD"] = config.password
        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)
            console.print(f"[green]✓[/green] Database '{config.database}' created successfully")
            return True
        except subprocess.CalledProcessError:
            console.print(f"[yellow]⚠[/yellow] Could not create database. You may need to create it manually.")
            return False

    elif config.driver == "mysql":
        cmd = ["mysql", "-h", config.host, "-P", str(config.port), "-u", config.username]
        if config.password:
            cmd.append(f"-p{config.password}")
        cmd.extend(["-e", f"CREATE DATABASE IF NOT EXISTS `{config.database}`"])
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            console.print(f"[green]✓[/green] Database '{config.database}' created successfully")
            return True
        except subprocess.CalledProcessError:
            console.print(f"[yellow]⚠[/yellow] Could not create database. You may need to create it manually.")
            return False

    return False


# ============================================
# CLI Commands
# ============================================

def setup_db(
    driver: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    database: Optional[str] = None,
    create: bool = True,
    interactive: bool = True,
) -> DatabaseConfig:
    """
    Configure database connection.

    Supports MySQL, PostgreSQL, and SQLite.
    """
    console.print(Panel.fit(
        "[bold cyan]Database Configuration[/bold cyan]",
        border_style="cyan"
    ))

    # Database driver selection
    if not driver and interactive:
        console.print("\n[cyan]Select database driver:[/cyan]")
        console.print("  [1] MySQL (recommended)")
        console.print("  [2] PostgreSQL")
        console.print("  [3] SQLite (development only)")

        choice = Prompt.ask("\nChoice", default="1")
        driver_map = {"1": "mysql", "2": "postgresql", "3": "sqlite"}
        driver = driver_map.get(choice, "mysql")

    driver = driver or "mysql"
    console.print(f"[green]✓[/green] Selected: {driver}")

    # SQLite configuration
    if driver == "sqlite":
        database = database or Prompt.ask("Database file name", default="fastpy") if interactive else "fastpy"
        config = DatabaseConfig(
            driver=driver,
            host="",
            port=0,
            username="",
            password="",
            database=database
        )
        update_env("DB_DRIVER", driver)
        update_env("DATABASE_URL", config.url)
        console.print(f"[green]✓[/green] SQLite configured: {config.url}")
        return config

    # Default values per driver
    defaults = {
        "mysql": {"host": "localhost", "port": 3306, "username": "root"},
        "postgresql": {"host": "localhost", "port": 5432, "username": "postgres"},
    }

    d = defaults.get(driver, defaults["mysql"])

    # Check server status
    running, message = check_database_server(driver)
    if running:
        console.print(f"[green]✓[/green] {message}")
    else:
        console.print(f"[yellow]⚠[/yellow] {message}")
        if driver == "mysql":
            console.print("  [dim]Start with: mysql.server start or brew services start mysql[/dim]")
        else:
            console.print("  [dim]Start with: brew services start postgresql[/dim]")

    # Interactive configuration
    if interactive:
        console.print("\n[cyan]Configure connection:[/cyan]")
        host = Prompt.ask("Host", default=host or d["host"])
        port = int(Prompt.ask("Port", default=str(port or d["port"])))
        username = Prompt.ask("Username", default=username or d["username"])
        password = Prompt.ask("Password", password=True, default=password or "")
        database = Prompt.ask("Database name", default=database or "fastpy_db")
    else:
        host = host or d["host"]
        port = port or d["port"]
        username = username or d["username"]
        password = password or ""
        database = database or "fastpy_db"

    config = DatabaseConfig(
        driver=driver,
        host=host,
        port=port,
        username=username,
        password=password,
        database=database
    )

    # Update .env
    update_env("DB_DRIVER", driver)
    update_env("DATABASE_URL", config.url)
    console.print(f"\n[green]✓[/green] Database URL: {config.masked_url}")

    # Check/create database
    if check_database_exists(config):
        console.print(f"[green]✓[/green] Database '{config.database}' exists")
    elif create:
        if interactive:
            if Confirm.ask(f"Database '{config.database}' does not exist. Create it?", default=True):
                create_database(config)
        else:
            create_database(config)

    return config


def setup_secret(
    length: int = 64,
) -> str:
    """
    Generate a secure secret key for JWT tokens.

    Uses Python's secrets module for cryptographic randomness.
    """
    console.print(Panel.fit(
        "[bold cyan]Secret Key Generation[/bold cyan]",
        border_style="cyan"
    ))

    # Generate secret key
    secret_key = secrets.token_hex(length // 2)

    # Update .env
    update_env("SECRET_KEY", secret_key)

    console.print(f"[green]✓[/green] Secure secret key generated ({length} characters)")
    console.print(f"[dim]Key saved to .env[/dim]")

    return secret_key


async def create_admin_user(name: str, email: str, password: str) -> bool:
    """Create admin user in database."""
    try:
        # Suppress SQLAlchemy logging BEFORE importing engine
        import logging
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.WARNING)

        # Import here to avoid circular imports and ensure env is loaded
        from dotenv import load_dotenv
        load_dotenv()

        from app.database.connection import engine
        from app.models.user import User
        from app.utils.auth import get_password_hash
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlmodel import select
        from datetime import datetime, timezone

        async with AsyncSession(engine) as session:
            # Check if user exists
            result = await session.execute(select(User).where(User.email == email))
            existing = result.scalar_one_or_none()

            if existing:
                console.print(f"[yellow]⚠[/yellow] User with email '{email}' already exists")
                return False

            # Create user
            user = User(
                name=name,
                email=email,
                password=get_password_hash(password),
                email_verified_at=datetime.now(timezone.utc)
            )
            session.add(user)
            await session.commit()

            console.print(f"[green]✓[/green] Admin user created: {email}")
            return True

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create admin: {e}")
        return False


def setup_admin(
    name: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    interactive: bool = True,
    show_header: bool = True,
):
    """
    Create a super admin user.

    Requires database to be configured and migrations to be run.
    """
    if show_header:
        console.print(Panel.fit(
            "[bold cyan]Create Super Admin[/bold cyan]",
            border_style="cyan"
        ))

    # Interactive prompts
    if interactive:
        name = Prompt.ask("Admin name", default=name or "Admin")

        while not email:
            email = Prompt.ask("Admin email")
            if not email:
                console.print("[yellow]Email is required[/yellow]")

        while not password or len(password) < 8:
            password = Prompt.ask("Admin password (min 8 chars)", password=True)
            if len(password) < 8:
                console.print("[yellow]Password must be at least 8 characters[/yellow]")
    else:
        if not all([name, email, password]):
            console.print("[red]✗[/red] Name, email, and password are required in non-interactive mode")
            return False

    # Create user
    return asyncio.run(create_admin_user(name, email, password))


def setup_hooks():
    """
    Install pre-commit hooks for code quality.

    Requires git to be initialized and pre-commit to be installed.
    """
    console.print(Panel.fit(
        "[bold cyan]Pre-commit Hooks Setup[/bold cyan]",
        border_style="cyan"
    ))

    # Check if git is initialized
    if not Path(".git").exists():
        console.print("[yellow]⚠[/yellow] Not a git repository. Initialize with: git init")
        return False

    # Check if pre-commit is available
    if not check_command_exists("pre-commit"):
        console.print("[yellow]⚠[/yellow] pre-commit not found. Install with: pip install pre-commit")
        return False

    # Check if .pre-commit-config.yaml exists
    if not Path(".pre-commit-config.yaml").exists():
        console.print("[yellow]⚠[/yellow] .pre-commit-config.yaml not found")
        return False

    # Install hooks
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Installing pre-commit hooks...", total=None)
        try:
            run_command(["pre-commit", "install"])
            progress.update(task, completed=True)
            console.print("[green]✓[/green] Pre-commit hooks installed")
            return True
        except subprocess.CalledProcessError:
            progress.update(task, completed=True)
            console.print("[red]✗[/red] Failed to install pre-commit hooks")
            return False


def setup_env():
    """
    Initialize .env file from .env.example.

    Creates .env file if it doesn't exist.
    """
    console.print(Panel.fit(
        "[bold cyan]Environment Setup[/bold cyan]",
        border_style="cyan"
    ))

    env_path = get_env_path()
    example_path = Path.cwd() / ".env.example"

    if env_path.exists():
        console.print("[yellow]⚠[/yellow] .env file already exists")
        if Confirm.ask("Backup and recreate?", default=False):
            import time
            backup_path = env_path.with_suffix(f".backup.{int(time.time())}")
            env_path.rename(backup_path)
            console.print(f"[dim]Backed up to: {backup_path}[/dim]")
        else:
            console.print("[dim]Keeping existing .env[/dim]")
            return True

    if example_path.exists():
        env_path.write_text(example_path.read_text())
        console.print("[green]✓[/green] Created .env from .env.example")
        return True
    else:
        console.print("[red]✗[/red] .env.example not found")
        return False


def run_migrations(auto_generate: bool = True):
    """
    Run database migrations.

    Optionally auto-generates initial migration if none exist.
    """
    console.print(Panel.fit(
        "[bold cyan]Database Migrations[/bold cyan]",
        border_style="cyan"
    ))

    versions_dir = Path("alembic/versions")

    # Check if migrations exist
    has_migrations = versions_dir.exists() and any(versions_dir.glob("*.py"))

    if not has_migrations and auto_generate:
        console.print("[blue]Generating initial migration...[/blue]")
        try:
            run_command(["alembic", "revision", "--autogenerate", "-m", "Initial migration"])
            console.print("[green]✓[/green] Initial migration generated")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗[/red] Failed to generate migration: {e}")
            return False

    # Run migrations
    console.print("[blue]Running migrations...[/blue]")
    try:
        run_command(["alembic", "upgrade", "head"])
        console.print("[green]✓[/green] Migrations completed")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] Migration failed: {e}")
        console.print("\n[yellow]Please check:[/yellow]")
        console.print("  1. Database server is running")
        console.print("  2. Database credentials in .env are correct")
        console.print("  3. Database exists")
        return False


def upgrade_pip():
    """Upgrade pip to latest version."""
    console.print("[blue]Upgrading pip...[/blue]")
    try:
        run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=False)
        console.print("[green]✓[/green] pip upgraded")
        return True
    except subprocess.CalledProcessError:
        console.print("[yellow]⚠[/yellow] Could not upgrade pip (continuing anyway)")
        return False


def install_requirements():
    """Install project requirements."""
    requirements_path = Path("requirements.txt")
    if not requirements_path.exists():
        console.print("[yellow]⚠[/yellow] requirements.txt not found")
        return False

    console.print("[blue]Installing requirements...[/blue]")
    try:
        run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        console.print("[green]✓[/green] Requirements installed")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] Failed to install requirements: {e}")
        return False


def install_db_driver(driver: str):
    """Install database driver package."""
    packages = {
        "mysql": ["mysqlclient", "pymysql"],
        "postgresql": ["psycopg2-binary"],
        "sqlite": ["aiosqlite"],
    }

    driver_packages = packages.get(driver, [])
    if not driver_packages:
        return

    console.print(f"[blue]Installing {driver} driver...[/blue]")

    for pkg in driver_packages:
        try:
            run_command([sys.executable, "-m", "pip", "install", pkg])
            console.print(f"[green]✓[/green] Installed {pkg}")
        except subprocess.CalledProcessError:
            console.print(f"[yellow]⚠[/yellow] Failed to install {pkg}")


def full_setup(
    skip_db: bool = False,
    skip_migrations: bool = False,
    skip_admin: bool = False,
    skip_hooks: bool = False,
):
    """
    Run complete project setup.

    Handles:
    - Environment file setup
    - Database configuration
    - Database driver installation
    - Secret key generation
    - Database migrations
    - Admin user creation
    - Pre-commit hooks
    """
    console.print(Panel.fit(
        "[bold green]🚀 Fastpy Project Setup[/bold green]\n"
        "[dim]Interactive setup wizard[/dim]",
        border_style="green"
    ))

    # Step 0: Upgrade pip (prevents installation issues)
    console.print("\n[bold]Step 0: Preparing Environment[/bold]")
    upgrade_pip()

    # Step 1: Install requirements
    console.print("\n[bold]Step 1: Installing Dependencies[/bold]")
    install_requirements()

    # Step 2: Environment setup
    console.print("\n[bold]Step 2: Environment Setup[/bold]")
    setup_env()

    # Step 3: Database configuration
    if not skip_db:
        console.print("\n[bold]Step 3: Database Configuration[/bold]")
        config = setup_db()

        # Install driver
        install_db_driver(config.driver)

    # Step 4: Secret key
    console.print("\n[bold]Step 4: Security[/bold]")
    setup_secret()

    # Step 5: Migrations
    if not skip_migrations:
        console.print("\n[bold]Step 5: Database Migrations[/bold]")
        if Confirm.ask("Run database migrations?", default=True):
            run_migrations()

            # Step 6: Admin user
            if not skip_admin:
                console.print("\n[bold]Step 6: Admin User[/bold]")
                if Confirm.ask("Create super admin user?", default=True):
                    setup_admin()

    # Step 7: Pre-commit hooks
    if not skip_hooks:
        console.print("\n[bold]Step 7: Code Quality[/bold]")
        if Confirm.ask("Install pre-commit hooks?", default=True):
            setup_hooks()

    # Complete!
    console.print(Panel.fit(
        "[bold green]✓ Setup Complete![/bold green]\n\n"
        "[cyan]Next steps:[/cyan]\n"
        "  1. Start server: [yellow]fastpy serve[/yellow]\n"
        "  2. Visit docs:   [blue]http://localhost:8000/docs[/blue]\n"
        "  3. Generate code: [yellow]fastpy make:resource Post -m[/yellow]",
        border_style="green"
    ))


# Export functions for use in main CLI
__all__ = [
    "setup_db",
    "setup_secret",
    "setup_admin",
    "setup_hooks",
    "setup_env",
    "run_migrations",
    "full_setup",
    "upgrade_pip",
    "install_requirements",
    "DatabaseConfig",
]
