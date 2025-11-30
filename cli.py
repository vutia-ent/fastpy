#!/usr/bin/env python3
"""
FastCLI - Code generation CLI tool for FastAPI project
Usage: python cli.py [command] or fastcli [command] (after pip install -e .)
"""
import typer
import subprocess
import sys
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from pathlib import Path
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

app = typer.Typer(help="Code generation CLI for FastAPI")
console = Console()


def to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case"""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase"""
    return "".join(word.capitalize() for word in name.split("_"))


def to_kebab_case(name: str) -> str:
    """Convert to kebab-case"""
    return to_snake_case(name).replace("_", "-")


def pluralize(name: str) -> str:
    """Simple pluralization"""
    if name.endswith("y"):
        return name[:-1] + "ies"
    elif name.endswith(("s", "x", "z", "ch", "sh")):
        return name + "es"
    return name + "s"


# Field type mappings with enhanced types
FIELD_TYPES = {
    "string": {"python": "str", "sqlmodel": "Field(nullable=False, max_length=255)"},
    "text": {"python": "str", "sqlmodel": "Field(nullable=False)"},
    "integer": {"python": "int", "sqlmodel": "Field(nullable=False)"},
    "bigint": {"python": "int", "sqlmodel": "Field(nullable=False)"},
    "float": {"python": "float", "sqlmodel": "Field(nullable=False)"},
    "decimal": {"python": "Decimal", "sqlmodel": "Field(max_digits=10, decimal_places=2)"},
    "money": {"python": "Decimal", "sqlmodel": "Field(max_digits=15, decimal_places=2)"},
    "percent": {"python": "Decimal", "sqlmodel": "Field(ge=0, le=100, decimal_places=2)"},
    "boolean": {"python": "bool", "sqlmodel": "Field(default=False)"},
    "datetime": {"python": "datetime", "sqlmodel": "Field(default_factory=utc_now)"},
    "date": {"python": "date", "sqlmodel": "Field(nullable=False)"},
    "time": {"python": "time", "sqlmodel": "Field(nullable=False)"},
    "email": {"python": "EmailStr", "sqlmodel": "Field(nullable=False, max_length=255, index=True)"},
    "url": {"python": "str", "sqlmodel": "Field(nullable=False, max_length=500)"},
    "uuid": {"python": "UUID", "sqlmodel": "Field(default_factory=uuid4)"},
    "json": {"python": "dict", "sqlmodel": "Field(default={}, sa_column=Column(JSON))"},
    "phone": {"python": "str", "sqlmodel": "Field(nullable=False, max_length=20)"},
    "slug": {"python": "str", "sqlmodel": "Field(nullable=False, unique=True, index=True, max_length=255)"},
    "ip": {"python": "str", "sqlmodel": "Field(nullable=False, max_length=45)"},
    "color": {"python": "str", "sqlmodel": "Field(nullable=False, max_length=7)"},
    "file": {"python": "str", "sqlmodel": "Field(nullable=True, max_length=500)"},
    "image": {"python": "str", "sqlmodel": "Field(nullable=True, max_length=500)"},
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

        if self.nullable:
            python_type = f"Optional[{python_type}]"

        # Build validation
        params = []
        if self.nullable:
            params.append("default=None")
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

    # Join remaining parts back with ':' to handle rules like max:100
    rules_str = ":".join(parts[2:]) if len(parts) > 2 else ""

    kwargs = {}
    nullable = True

    # Parse rules - split by comma first, then handle each rule
    if rules_str:
        for rule in rules_str.split(","):
            rule = rule.strip()
            if rule:
                process_rule(rule, kwargs)

    # Determine nullable from rules
    if "required" in rules_str.lower():
        nullable = False
    elif "nullable" in rules_str.lower():
        nullable = True

    return FieldDefinition(name, field_type, nullable, **kwargs)


def process_rule(rule: str, kwargs: dict):
    """Process a single validation rule"""
    rule = rule.strip()

    # Note: 'required' and 'nullable' are handled in parse_field_definition
    # to avoid duplicate argument issues with FieldDefinition.__init__
    if rule == "required":
        pass  # Handled in parse_field_definition
    elif rule == "nullable":
        pass  # Handled in parse_field_definition
    elif rule == "unique":
        kwargs["unique"] = True
    elif rule == "index":
        kwargs["index"] = True
    elif rule.startswith("max:"):
        kwargs["max_length"] = int(rule.split(":", 1)[1])
    elif rule.startswith("min:"):
        kwargs["min_length"] = int(rule.split(":", 1)[1])
    elif rule.startswith("gt:"):
        value = rule.split(":", 1)[1]
        kwargs["min_value"] = float(value) if "." in value else int(value) + 1
    elif rule.startswith("gte:") or rule.startswith("ge:"):
        value = rule.split(":", 1)[1]
        kwargs["min_value"] = float(value) if "." in value else int(value)
    elif rule.startswith("lt:"):
        value = rule.split(":", 1)[1]
        kwargs["max_value"] = float(value) if "." in value else int(value) - 1
    elif rule.startswith("lte:") or rule.startswith("le:"):
        value = rule.split(":", 1)[1]
        kwargs["max_value"] = float(value) if "." in value else int(value)
    elif rule.startswith("foreign:"):
        kwargs["foreign_key"] = rule.split(":", 1)[1]
    elif rule.startswith("default:"):
        kwargs["default"] = rule.split(":", 1)[1]


def prompt_for_fields() -> List[FieldDefinition]:
    """Interactive prompt for field definitions"""
    fields = []
    console.print("\n[cyan]Define your model fields[/cyan]")
    console.print(
        "[yellow]Format:[/yellow] name:type:rules (e.g., email:email:required,unique)"
    )
    console.print(f"[yellow]Available types:[/yellow] {', '.join(FIELD_TYPES.keys())}")
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


# ============================================
# Model Generation Commands
# ============================================

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
    table_name = pluralize(to_snake_case(name))
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
        field_defs = [FieldDefinition("name", "string", nullable=False, max_length=255)]

    # Generate imports
    imports = ["from typing import Optional", "from datetime import datetime", "from sqlmodel import Field"]

    # Check if we need additional imports
    needs_date = any(f.field_type == "date" for f in field_defs)
    needs_time = any(f.field_type == "time" for f in field_defs)
    needs_email = any(f.field_type == "email" for f in field_defs)
    needs_json = any(f.field_type == "json" for f in field_defs)
    needs_uuid = any(f.field_type == "uuid" for f in field_defs)
    needs_decimal = any(f.field_type in ["decimal", "money", "percent"] for f in field_defs)

    if needs_date or needs_time:
        imports[1] = "from datetime import datetime, date, time"
    if needs_email:
        imports.append("from pydantic import EmailStr")
    if needs_json:
        imports.append("from sqlalchemy import Column, JSON")
    if needs_uuid:
        imports.append("from uuid import UUID, uuid4")
    if needs_decimal:
        imports.append("from decimal import Decimal")

    imports.append("from app.models.base import BaseModel, utc_now")

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
    """Create a new controller with CRUD operations"""
    controller_name = to_pascal_case(name) + "Controller"
    model_name = to_pascal_case(name)
    file_name = to_snake_case(name) + "_controller.py"
    file_path = Path(f"app/controllers/{file_name}")

    if file_path.exists():
        console.print(f"[red]Controller already exists:[/red] {file_path}")
        raise typer.Exit(1)

    controller_template = f'''from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.{to_snake_case(name)} import {model_name}, {model_name}Create, {model_name}Update
from app.utils.pagination import paginate, PaginatedResult


class {controller_name}:
    """Controller for {model_name} operations"""

    @staticmethod
    async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[{model_name}]:
        """Get all non-deleted {to_snake_case(name)}s"""
        query = select({model_name}).where({model_name}.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_paginated(
        session: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> PaginatedResult[{model_name}]:
        """Get paginated {to_snake_case(name)}s"""
        query = select({model_name}).where({model_name}.deleted_at.is_(None))
        return await paginate(
            session=session,
            query=query,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )

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
        await session.flush()
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

        item.touch()
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    @staticmethod
    async def delete(session: AsyncSession, id: int) -> dict:
        """Soft delete a {to_snake_case(name)}"""
        item = await {controller_name}.get_by_id(session, id)
        item.soft_delete()
        session.add(item)
        await session.flush()
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
        await session.flush()
        await session.refresh(item)
        return item

    @staticmethod
    async def count(session: AsyncSession) -> int:
        """Count total {to_snake_case(name)}s"""
        from sqlalchemy import func
        query = select(func.count({model_name}.id)).where({model_name}.deleted_at.is_(None))
        result = await session.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def exists(session: AsyncSession, id: int) -> bool:
        """Check if {to_snake_case(name)} exists"""
        query = select({model_name}.id).where({model_name}.id == id, {model_name}.deleted_at.is_(None))
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None
'''

    file_path.write_text(controller_template)
    console.print(f"[green]✓[/green] Controller created: {file_path}")


@app.command("make:route")
def make_route(
    name: str = typer.Argument(..., help="Route name (e.g., BlogPost)"),
    protected: bool = typer.Option(False, "--protected", "-p", help="Add authentication"),
):
    """Create a new route file with all CRUD endpoints"""
    model_name = to_pascal_case(name)
    controller_name = model_name + "Controller"
    file_name = to_snake_case(name) + "_routes.py"
    file_path = Path(f"app/routes/{file_name}")
    route_prefix = pluralize(to_snake_case(name))

    if file_path.exists():
        console.print(f"[red]Route already exists:[/red] {file_path}")
        raise typer.Exit(1)

    # Auth import if protected
    auth_import = ""
    auth_dep = ""
    if protected:
        auth_import = "\nfrom app.utils.auth import get_current_active_user\nfrom app.models.user import User"
        auth_dep = ", current_user: User = Depends(get_current_active_user)"

    route_template = f'''from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.controllers.{to_snake_case(name)}_controller import {controller_name}
from app.models.{to_snake_case(name)} import {model_name}, {model_name}Create, {model_name}Update, {model_name}Read
from app.config.settings import settings{auth_import}

router = APIRouter()


@router.get("/", response_model=List[{model_name}Read])
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session){auth_dep}
):
    """Get all {to_snake_case(name)}s"""
    return await {controller_name}.get_all(session, skip, limit)


@router.get("/paginated")
async def get_paginated(
    page: int = Query(1, ge=1),
    per_page: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    session: AsyncSession = Depends(get_session){auth_dep}
) -> Dict[str, Any]:
    """Get paginated {to_snake_case(name)}s with sorting"""
    result = await {controller_name}.get_paginated(session, page, per_page, sort_by, sort_order)
    return {{
        "data": result.items,
        "pagination": {{
            "page": result.page,
            "per_page": result.per_page,
            "total": result.total,
            "pages": result.pages,
            "has_next": result.has_next,
            "has_prev": result.has_prev
        }}
    }}


@router.get("/count")
async def count(session: AsyncSession = Depends(get_session){auth_dep}) -> Dict[str, int]:
    """Get total count"""
    count = await {controller_name}.count(session)
    return {{"count": count}}


@router.get("/{{id}}", response_model={model_name}Read)
async def get_one(id: int, session: AsyncSession = Depends(get_session){auth_dep}):
    """Get {to_snake_case(name)} by ID"""
    return await {controller_name}.get_by_id(session, id)


@router.head("/{{id}}", status_code=status.HTTP_200_OK)
async def check_exists(id: int, session: AsyncSession = Depends(get_session){auth_dep}):
    """Check if {to_snake_case(name)} exists"""
    exists = await {controller_name}.exists(session, id)
    if not exists:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return None


@router.post("/", response_model={model_name}Read, status_code=201)
async def create(data: {model_name}Create, session: AsyncSession = Depends(get_session){auth_dep}):
    """Create a new {to_snake_case(name)}"""
    return await {controller_name}.create(session, data)


@router.put("/{{id}}", response_model={model_name}Read)
async def update(
    id: int, data: {model_name}Update, session: AsyncSession = Depends(get_session){auth_dep}
):
    """Full update a {to_snake_case(name)}"""
    return await {controller_name}.update(session, id, data)


@router.patch("/{{id}}", response_model={model_name}Read)
async def partial_update(
    id: int, data: {model_name}Update, session: AsyncSession = Depends(get_session){auth_dep}
):
    """Partial update a {to_snake_case(name)}"""
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
        f'  app.include_router({to_snake_case(name)}_router, prefix="/api/{route_prefix}", tags=["{model_name}s"])'
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
    """Create model, controller, and routes all at once"""
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
        table_name = pluralize(to_snake_case(name))
        console.print("\n[yellow]Run migration commands:[/yellow]")
        console.print(f'  alembic revision --autogenerate -m "Create {table_name} table"')
        console.print("  alembic upgrade head")

    console.print(f"\n[green]✓ Resource '{name}' created successfully![/green]")


# ============================================
# Service and Repository Commands
# ============================================

@app.command("make:service")
def make_service(name: str = typer.Argument(..., help="Service name (e.g., Payment)")):
    """Create a new service class"""
    service_name = to_pascal_case(name) + "Service"
    model_name = to_pascal_case(name)
    repo_name = to_pascal_case(name) + "Repository"
    file_name = to_snake_case(name) + "_service.py"
    file_path = Path(f"app/services/{file_name}")

    if file_path.exists():
        console.print(f"[red]Service already exists:[/red] {file_path}")
        raise typer.Exit(1)

    service_template = f'''"""
{model_name} service for business logic.
"""
from typing import Any, Dict, List, Optional

from app.services.base import BaseService
from app.repositories.{to_snake_case(name)}_repository import {repo_name}
from app.models.{to_snake_case(name)} import {model_name}, {model_name}Create, {model_name}Update


class {service_name}(BaseService[{model_name}, {repo_name}]):
    """Service for {model_name} operations"""

    repository_class = {repo_name}

    async def create_{to_snake_case(name)}(self, data: {model_name}Create) -> {model_name}:
        """Create a new {to_snake_case(name)} with business logic"""
        # Add any business logic here
        return await self.repository.create(data.model_dump())

    async def update_{to_snake_case(name)}(self, id: int, data: {model_name}Update) -> {model_name}:
        """Update a {to_snake_case(name)} with business logic"""
        # Add any business logic here
        return await self.repository.update(id, data.model_dump(exclude_unset=True))

    # Add custom business methods here
'''

    file_path.write_text(service_template)
    console.print(f"[green]✓[/green] Service created: {file_path}")
    console.print(f"[yellow]Note:[/yellow] You may need to create the repository first with: fastcli make:repository {name}")


@app.command("make:repository")
def make_repository(name: str = typer.Argument(..., help="Repository name (e.g., Payment)")):
    """Create a new repository class"""
    repo_name = to_pascal_case(name) + "Repository"
    model_name = to_pascal_case(name)
    file_name = to_snake_case(name) + "_repository.py"
    file_path = Path(f"app/repositories/{file_name}")

    if file_path.exists():
        console.print(f"[red]Repository already exists:[/red] {file_path}")
        raise typer.Exit(1)

    repo_template = f'''"""
{model_name} repository for database operations.
"""
from typing import Optional, List
from sqlmodel import select

from app.repositories.base import BaseRepository
from app.models.{to_snake_case(name)} import {model_name}


class {repo_name}(BaseRepository[{model_name}]):
    """Repository for {model_name} model"""

    model = {model_name}

    # Add custom query methods here
    # Example:
    # async def get_by_status(self, status: str) -> List[{model_name}]:
    #     query = select(self.model).where(
    #         self.model.status == status,
    #         self.model.deleted_at.is_(None)
    #     )
    #     result = await self.session.execute(query)
    #     return list(result.scalars().all())
'''

    file_path.write_text(repo_template)
    console.print(f"[green]✓[/green] Repository created: {file_path}")


# ============================================
# Middleware Command
# ============================================

@app.command("make:middleware")
def make_middleware(name: str = typer.Argument(..., help="Middleware name (e.g., Logging)")):
    """Create a new middleware"""
    middleware_name = to_pascal_case(name) + "Middleware"
    file_name = to_snake_case(name) + ".py"
    file_path = Path(f"app/middleware/{file_name}")

    if file_path.exists():
        console.print(f"[red]Middleware already exists:[/red] {file_path}")
        raise typer.Exit(1)

    middleware_template = f'''"""
{to_pascal_case(name)} middleware.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.utils.logger import logger


class {middleware_name}(BaseHTTPMiddleware):
    """
    {to_pascal_case(name)} middleware.
    Add your middleware logic here.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Before request processing
        logger.debug(f"{{request.method}} {{request.url.path}}")

        # Process the request
        response = await call_next(request)

        # After request processing
        # Add your logic here

        return response
'''

    file_path.write_text(middleware_template)
    console.print(f"[green]✓[/green] Middleware created: {file_path}")
    console.print("\n[yellow]Add to main.py:[/yellow]")
    console.print(f"  from app.middleware.{to_snake_case(name)} import {middleware_name}")
    console.print(f"  app.add_middleware({middleware_name})")


# ============================================
# Test and Factory Commands
# ============================================

@app.command("make:test")
def make_test(name: str = typer.Argument(..., help="Test name (e.g., User)")):
    """Create a test file for a model"""
    model_name = to_pascal_case(name)
    file_name = f"test_{to_snake_case(name)}.py"
    file_path = Path(f"tests/{file_name}")

    # Ensure tests directory exists
    Path("tests").mkdir(exist_ok=True)

    if file_path.exists():
        console.print(f"[red]Test file already exists:[/red] {file_path}")
        raise typer.Exit(1)

    test_template = f'''"""
Tests for {model_name} endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from app.models.{to_snake_case(name)} import {model_name}, {model_name}Create


@pytest.fixture
def {to_snake_case(name)}_data():
    """Sample {to_snake_case(name)} data for testing"""
    return {{
        "name": "Test {model_name}",
        # Add more fields as needed
    }}


class Test{model_name}Endpoints:
    """Test suite for {model_name} API endpoints"""

    @pytest.mark.asyncio
    async def test_create_{to_snake_case(name)}(self, {to_snake_case(name)}_data):
        """Test creating a new {to_snake_case(name)}"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/{pluralize(to_snake_case(name))}/",
                json={to_snake_case(name)}_data
            )
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == {to_snake_case(name)}_data["name"]
            assert "id" in data

    @pytest.mark.asyncio
    async def test_get_{to_snake_case(name)}s(self):
        """Test getting all {to_snake_case(name)}s"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/{pluralize(to_snake_case(name))}/")
            assert response.status_code == 200
            assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_{to_snake_case(name)}_by_id(self, {to_snake_case(name)}_data):
        """Test getting a {to_snake_case(name)} by ID"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # First create a {to_snake_case(name)}
            create_response = await client.post(
                "/api/{pluralize(to_snake_case(name))}/",
                json={to_snake_case(name)}_data
            )
            created_id = create_response.json()["id"]

            # Then get it
            response = await client.get(f"/api/{pluralize(to_snake_case(name))}/{{created_id}}")
            assert response.status_code == 200
            assert response.json()["id"] == created_id

    @pytest.mark.asyncio
    async def test_get_{to_snake_case(name)}_not_found(self):
        """Test getting a non-existent {to_snake_case(name)}"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/{pluralize(to_snake_case(name))}/99999")
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_{to_snake_case(name)}(self, {to_snake_case(name)}_data):
        """Test updating a {to_snake_case(name)}"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # First create a {to_snake_case(name)}
            create_response = await client.post(
                "/api/{pluralize(to_snake_case(name))}/",
                json={to_snake_case(name)}_data
            )
            created_id = create_response.json()["id"]

            # Then update it
            update_data = {{"name": "Updated {model_name}"}}
            response = await client.put(
                f"/api/{pluralize(to_snake_case(name))}/{{created_id}}",
                json=update_data
            )
            assert response.status_code == 200
            assert response.json()["name"] == "Updated {model_name}"

    @pytest.mark.asyncio
    async def test_delete_{to_snake_case(name)}(self, {to_snake_case(name)}_data):
        """Test soft deleting a {to_snake_case(name)}"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # First create a {to_snake_case(name)}
            create_response = await client.post(
                "/api/{pluralize(to_snake_case(name))}/",
                json={to_snake_case(name)}_data
            )
            created_id = create_response.json()["id"]

            # Then delete it
            response = await client.delete(f"/api/{pluralize(to_snake_case(name))}/{{created_id}}")
            assert response.status_code == 200

            # Verify it's deleted (soft delete)
            get_response = await client.get(f"/api/{pluralize(to_snake_case(name))}/{{created_id}}")
            assert get_response.status_code == 404
'''

    file_path.write_text(test_template)
    console.print(f"[green]✓[/green] Test file created: {file_path}")


@app.command("make:factory")
def make_factory(name: str = typer.Argument(..., help="Factory name (e.g., User)")):
    """Create a test factory for a model"""
    model_name = to_pascal_case(name)
    factory_name = to_pascal_case(name) + "Factory"
    file_name = f"{to_snake_case(name)}_factory.py"
    file_path = Path(f"tests/factories/{file_name}")

    # Ensure factories directory exists
    Path("tests/factories").mkdir(parents=True, exist_ok=True)

    # Create __init__.py if it doesn't exist
    init_path = Path("tests/factories/__init__.py")
    if not init_path.exists():
        init_path.write_text('"""Test factories."""\n')

    if file_path.exists():
        console.print(f"[red]Factory already exists:[/red] {file_path}")
        raise typer.Exit(1)

    factory_template = f'''"""
