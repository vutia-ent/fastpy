#!/usr/bin/env python3
"""
FastCLI - Code generation CLI tool for FastAPI project
Usage: python cli.py [command] or fastcli [command] (after pip install -e .)
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from pathlib import Path
import re
from typing import List, Dict, Any

app = typer.Typer(help="Code generation CLI for FastAPI")
console = Console()


def to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case"""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase"""
    return "".join(word.capitalize() for word in name.split("_"))


# Field type mappings
FIELD_TYPES = {
    "string": {"python": "str", "sqlmodel": "Field(nullable=False, max_length=255)"},
    "text": {"python": "str", "sqlmodel": "Field(nullable=False)"},
    "integer": {"python": "int", "sqlmodel": "Field(nullable=False)"},
    "float": {"python": "float", "sqlmodel": "Field(nullable=False)"},
    "boolean": {"python": "bool", "sqlmodel": "Field(default=False)"},
    "datetime": {"python": "datetime", "sqlmodel": "Field(default_factory=datetime.utcnow)"},
    "email": {"python": "EmailStr", "sqlmodel": "Field(nullable=False, max_length=255, index=True)"},
    "url": {"python": "str", "sqlmodel": "Field(nullable=False, max_length=500)"},
    "json": {"python": "dict", "sqlmodel": "Field(default={}, sa_column=Column(JSON))"},
}

# Validation rules for Pydantic schemas
VALIDATION_RULES = {
    "required": "...",
    "email": "EmailStr",
    "min": "Field(min_length={value})",
    "max": "Field(max_length={value})",
    "gt": "Field(gt={value})",
    "lt": "Field(lt={value})",
    "ge": "Field(ge={value})",
    "le": "Field(le={value})",
    "regex": 'Field(regex=r"{value}")',
    "unique": "# Unique constraint enforced at database level",
}


class FieldDefinition:
    """Represents a model field definition"""

    def __init__(self, name: str, field_type: str, nullable: bool = False, **kwargs):
        self.name = name
        self.field_type = field_type
        self.nullable = nullable
        self.unique = kwargs.get("unique", False)
        self.index = kwargs.get("index", False)
        self.default = kwargs.get("default", None)
        self.max_length = kwargs.get("max_length", None)
        self.min_length = kwargs.get("min_length", None)
        self.min_value = kwargs.get("min_value", None)
        self.max_value = kwargs.get("max_value", None)
        self.foreign_key = kwargs.get("foreign_key", None)
        self.description = kwargs.get("description", "")

    def get_model_field(self) -> str:
        """Generate SQLModel field definition"""
        type_info = FIELD_TYPES.get(self.field_type, FIELD_TYPES["string"])
        python_type = type_info["python"]

        if self.nullable:
            python_type = f"Optional[{python_type}]"

        # Build Field parameters
        params = []
        if self.nullable:
            params.append("default=None")
        else:
            params.append("nullable=False")

        if self.max_length:
            params.append(f"max_length={self.max_length}")
        if self.unique:
            params.append("unique=True")
        if self.index:
            params.append("index=True")
        if self.foreign_key:
            params.append(f'foreign_key="{self.foreign_key}"')
        if self.description:
            params.append(f'description="{self.description}"')

        field_def = f"Field({', '.join(params)})"
        return f"    {self.name}: {python_type} = {field_def}"

    def get_create_field(self) -> str:
        """Generate field for Create schema with validations"""
        type_info = FIELD_TYPES.get(self.field_type, FIELD_TYPES["string"])
        python_type = type_info["python"]

        # Build validation
        params = []
        if self.min_length:
            params.append(f"min_length={self.min_length}")
        if self.max_length:
            params.append(f"max_length={self.max_length}")
        if self.min_value is not None:
            params.append(f"ge={self.min_value}")
        if self.max_value is not None:
            params.append(f"le={self.max_value}")
        if self.description:
            params.append(f'description="{self.description}"')

        if params:
            field_def = f"Field({', '.join(params)})"
            return f"    {self.name}: {python_type} = {field_def}"
        else:
            return f"    {self.name}: {python_type}"

    def get_update_field(self) -> str:
        """Generate field for Update schema (all optional)"""
        type_info = FIELD_TYPES.get(self.field_type, FIELD_TYPES["string"])
        python_type = f"Optional[{type_info['python']}]"

        params = ["default=None"]
        if self.max_length:
            params.append(f"max_length={self.max_length}")

        field_def = f"Field({', '.join(params)})"
        return f"    {self.name}: {python_type} = {field_def}"

    def get_read_field(self) -> str:
        """Generate field for Read schema"""
        type_info = FIELD_TYPES.get(self.field_type, FIELD_TYPES["string"])
        python_type = type_info["python"]

        if self.nullable:
            python_type = f"Optional[{python_type}]"

        return f"    {self.name}: {python_type}"


def parse_field_definition(field_str: str) -> FieldDefinition:
    """
    Parse field definition with validation rules
    Format: name:type:rules
    Example: email:email:required,unique or title:string:max:255,min:3
    """
    parts = field_str.split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid field format: {field_str}. Use name:type:rules")

    name = parts[0]
    field_type = parts[1]
    rules = parts[2:] if len(parts) > 2 else []

    kwargs = {}
    nullable = True

    # Parse rules
    for rule in rules:
        if "," in rule:
            # Multiple rules in one part
            for r in rule.split(","):
                process_rule(r, kwargs)
        else:
            process_rule(rule, kwargs)

    # Check if required
    if "required" in str(rules).lower():
        nullable = False

    return FieldDefinition(name, field_type, nullable, **kwargs)


def process_rule(rule: str, kwargs: dict):
    """Process a single validation rule"""
    rule = rule.strip()

    if rule == "required":
        kwargs["nullable"] = False
    elif rule == "nullable":
        kwargs["nullable"] = True
    elif rule == "unique":
        kwargs["unique"] = True
    elif rule == "index":
        kwargs["index"] = True
    elif rule.startswith("max:"):
        kwargs["max_length"] = int(rule.split(":")[1])
    elif rule.startswith("min:"):
        kwargs["min_length"] = int(rule.split(":")[1])
    elif rule.startswith("gt:"):
        kwargs["min_value"] = int(rule.split(":")[1]) + 1
    elif rule.startswith("gte:") or rule.startswith("ge:"):
        kwargs["min_value"] = int(rule.split(":")[1])
    elif rule.startswith("lt:"):
        kwargs["max_value"] = int(rule.split(":")[1]) - 1
    elif rule.startswith("lte:") or rule.startswith("le:"):
        kwargs["max_value"] = int(rule.split(":")[1])
    elif rule.startswith("foreign:"):
        kwargs["foreign_key"] = rule.split(":")[1]
    elif rule.startswith("default:"):
        kwargs["default"] = rule.split(":")[1]


def prompt_for_fields() -> List[FieldDefinition]:
    """Interactive prompt for field definitions"""
    fields = []
    console.print("\n[cyan]Define your model fields[/cyan]")
    console.print(
        "[yellow]Format:[/yellow] name:type:rules (e.g., email:email:required,unique)"
    )
    console.print("[yellow]Available types:[/yellow] string, text, integer, float, boolean, datetime, email, url, json")
    console.print("[yellow]Available rules:[/yellow] required, nullable, unique, index, max:N, min:N, foreign:table.column")
    console.print("[dim]Press Enter with empty field name to finish[/dim]\n")

    while True:
        field_input = Prompt.ask("[cyan]Field definition[/cyan]", default="")
        if not field_input:
            break

        try:
            field = parse_field_definition(field_input)
            fields.append(field)
            console.print(f"[green]✓[/green] Added field: {field.name} ({field.field_type})")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            continue

    return fields


@app.command("make:model")
def make_model(
    name: str = typer.Argument(..., help="Model name (e.g., BlogPost)"),
    fields: List[str] = typer.Option(
        None,
        "--field",
        "-f",
        help="Field definition (e.g., -f email:email:required,unique)",
    ),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode"),
    migration: bool = typer.Option(False, "--migration", "-m", help="Create migration"),
):
    """Create a new model with field definitions and automatic validation"""
    model_name = to_pascal_case(name)
    table_name = to_snake_case(name) + "s"  # Pluralize
    file_name = to_snake_case(name) + ".py"
    file_path = Path(f"app/models/{file_name}")

    if file_path.exists():
        console.print(f"[red]Model already exists:[/red] {file_path}")
        raise typer.Exit(1)

    # Get field definitions
    field_defs: List[FieldDefinition] = []

    if interactive:
        field_defs = prompt_for_fields()
    elif fields:
        for field_str in fields:
            try:
                field_defs.append(parse_field_definition(field_str))
            except Exception as e:
                console.print(f"[red]Error parsing field '{field_str}':[/red] {e}")
                raise typer.Exit(1)
    else:
        # Default field
        field_defs = [FieldDefinition("name", "string", nullable=False, max_length=255)]

    # Generate imports
    imports = ["from typing import Optional", "from sqlmodel import Field"]

    # Check if we need additional imports
    needs_datetime = any(f.field_type == "datetime" for f in field_defs)
    needs_email = any(f.field_type == "email" for f in field_defs)
    needs_json = any(f.field_type == "json" for f in field_defs)

    if needs_datetime:
        imports.append("from datetime import datetime")
    if needs_email:
        imports.append("from pydantic import EmailStr")
    if needs_json:
        imports.append("from sqlalchemy import Column, JSON")

    imports.append("from app.models.base import BaseModel")

    # Generate model fields
    model_fields = "\n".join([f.get_model_field() for f in field_defs])
    create_fields = "\n".join([f.get_create_field() for f in field_defs])
    read_fields = "\n".join([f.get_read_field() for f in field_defs])
    update_fields = "\n".join([f.get_update_field() for f in field_defs])

    model_template = f'''{chr(10).join(imports)}


class {model_name}(BaseModel, table=True):
    """
    {model_name} model.
    Table name: {table_name}
    """

    __tablename__ = "{table_name}"

{model_fields}


class {model_name}Create(BaseModel):
    """
    Schema for creating a {model_name}.
    All validations are enforced here.
    """

{create_fields}


class {model_name}Read(BaseModel):
    """Schema for reading a {model_name}"""

    id: int
{read_fields}
    created_at: datetime
    updated_at: datetime


class {model_name}Update(BaseModel):
    """
    Schema for updating a {model_name}.
    All fields are optional.
    """

{update_fields}
'''

    file_path.write_text(model_template)
    console.print(f"[green]✓[/green] Model created: {file_path}")
    console.print(f"[cyan]Fields created:[/cyan]")
    for field in field_defs:
        console.print(f"  - {field.name}: {field.field_type}")

    # Update alembic env.py
    env_path = Path("alembic/env.py")
    if env_path.exists():
        content = env_path.read_text()
        import_line = f"from app.models.{to_snake_case(name)} import {model_name}  # noqa"
        if import_line not in content:
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "from app.models.user import User  # noqa" in line:
                    lines.insert(i + 1, import_line)
                    break
            env_path.write_text("\n".join(lines))
            console.print(f"[green]✓[/green] Added import to alembic/env.py")

    if migration:
        console.print("\n[yellow]Run migration commands:[/yellow]")
        console.print(f'  alembic revision --autogenerate -m "Create {table_name} table"')
        console.print("  alembic upgrade head")


@app.command("make:controller")
def make_controller(name: str = typer.Argument(..., help="Controller name (e.g., BlogPost)")):
    """Create a new controller"""
    controller_name = to_pascal_case(name) + "Controller"
    model_name = to_pascal_case(name)
    file_name = to_snake_case(name) + "_controller.py"
    file_path = Path(f"app/controllers/{file_name}")

    if file_path.exists():
        console.print(f"[red]Controller already exists:[/red] {file_path}")
        raise typer.Exit(1)

    controller_template = f'''from typing import List
from datetime import datetime
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.{to_snake_case(name)} import {model_name}, {model_name}Create, {model_name}Update


class {controller_name}:
    """Controller for {model_name} operations"""

    @staticmethod
    async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[{model_name}]:
        """Get all non-deleted {to_snake_case(name)}s"""
        query = select({model_name}).where({model_name}.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> {model_name}:
        """Get {to_snake_case(name)} by ID"""
        query = select({model_name}).where({model_name}.id == id, {model_name}.deleted_at.is_(None))
        result = await session.execute(query)
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="{model_name} not found")
        return item

    @staticmethod
    async def create(session: AsyncSession, data: {model_name}Create) -> {model_name}:
        """
        Create a new {to_snake_case(name)}.
        Validations are handled by Pydantic schema.
        """
        item = {model_name}(**data.model_dump())
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item

    @staticmethod
    async def update(session: AsyncSession, id: int, data: {model_name}Update) -> {model_name}:
        """
        Update a {to_snake_case(name)}.
        Only provided fields are updated.
        """
        item = await {controller_name}.get_by_id(session, id)

        # Update only provided fields
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)

        item.updated_at = datetime.utcnow()
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item

    @staticmethod
    async def delete(session: AsyncSession, id: int) -> dict:
        """Soft delete a {to_snake_case(name)}"""
        item = await {controller_name}.get_by_id(session, id)
        item.soft_delete()
        session.add(item)
        await session.commit()
        return {{"message": "{model_name} deleted successfully"}}

    @staticmethod
    async def restore(session: AsyncSession, id: int) -> {model_name}:
        """Restore a soft deleted {to_snake_case(name)}"""
        query = select({model_name}).where({model_name}.id == id)
        result = await session.execute(query)
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="{model_name} not found")

        item.restore()
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item
'''

    file_path.write_text(controller_template)
    console.print(f"[green]✓[/green] Controller created: {file_path}")


@app.command("make:route")
def make_route(
    name: str = typer.Argument(..., help="Route name (e.g., BlogPost)"),
    protected: bool = typer.Option(False, "--protected", "-p", help="Add authentication"),
):
    """Create a new route file"""
    model_name = to_pascal_case(name)
    controller_name = model_name + "Controller"
    file_name = to_snake_case(name) + "_routes.py"
    file_path = Path(f"app/routes/{file_name}")

    if file_path.exists():
        console.print(f"[red]Route already exists:[/red] {file_path}")
        raise typer.Exit(1)

    # Auth import if protected
    auth_import = ""
    auth_dep = ""
    if protected:
        auth_import = "\nfrom app.utils.auth import get_current_user\nfrom app.models.user import User"
        auth_dep = ", current_user: User = Depends(get_current_user)"

    route_template = f'''from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.controllers.{to_snake_case(name)}_controller import {controller_name}
from app.models.{to_snake_case(name)} import {model_name}, {model_name}Create, {model_name}Update, {model_name}Read{auth_import}

router = APIRouter()


@router.get("/", response_model=List[{model_name}Read])
async def get_all(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session){auth_dep}
):
    """Get all {to_snake_case(name)}s"""
    return await {controller_name}.get_all(session, skip, limit)


@router.get("/{{id}}", response_model={model_name}Read)
async def get_one(id: int, session: AsyncSession = Depends(get_session){auth_dep}):
    """Get {to_snake_case(name)} by ID"""
    return await {controller_name}.get_by_id(session, id)


@router.post("/", response_model={model_name}Read, status_code=201)
async def create(data: {model_name}Create, session: AsyncSession = Depends(get_session){auth_dep}):
    """
    Create a new {to_snake_case(name)}.
    All validation rules defined in {model_name}Create schema are enforced.
    """
    return await {controller_name}.create(session, data)


@router.put("/{{id}}", response_model={model_name}Read)
async def update(
    id: int, data: {model_name}Update, session: AsyncSession = Depends(get_session){auth_dep}
):
    """
    Update a {to_snake_case(name)}.
    Only provided fields will be updated.
    """
    return await {controller_name}.update(session, id, data)


@router.delete("/{{id}}")
async def delete(id: int, session: AsyncSession = Depends(get_session){auth_dep}):
    """Soft delete a {to_snake_case(name)}"""
    return await {controller_name}.delete(session, id)


@router.post("/{{id}}/restore", response_model={model_name}Read)
async def restore(id: int, session: AsyncSession = Depends(get_session){auth_dep}):
    """Restore a soft deleted {to_snake_case(name)}"""
    return await {controller_name}.restore(session, id)
'''

    file_path.write_text(route_template)
    console.print(f"[green]✓[/green] Route created: {file_path}")

    if protected:
        console.print("[cyan]Routes are protected with authentication[/cyan]")

    console.print("\n[yellow]Add to main.py:[/yellow]")
    console.print(
        f'  from app.routes.{to_snake_case(name)}_routes import router as {to_snake_case(name)}_router'
    )
    console.print(
        f'  app.include_router({to_snake_case(name)}_router, prefix="/api/{to_snake_case(name)}s", tags=["{model_name}s"])'
    )


@app.command("make:resource")
def make_resource(
    name: str = typer.Argument(..., help="Resource name (e.g., BlogPost)"),
    fields: List[str] = typer.Option(
        None,
        "--field",
        "-f",
        help="Field definition (e.g., -f email:email:required,unique)",
    ),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode"),
    migration: bool = typer.Option(False, "--migration", "-m", help="Create migration"),
    protected: bool = typer.Option(False, "--protected", "-p", help="Add authentication"),
):
    """Create model, controller, and routes all at once with intelligent field definitions"""
    console.print(f"[cyan]Creating resource:[/cyan] {name}\n")

    # Create model
    if interactive:
        make_model(name, fields=None, interactive=True, migration=False)
    elif fields:
        make_model(name, fields=fields, interactive=False, migration=False)
    else:
        console.print("[yellow]No fields specified. Use --field or --interactive[/yellow]")
        if Confirm.ask("Do you want to use interactive mode?"):
            make_model(name, fields=None, interactive=True, migration=False)
        else:
            make_model(name, fields=None, interactive=False, migration=False)

    make_controller(name)
    make_route(name, protected=protected)

    if migration:
        table_name = to_snake_case(name) + "s"
        console.print("\n[yellow]Run migration commands:[/yellow]")
        console.print(f'  alembic revision --autogenerate -m "Create {table_name} table"')
        console.print("  alembic upgrade head")

    console.print(f"\n[green]✓ Resource '{name}' created successfully![/green]")


@app.command("init:ai")
def init_ai(
    provider: str = typer.Argument(
        None,
        help="AI provider (claude, copilot, gemini, cursor, or leave empty for interactive)",
    )
):
    """Generate AI assistant configuration file for your project"""

    providers = {
        "claude": {
            "name": "Claude Code",
            "file": "CLAUDE.md",
            "description": "Anthropic's Claude Code (claude.ai/code)"
        },
        "copilot": {
            "name": "GitHub Copilot",
            "file": ".github/copilot-instructions.md",
            "description": "GitHub Copilot workspace instructions"
        },
        "gemini": {
            "name": "Google Gemini",
            "file": ".gemini/instructions.md",
            "description": "Google Gemini Code Assist"
        },
        "cursor": {
            "name": "Cursor AI",
            "file": ".cursorrules",
            "description": "Cursor AI editor rules"
        }
    }

    # Interactive mode if no provider specified
    if not provider:
        console.print("\n[cyan]Select AI Assistant:[/cyan]")
        for key, info in providers.items():
            console.print(f"  {key:10} - {info['name']} ({info['description']})")

        provider = Prompt.ask(
            "\n[cyan]Which AI assistant do you want to configure?[/cyan]",
            choices=list(providers.keys()),
            default="claude"
        )

    if provider not in providers:
        console.print(f"[red]Unknown provider:[/red] {provider}")
        console.print(f"[yellow]Available providers:[/yellow] {', '.join(providers.keys())}")
        raise typer.Exit(1)

    provider_info = providers[provider]
    file_path = Path(provider_info["file"])

    # Create directory if needed
    if "/" in provider_info["file"]:
        file_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if file exists
    if file_path.exists():
        overwrite = Confirm.ask(
            f"\n[yellow]{file_path} already exists. Overwrite?[/yellow]",
            default=False
        )
        if not overwrite:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0)

    # Generate content based on provider
    if provider == "claude":
        content = generate_claude_md()
    elif provider == "copilot":
        content = generate_copilot_instructions()
    elif provider == "gemini":
        content = generate_gemini_instructions()
    elif provider == "cursor":
        content = generate_cursor_rules()

    file_path.write_text(content)
    console.print(f"\n[green]✓[/green] Created {file_path} for {provider_info['name']}")
    console.print(f"[dim]This file provides context to {provider_info['name']} about your project.[/dim]")


def generate_claude_md() -> str:
    """Generate CLAUDE.md content"""
    return '''# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Production-ready FastAPI starter with SQLModel, PostgreSQL/MySQL support, JWT authentication, MVC architecture, and FastCLI code generator. Features soft deletes, automatic timestamps, password hashing, intelligent field validation, and clean folder structure.

## Technology Stack

- **Framework**: FastAPI (async/await)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL OR MySQL (configurable via .env)
- **Authentication**: JWT with bcrypt password hashing
- **Migrations**: Alembic
- **CLI**: FastCLI (Typer-based code generator with automatic validation)
- **Language**: Python 3.9+

## Development Commands

### Running the Application

```bash
# Run development server with auto-reload
uvicorn main:app --reload

# Run on specific host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### FastCLI - Code Generation

```bash
# List all available commands
fastcli list

# Generate resources with field definitions
fastcli make:model Post -f title:string:required,max:200 -f body:text:required -m
fastcli make:controller Post
fastcli make:route Post --protected
fastcli make:resource Post -i -m -p  # Interactive mode, migration, protected

# Field definition syntax: name:type:rules
# Types: string, text, integer, float, boolean, datetime, email, url, json
# Rules: required, nullable, unique, index, max:N, min:N, foreign:table.column
```

### Database Migrations

```bash
# Create migration after model changes
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check . --fix

# Type checking
mypy .
```

## Architecture

### MVC Architecture

```
app/
├── config/       # Application settings
├── controllers/  # Business logic
├── models/       # Database models (SQLModel)
├── routes/       # API endpoints (FastAPI routers)
├── database/     # Database connection & session
├── middleware/   # Custom middleware
└── utils/        # Helper utilities (auth, etc.)
```

### Naming Conventions

- **Tables**: Plural, snake_case (e.g., `users`, `blog_posts`)
- **Columns**: snake_case (e.g., `created_at`, `email_verified_at`)
- **Models**: Singular, PascalCase (e.g., `User`, `BlogPost`)
- **Files**: snake_case (e.g., `user_controller.py`, `blog_post.py`)

### Base Model

All models inherit from `BaseModel` which includes:
- `id` - Primary key (auto-increment)
- `created_at` - Timestamp (auto-set on create)
- `updated_at` - Timestamp (auto-updated)
- `deleted_at` - Timestamp for soft deletes (nullable)

## FastCLI Field Definitions

When generating models with FastCLI, use this syntax:

```bash
fastcli make:resource Product \\
  -f name:string:required,max:255 \\
  -f price:float:required,ge:0 \\
  -f stock:integer:required,ge:0 \\
  -f sku:string:required,unique \\
  -f category_id:integer:foreign:categories.id \\
  -m -p
```

This generates:
- Model with SQLModel fields
- Create/Read/Update schemas with validations
- Controller with CRUD operations
- Protected routes (if -p flag)
- Migration file (if -m flag)

## Important Notes

- Always use async/await for database operations
- Use soft deletes instead of hard deletes (call `.soft_delete()`)
- Password fields are automatically hashed in controllers
- JWT tokens expire after 30 minutes (configurable)
- All API routes should be prefixed with `/api`

## User Instructions

All table Actions should be in an ActionGroup
'''


def generate_copilot_instructions() -> str:
    """Generate GitHub Copilot instructions"""
    return '''# GitHub Copilot Instructions

## Project Context

This is a production-ready FastAPI starter with SQLModel ORM, supporting both PostgreSQL and MySQL. It follows MVC architecture with JWT authentication and includes FastCLI for intelligent code generation.

## Code Generation Guidelines

### When creating models:
- Always inherit from `BaseModel` (includes id, timestamps, soft deletes)
- Use snake_case for table names (plural)
- Use PascalCase for model class names (singular)
- Include Create/Read/Update Pydantic schemas
- Add field validations in Create schema

### When creating controllers:
- Use async/await for all database operations
- Implement soft deletes (call `.soft_delete()`)
- Include error handling with HTTPException
- Return proper status codes

### When creating routes:
- Prefix all routes with `/api`
- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Add authentication with `Depends(get_current_user)` when needed
- Include response models for type safety

## Naming Conventions

- **Tables**: `users`, `blog_posts` (plural, snake_case)
- **Models**: `User`, `BlogPost` (singular, PascalCase)
- **Files**: `user_controller.py`, `blog_post.py` (snake_case)
- **Routes**: `/api/users`, `/api/blog-posts` (kebab-case in URLs)

## FastCLI Commands

Suggest using FastCLI for rapid development:
```bash
fastcli make:resource Product -f name:string:required -f price:float:required,ge:0 -m -p
```

## Database

- Use SQLModel for ORM
- Use Alembic for migrations
- Prefer soft deletes over hard deletes
- Always use async session: `AsyncSession = Depends(get_session)`

## Authentication

- JWT tokens with bcrypt password hashing
- Protected routes use `current_user: User = Depends(get_current_user)`
- Tokens expire after 30 minutes

## Testing

- Use pytest with async support
- Include test fixtures with factory-boy
- Aim for >80% code coverage
'''


def generate_gemini_instructions() -> str:
    """Generate Google Gemini instructions"""
    return '''# Google Gemini Code Assist Instructions

## Project Overview

FastAPI production starter with:
- SQLModel ORM (PostgreSQL/MySQL)
- JWT authentication with bcrypt
- MVC architecture
- FastCLI code generator
- Soft deletes, automatic timestamps

## Key Technologies

- **Framework**: FastAPI (Python 3.9+)
- **ORM**: SQLModel + Alembic migrations
- **Auth**: JWT tokens, bcrypt passwords
- **Database**: PostgreSQL OR MySQL
- **CLI**: FastCLI (Typer + Rich)

## Development Workflow

1. **Create models**: `fastcli make:model Product -f name:string:required -m`
2. **Create controllers**: `fastcli make:controller Product`
3. **Create routes**: `fastcli make:route Product --protected`
4. **Or all at once**: `fastcli make:resource Product -i -m -p`
5. **Run migrations**: `alembic upgrade head`
6. **Start server**: `uvicorn main:app --reload`

## Code Style

- **Models**: Inherit from `BaseModel`, use type hints
- **Controllers**: Static methods, async/await
- **Routes**: FastAPI routers with dependency injection
- **Naming**: snake_case files, PascalCase classes, snake_case tables

## FastCLI Field Syntax

```
name:type:rules
```

**Types**: string, text, integer, float, boolean, datetime, email, url, json
**Rules**: required, nullable, unique, index, max:N, min:N, foreign:table.column

Example:
```bash
fastcli make:resource Post \\
  -f title:string:required,max:200 \\
  -f email:email:required,unique \\
  -f price:float:ge:0 \\
  -m -p
```

## Architecture Patterns

- MVC: models, controllers, routes separation
- Dependency injection for database sessions
- JWT middleware for authentication
- Soft deletes via `deleted_at` timestamp
- Automatic `created_at`/`updated_at` tracking

## Common Commands

- Run: `uvicorn main:app --reload`
- Test: `pytest --cov=app`
- Format: `black .`
- Lint: `ruff check . --fix`
- Migrate: `alembic upgrade head`
- Generate: `fastcli make:resource Name -i -m -p`
'''


def generate_cursor_rules() -> str:
    """Generate Cursor AI rules"""
    return '''# Cursor AI Rules

## Project: FastAPI Starter with FastCLI

### Tech Stack
- FastAPI (async), SQLModel, PostgreSQL/MySQL
- JWT auth, bcrypt passwords
- Alembic migrations
- FastCLI code generator

### Code Generation

When generating models:
- Inherit from `BaseModel` (includes id, timestamps, soft deletes)
- Use snake_case for tables (plural)
- Use PascalCase for classes (singular)
- Include Create/Read/Update schemas
- Add Pydantic validations

When generating controllers:
- Use async/await
- Implement soft deletes
- Add error handling
- Use type hints

When generating routes:
- Prefix with `/api`
- Add auth with `Depends(get_current_user)`
- Use response models
- Include proper status codes

### Naming Conventions
- Tables: `users`, `blog_posts` (plural, snake_case)
- Models: `User`, `BlogPost` (singular, PascalCase)
- Files: `user_controller.py` (snake_case)

### FastCLI Usage
Suggest FastCLI for rapid development:
```bash
fastcli make:resource Product -f name:string:required -f price:float:ge:0 -m -p
```

Field syntax: `name:type:rules`
- Types: string, text, integer, float, boolean, datetime, email, url, json
- Rules: required, nullable, unique, index, max:N, min:N, foreign:table.column

### Architecture
- MVC pattern (models, controllers, routes)
- Soft deletes via `deleted_at`
- Automatic timestamps
- JWT authentication
- Async database operations

### Commands
- Run: `uvicorn main:app --reload`
- Test: `pytest --cov=app`
- Format: `black .`
- Lint: `ruff check . --fix`
- Migrate: `alembic upgrade head`
- Generate: `fastcli make:resource Name -i -m -p`

### Important
- Always use async/await for DB
- Use soft deletes (`.soft_delete()`)
- Hash passwords automatically
- JWT tokens expire in 30min
- All routes prefixed with `/api`
'''


@app.command("list")
def list_commands():
    """List all available commands with examples"""
    table = Table(title="Available CLI Commands")
    table.add_column("Command", style="cyan", width=30)
    table.add_column("Description", style="green")
    table.add_column("Example", style="yellow")

    table.add_row(
        "init:ai",
        "Generate AI assistant config",
        "fastcli init:ai claude",
    )
    table.add_row(
        "make:model",
        "Create a new model with validations",
        "fastcli make:model Post -f title:string:required,max:200 -f body:text:required -m",
    )
    table.add_row(
        "make:controller",
        "Create a new controller",
        "fastcli make:controller Post",
    )
    table.add_row(
        "make:route",
        "Create a new route file",
        "fastcli make:route Post --protected",
    )
    table.add_row(
        "make:resource",
        "Create model, controller, and routes",
        "fastcli make:resource Post -i -m -p",
    )
    table.add_row(
        "list",
        "List all available commands",
        "fastcli list",
    )

    console.print(table)

    console.print("\n[cyan]Field Types:[/cyan]")
    console.print("  string, text, integer, float, boolean, datetime, email, url, json")

    console.print("\n[cyan]Validation Rules:[/cyan]")
    console.print("  required, nullable, unique, index, max:N, min:N, foreign:table.column")

    console.print("\n[cyan]Options:[/cyan]")
    console.print("  -f, --field      Add a field (can be used multiple times)")
    console.print("  -i, --interactive  Interactive field definition")
    console.print("  -m, --migration    Generate migration after model creation")
    console.print("  -p, --protected    Add authentication to routes")


if __name__ == "__main__":
    app()