Factory for {model_name} model.
"""
import factory
from faker import Faker

from app.models.{to_snake_case(name)} import {model_name}

fake = Faker()


class {factory_name}(factory.Factory):
    """Factory for creating {model_name} instances"""

    class Meta:
        model = {model_name}

    name = factory.LazyFunction(lambda: fake.name())
    # Add more fields as needed
    # email = factory.LazyFunction(lambda: fake.email())
    # description = factory.LazyFunction(lambda: fake.text())

    @classmethod
    def create_batch_dict(cls, size: int) -> list:
        """Create a batch of {model_name} dictionaries"""
        return [cls.build().__dict__ for _ in range(size)]
'''

    file_path.write_text(factory_template)
    console.print(f"[green]✓[/green] Factory created: {file_path}")


# ============================================
# Seeder Commands
# ============================================

@app.command("make:seeder")
def make_seeder(name: str = typer.Argument(..., help="Seeder name (e.g., User)")):
    """Create a database seeder"""
    seeder_name = to_pascal_case(name) + "Seeder"
    model_name = to_pascal_case(name)
    file_name = f"{to_snake_case(name)}_seeder.py"
    file_path = Path(f"app/seeders/{file_name}")

    if file_path.exists():
        console.print(f"[red]Seeder already exists:[/red] {file_path}")
        raise typer.Exit(1)

    seeder_template = f'''"""
Seeder for {model_name} model.
"""
from typing import List
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.{to_snake_case(name)} import {model_name}

fake = Faker()


class {seeder_name}:
    """Seeder for {model_name} data"""

    @staticmethod
    async def run(session: AsyncSession, count: int = 10) -> List[{model_name}]:
        """
        Seed {to_snake_case(name)}s into the database.

        Args:
            session: Database session
            count: Number of records to create

        Returns:
            List of created {model_name}s
        """
        items = []
        for _ in range(count):
            item = {model_name}(
                name=fake.name(),
                # Add more fields as needed
            )
            session.add(item)
            items.append(item)

        await session.flush()

        for item in items:
            await session.refresh(item)

        return items

    @staticmethod
    def get_sample_data() -> dict:
        """Get sample data for a single {to_snake_case(name)}"""
        return {{
            "name": fake.name(),
            # Add more fields as needed
        }}
'''

    file_path.write_text(seeder_template)
    console.print(f"[green]✓[/green] Seeder created: {file_path}")


# ============================================
# Enum Command
# ============================================

@app.command("make:enum")
def make_enum(
    name: str = typer.Argument(..., help="Enum name (e.g., Status)"),
    values: List[str] = typer.Option(
        None,
        "--value",
        "-v",
        help="Enum value (e.g., -v active -v inactive)",
    ),
):
    """Create an enum class"""
    enum_name = to_pascal_case(name)
    file_name = f"{to_snake_case(name)}.py"
    file_path = Path(f"app/enums/{file_name}")

    if file_path.exists():
        console.print(f"[red]Enum already exists:[/red] {file_path}")
        raise typer.Exit(1)

    if not values:
        values = ["active", "inactive"]
        console.print(f"[yellow]No values provided, using defaults: {values}[/yellow]")

    enum_values = "\n".join([f'    {v.upper()} = "{v.lower()}"' for v in values])

    enum_template = f'''"""
{enum_name} enum.
"""
from enum import Enum


class {enum_name}(str, Enum):
    """
    {enum_name} enumeration.
    """

{enum_values}

    @classmethod
    def values(cls) -> list:
        """Get all enum values"""
        return [e.value for e in cls]

    @classmethod
    def from_value(cls, value: str) -> "{enum_name}":
        """Get enum from value"""
        for e in cls:
            if e.value == value:
                return e
        raise ValueError(f"Invalid {enum_name} value: {{value}}")
'''

    file_path.write_text(enum_template)
    console.print(f"[green]✓[/green] Enum created: {file_path}")
    console.print(f"[cyan]Values:[/cyan] {', '.join(values)}")


# ============================================
# Exception Command
# ============================================

@app.command("make:exception")
def make_exception(
    name: str = typer.Argument(..., help="Exception name (e.g., PaymentFailed)"),
    status_code: int = typer.Option(400, "--status", "-s", help="HTTP status code"),
):
    """Create a custom exception class"""
    exception_name = to_pascal_case(name) + "Exception"
    error_code = to_snake_case(name).upper()

    # Append to exceptions.py
    exceptions_path = Path("app/utils/exceptions.py")

    if not exceptions_path.exists():
        console.print(f"[red]Exceptions file not found:[/red] {exceptions_path}")
        raise typer.Exit(1)

    exception_code = f'''

class {exception_name}(AppException):
    """{to_pascal_case(name)} exception"""

    def __init__(self, message: str = "{to_pascal_case(name)} error"):
        super().__init__(
            message=message,
            status_code={status_code},
            error_code="{error_code}"
        )
'''

    with open(exceptions_path, "a") as f:
        f.write(exception_code)

    console.print(f"[green]✓[/green] Exception added to: {exceptions_path}")
    console.print(f"[cyan]Class:[/cyan] {exception_name}")
    console.print(f"[cyan]Status Code:[/cyan] {status_code}")
    console.print(f"[cyan]Error Code:[/cyan] {error_code}")


# ============================================
# Database Commands
# ============================================

@app.command("db:migrate")
def db_migrate(
    message: str = typer.Option(None, "--message", "-m", help="Migration message"),
):
    """Run database migrations (alembic upgrade head)"""
    console.print("[cyan]Running database migrations...[/cyan]")

    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        console.print("[green]✓[/green] Migrations completed successfully")
        if result.stdout:
            console.print(result.stdout)
    else:
        console.print("[red]✗[/red] Migration failed")
        console.print(result.stderr)
        raise typer.Exit(1)


@app.command("db:rollback")
def db_rollback(
    steps: int = typer.Option(1, "--steps", "-s", help="Number of migrations to rollback"),
):
    """Rollback database migrations"""
    console.print(f"[cyan]Rolling back {steps} migration(s)...[/cyan]")

    result = subprocess.run(
        ["alembic", "downgrade", f"-{steps}"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        console.print("[green]✓[/green] Rollback completed successfully")
        if result.stdout:
            console.print(result.stdout)
    else:
        console.print("[red]✗[/red] Rollback failed")
        console.print(result.stderr)
        raise typer.Exit(1)


@app.command("db:fresh")
def db_fresh():
    """Drop all tables and re-run migrations"""
    if not Confirm.ask("[yellow]This will drop all tables. Are you sure?[/yellow]"):
        console.print("Cancelled.")
        raise typer.Exit(0)

    console.print("[cyan]Dropping all tables...[/cyan]")

    # Downgrade to base
    result = subprocess.run(
        ["alembic", "downgrade", "base"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        console.print("[red]✗[/red] Failed to drop tables")
        console.print(result.stderr)
        raise typer.Exit(1)

    console.print("[green]✓[/green] Tables dropped")

    # Upgrade to head
    console.print("[cyan]Running migrations...[/cyan]")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        console.print("[green]✓[/green] Fresh database created")
    else:
        console.print("[red]✗[/red] Migration failed")
        console.print(result.stderr)
        raise typer.Exit(1)


@app.command("db:seed")
def db_seed(
    seeder: str = typer.Option(None, "--seeder", "-s", help="Specific seeder to run"),
    count: int = typer.Option(10, "--count", "-c", help="Number of records"),
):
    """Run database seeders"""
    console.print("[cyan]Running database seeders...[/cyan]")

    seed_script = f'''
import asyncio
from app.database.connection import async_session_maker

async def run_seeders():
    async with async_session_maker() as session:
        try:
'''

    if seeder:
        seeder_class = to_pascal_case(seeder) + "Seeder"
        seed_script += f'''
            from app.seeders.{to_snake_case(seeder)}_seeder import {seeder_class}
            items = await {seeder_class}.run(session, count={count})
            print(f"Created {{len(items)}} {to_snake_case(seeder)}s")
'''
    else:
        # Run all seeders
        seeders_path = Path("app/seeders")
        if seeders_path.exists():
            for seeder_file in seeders_path.glob("*_seeder.py"):
                seeder_name = seeder_file.stem.replace("_seeder", "")
                seeder_class = to_pascal_case(seeder_name) + "Seeder"
                seed_script += f'''
            from app.seeders.{seeder_file.stem} import {seeder_class}
            items = await {seeder_class}.run(session, count={count})
            print(f"Created {{len(items)}} {seeder_name}s")
'''

    seed_script += '''
            await session.commit()
            print("Seeding completed successfully!")
        except Exception as e:
            await session.rollback()
            print(f"Seeding failed: {e}")
            raise

asyncio.run(run_seeders())
'''

    # Write and execute the seed script
    seed_file = Path("_seed_runner.py")
    seed_file.write_text(seed_script)

    try:
        result = subprocess.run([sys.executable, str(seed_file)], capture_output=True, text=True)
        if result.returncode == 0:
            console.print("[green]✓[/green] Seeding completed")
            console.print(result.stdout)
        else:
            console.print("[red]✗[/red] Seeding failed")
            console.print(result.stderr)
    finally:
        seed_file.unlink(missing_ok=True)


# ============================================
# Server Commands
# ============================================

def is_port_in_use(port: int) -> bool:
    """Check if a port is in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def find_available_port(start_port: int, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port"""
    for i in range(max_attempts):
        port = start_port + i
        if not is_port_in_use(port):
            return port
    return start_port + max_attempts


@app.command("serve")
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    reload: bool = typer.Option(True, "--reload/--no-reload", help="Enable auto-reload"),
):
    """Start the development server"""
    # Check if port is in use and find alternative
    if is_port_in_use(port):
        original_port = port
        port = find_available_port(port + 1)
        console.print(f"[yellow]⚠[/yellow] Port {original_port} is in use, using port {port} instead")

    console.print(f"[cyan]Starting server on {host}:{port}...[/cyan]")

    cmd = ["uvicorn", "main:app", f"--host={host}", f"--port={port}"]
    if reload:
        cmd.append("--reload")

    subprocess.run(cmd)


@app.command("route:list")
def route_list():
    """List all registered routes"""
    console.print("[cyan]Loading routes...[/cyan]\n")

    try:
        # Import the app to get routes
        from main import app as fastapi_app

        table = Table(title="Registered Routes")
        table.add_column("Method", style="cyan", width=10)
        table.add_column("Path", style="green", width=40)
        table.add_column("Name", style="yellow", width=30)
        table.add_column("Tags", style="magenta", width=20)

        for route in fastapi_app.routes:
            if hasattr(route, "methods"):
                methods = ", ".join(route.methods - {"HEAD", "OPTIONS"})
                tags = ", ".join(route.tags) if hasattr(route, "tags") and route.tags else "-"
                name = route.name or "-"
                table.add_row(methods, route.path, name, tags)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error loading routes:[/red] {e}")
        console.print("[yellow]Make sure the application can be imported[/yellow]")
        raise typer.Exit(1)


# ============================================
# AI Configuration Command
# ============================================

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
    content = generate_ai_config(provider)

    file_path.write_text(content)
    console.print(f"\n[green]✓[/green] Created {file_path} for {provider_info['name']}")
    console.print(f"[dim]This file provides context to {provider_info['name']} about your project.[/dim]")


def generate_ai_config(provider: str) -> str:
    """Generate AI configuration content"""
    base_content = '''# Project Overview

Production-ready FastAPI starter with SQLModel, PostgreSQL/MySQL support, JWT authentication, MVC architecture, and FastCLI code generator.

## Technology Stack

- **Framework**: FastAPI (async/await)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL OR MySQL
- **Authentication**: JWT with bcrypt, refresh tokens
- **Migrations**: Alembic
- **CLI**: FastCLI (code generator)
- **Testing**: pytest + pytest-asyncio + factory-boy

## Development Commands

```bash
# Activate virtual environment (required before running commands)
source venv/bin/activate

# Start development server
python cli.py serve
# Or: uvicorn main:app --reload

# List all routes
python cli.py route:list
```

## Code Generation (FastCLI)

```bash
# Generate complete resource (model + controller + routes)
python cli.py make:resource Post -f title:string:required,max:200 -f body:text:required -m -p

# Individual generators
python cli.py make:model Post -f title:string:required -m      # Model + migration
python cli.py make:controller Post                              # Controller
python cli.py make:route Post --protected                       # Routes (with auth)
python cli.py make:service Post                                 # Service class
python cli.py make:repository Post                              # Repository class
python cli.py make:middleware Logging                           # Middleware
python cli.py make:test Post                                    # Test file
python cli.py make:factory Post                                 # Test factory
python cli.py make:seeder Post                                  # Database seeder
python cli.py make:enum Status -v active -v inactive            # Enum
python cli.py make:exception PaymentFailed -s 400               # Custom exception

# List all commands
python cli.py list
```

## Database Commands

```bash
python cli.py db:migrate                         # Run migrations
python cli.py db:rollback                        # Rollback one migration
python cli.py db:rollback --steps 3              # Rollback multiple
python cli.py db:fresh                           # Drop all & re-migrate
python cli.py db:seed                            # Run all seeders
python cli.py db:seed --seeder User --count 50   # Run specific seeder

# Alembic directly
alembic revision --autogenerate -m "Add posts table"
alembic upgrade head
alembic downgrade -1
```

## Field Definition Syntax

**Format:** `name:type:rules`

**Field Types:**
string, text, integer, bigint, float, decimal, money, percent, boolean, datetime, date, time, email, url, uuid, json, phone, slug, ip, color, file, image

**Validation Rules:**
- `required` - Field cannot be null
- `nullable` - Field can be null
- `unique` - Unique constraint
- `index` - Database index
- `max:N` - Maximum length/value
- `min:N` - Minimum length/value
- `ge:N` / `gte:N` - Greater than or equal
- `le:N` / `lte:N` - Less than or equal
- `gt:N` - Greater than
- `lt:N` - Less than
- `foreign:table.column` - Foreign key

**Examples:**
```bash
-f title:string:required,max:200
-f price:decimal:required,ge:0
-f user_id:integer:required,foreign:users.id
-f email:email:required,unique
-f published_at:datetime:nullable
```

## Project Architecture

```
app/
├── config/           # Application settings (settings.py)
├── controllers/      # Business logic (CRUD operations)
├── database/         # DB connection and session management
├── enums/            # Enum definitions
├── middleware/       # Custom middleware
│   ├── request_id.py   # X-Request-ID tracking
│   ├── timing.py       # X-Response-Time header
│   └── rate_limit.py   # Sliding window rate limiting
├── models/           # SQLModel models with Pydantic schemas
├── repositories/     # Data access layer (BaseRepository)
├── routes/           # API route definitions
├── seeders/          # Database seeders
├── services/         # Business logic services (BaseService)
└── utils/
    ├── auth.py         # JWT & password hashing
    ├── exceptions.py   # Custom exceptions
    ├── logger.py       # Structured logging
    ├── pagination.py   # Pagination utilities
    └── responses.py    # Standard response format

tests/
├── conftest.py       # Pytest fixtures
├── factories.py      # Test data factories
└── test_*.py         # Test files
```

## Naming Conventions

- **Tables**: plural, snake_case (`users`, `blog_posts`)
- **Models**: singular, PascalCase (`User`, `BlogPost`)
- **Files**: snake_case (`user_controller.py`)
- **Controllers**: `{Model}Controller`
- **Routes**: `{model}_routes.py`

## Base Model Features

All models inherit from `BaseModel` which provides:
- `id` - Auto-incrementing primary key
- `created_at` - Timestamp on creation
- `updated_at` - Timestamp on update
- `deleted_at` - Soft delete timestamp
- `soft_delete()` - Soft delete method
- `restore()` - Restore soft deleted record
- `is_deleted` - Property to check if deleted
- `touch()` - Update timestamps

## Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user (JSON) |
| `/api/auth/login` | POST | Login (form-data, OAuth2) |
| `/api/auth/login/json` | POST | Login (JSON: email, password) |
| `/api/auth/refresh` | POST | Refresh access token |
| `/api/auth/me` | GET | Get current user |
| `/api/auth/change-password` | POST | Change password |
| `/api/auth/logout` | POST | Logout |

## Protecting Routes

```python
from app.utils.auth import get_current_active_user
from app.models.user import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"user": current_user}
```

## Standard Response Format

```python
from app.utils.responses import success_response, error_response, paginated_response

# Success
return success_response(data=user, message="User created")

# Error
return error_response(message="Not found", code="NOT_FOUND", status_code=404)

# Paginated
return paginated_response(items=users, page=1, per_page=20, total=100)
```

## Custom Exceptions

```python
from app.utils.exceptions import (
    NotFoundException,      # 404
    BadRequestException,    # 400
    UnauthorizedException,  # 401
    ForbiddenException,     # 403
    ConflictException,      # 409
    ValidationException,    # 422
    RateLimitException      # 429
)

raise NotFoundException("User not found")
```

## Middleware

- **RequestIDMiddleware** - Adds X-Request-ID to requests/responses
- **TimingMiddleware** - Adds X-Response-Time header
- **RateLimitMiddleware** - Sliding window rate limiting (configurable in .env)

## Health Check Endpoints

- `GET /health/` - Basic health check
- `GET /health/ready` - Readiness (includes DB)
- `GET /health/live` - Liveness probe
- `GET /health/info` - Service information

## Testing

```bash
pytest                              # Run all tests
pytest -v                           # Verbose output
pytest tests/test_auth.py           # Specific file
pytest --cov=app --cov-report=html  # With coverage
```

## Environment Variables

Key settings in `.env`:
- `DB_DRIVER` - postgresql or mysql
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT secret (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiry (default: 30)
- `RATE_LIMIT_ENABLED` - Enable rate limiting
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)

## User-Specific Instructions

- All table Actions should be in an ActionGroup
- Use JSON for all POST/PUT/PATCH request bodies
- Always use async/await for database operations
- Filter soft deletes in queries: `where(Model.deleted_at.is_(None))`
'''
    return base_content


# ============================================
# List Command
# ============================================

@app.command("list")
def list_commands():
    """List all available commands with examples"""
    table = Table(title="FastCLI Commands")
    table.add_column("Command", style="cyan", width=25)
    table.add_column("Description", style="green", width=35)
    table.add_column("Example", style="yellow")

    commands = [
        ("serve", "Start dev server", "fastcli serve --port 8000"),
        ("route:list", "List all routes", "fastcli route:list"),
        ("make:model", "Create model", "fastcli make:model Post -f title:string:required -m"),
        ("make:controller", "Create controller", "fastcli make:controller Post"),
        ("make:route", "Create routes", "fastcli make:route Post -p"),
        ("make:resource", "Create all at once", "fastcli make:resource Post -i -m -p"),
        ("make:service", "Create service", "fastcli make:service Payment"),
        ("make:repository", "Create repository", "fastcli make:repository Payment"),
        ("make:middleware", "Create middleware", "fastcli make:middleware Logging"),
        ("make:test", "Create test file", "fastcli make:test User"),
        ("make:factory", "Create test factory", "fastcli make:factory User"),
        ("make:seeder", "Create seeder", "fastcli make:seeder User"),
        ("make:enum", "Create enum", "fastcli make:enum Status -v active -v inactive"),
        ("make:exception", "Create exception", "fastcli make:exception NotFound -s 404"),
        ("db:migrate", "Run migrations", "fastcli db:migrate"),
        ("db:rollback", "Rollback migrations", "fastcli db:rollback -s 2"),
        ("db:fresh", "Fresh database", "fastcli db:fresh"),
        ("db:seed", "Run seeders", "fastcli db:seed -c 20"),
        ("init:ai", "AI config file", "fastcli init:ai claude"),
        ("update", "Update Fastpy files", "fastcli update --cli"),
        ("list", "List commands", "fastcli list"),
    ]

    for cmd, desc, example in commands:
        table.add_row(cmd, desc, example)

    console.print(table)

    console.print("\n[cyan]Field Types:[/cyan]")
    console.print(f"  {', '.join(FIELD_TYPES.keys())}")

    console.print("\n[cyan]Validation Rules:[/cyan]")
    console.print("  required, nullable, unique, index, max:N, min:N, gt:N, lt:N, ge:N, le:N, foreign:table.column")


# ============================================
# Update Command
# ============================================

FASTPY_BASE_URL = "https://raw.githubusercontent.com/vutia-ent/fastpy/main"

UPDATE_FILES = {
    "cli": ["cli.py"],
    "utils": [
        "app/utils/auth.py",
        "app/utils/exceptions.py",
        "app/utils/responses.py",
        "app/utils/pagination.py",
        "app/utils/logger.py",
    ],
    "models": ["app/models/base.py"],
    "middleware": [
        "app/middleware/rate_limit.py",
        "app/middleware/request_id.py",
        "app/middleware/timing.py",
    ],
    "config": ["app/config/settings.py"],
    "database": ["app/database/connection.py"],
}


@app.command("update")
def update(
    cli: bool = typer.Option(False, "--cli", help="Update CLI only"),
    utils: bool = typer.Option(False, "--utils", help="Update utility files"),
    models: bool = typer.Option(False, "--models", help="Update base models"),
    middleware: bool = typer.Option(False, "--middleware", help="Update middleware"),
    config: bool = typer.Option(False, "--config", help="Update config"),
    database: bool = typer.Option(False, "--database", help="Update database connection"),
    all_files: bool = typer.Option(False, "--all", "-a", help="Update all files"),
):
    """Update Fastpy files from the latest release"""
    import urllib.request
    import urllib.error

    files_to_update = []

    if all_files:
        for file_list in UPDATE_FILES.values():
            files_to_update.extend(file_list)
    else:
        if cli:
            files_to_update.extend(UPDATE_FILES["cli"])
        if utils:
            files_to_update.extend(UPDATE_FILES["utils"])
        if models:
            files_to_update.extend(UPDATE_FILES["models"])
        if middleware:
            files_to_update.extend(UPDATE_FILES["middleware"])
        if config:
            files_to_update.extend(UPDATE_FILES["config"])
        if database:
            files_to_update.extend(UPDATE_FILES["database"])

    if not files_to_update:
        console.print("[yellow]No update option selected.[/yellow]")
        console.print("\nUsage:")
        console.print("  python cli.py update --cli          # Update CLI only")
        console.print("  python cli.py update --utils        # Update utility files")
        console.print("  python cli.py update --middleware   # Update middleware")
        console.print("  python cli.py update --all          # Update all files")
        return

    console.print(f"[cyan]Updating {len(files_to_update)} file(s)...[/cyan]\n")

    success_count = 0
    for file_path in files_to_update:
        url = f"{FASTPY_BASE_URL}/{file_path}"
        try:
            # Backup existing file
            local_path = Path(file_path)
            if local_path.exists():
                backup_path = local_path.with_suffix(local_path.suffix + ".backup")
                backup_path.write_text(local_path.read_text())

            # Download new file
            with urllib.request.urlopen(url, timeout=10) as response:
                content = response.read().decode('utf-8')
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_text(content)
                console.print(f"[green]✓[/green] Updated {file_path}")
                success_count += 1

        except urllib.error.HTTPError as e:
            console.print(f"[red]✗[/red] Failed to download {file_path}: HTTP {e.code}")
        except urllib.error.URLError as e:
            console.print(f"[red]✗[/red] Failed to download {file_path}: {e.reason}")
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to update {file_path}: {e}")

    console.print(f"\n[green]Updated {success_count}/{len(files_to_update)} files[/green]")

    if success_count > 0:
        console.print("\n[yellow]Note:[/yellow] Backup files created with .backup extension")
        console.print("Review changes and remove backups when satisfied.")


if __name__ == "__main__":
    app()
