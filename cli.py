#!/usr/bin/env python3
"""
FastCLI - Code generation CLI tool for FastAPI project
Usage: fastpy [command] (install with: pip install fastpy-cli)
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
    """Convert snake_case or camelCase to PascalCase, preserving existing capitalization"""
    # If already PascalCase (starts with uppercase, contains uppercase), return as-is
    if name[0].isupper() and any(c.isupper() for c in name[1:]):
        return name
    # Convert snake_case to PascalCase
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
    no_concerns: bool = typer.Option(False, "--no-concerns", help="Disable Model Concerns (enabled by default)"),
):
    """Create a new model with field definitions, validation, and Model Concerns"""
    model_name = to_pascal_case(name)
    table_name = pluralize(to_snake_case(name))
    file_name = to_snake_case(name) + ".py"
    file_path = Path(f"app/models/{file_name}")
    snake_name = to_snake_case(name)

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
    imports = ["from typing import Optional, List", "from datetime import datetime", "from sqlmodel import Field"]

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

    # Model Concerns are enabled by default
    use_concerns = not no_concerns
    concerns_import = ""
    concerns_mixin = ""
    concerns_config = ""

    if use_concerns:
        concerns_import = "from app.models.concerns import HasScopes, GuardsAttributes"
        concerns_mixin = ", HasScopes, GuardsAttributes"
        # Generate fillable fields list
        fillable_fields = [f.name for f in field_defs]
        concerns_config = f'''
    # Mass assignment protection
    _fillable = {fillable_fields}
    _guarded = ["id", "created_at", "updated_at", "deleted_at"]
'''
        imports.append(concerns_import)

    # Check if user defined an id field with UUID type
    has_uuid_id = any(f.name == "id" and f.field_type == "uuid" for f in field_defs)

    # Filter out user-defined id field if it exists (we'll handle it separately)
    non_id_fields = [f for f in field_defs if f.name != "id"]

    # Generate model fields (excluding id if UUID)
    model_fields = "\n".join([f.get_model_field() for f in non_id_fields])

    # For create/read/update, also filter id field since it's auto-generated
    create_fields = "\n".join([f.get_create_field() for f in non_id_fields])
    read_fields = "\n".join([f.get_read_field() for f in non_id_fields])
    update_fields = "\n".join([f.get_update_field() for f in non_id_fields])

    # Determine the id field definition
    if has_uuid_id:
        id_field = "id: UUID = Field(default_factory=uuid4, primary_key=True)"
        id_read_type = "id: UUID"
    else:
        id_field = "id: Optional[int] = Field(default=None, primary_key=True)"
        id_read_type = "id: int"

    model_template = f'''{chr(10).join(imports)}


class {model_name}(BaseModel{concerns_mixin}, table=True):
    """
    {model_name} model.

    Table name: {table_name}
    Active Record methods: create(), find(), find_or_fail(), where(), update(), delete()
    Query builder: {model_name}.query().where(...).order_by(...).get()
    """

    __tablename__ = "{table_name}"

    {id_field}
{model_fields}
    # Timestamps (always last)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)
{concerns_config}

class {model_name}Create(BaseModel):
    """
    Schema for creating a {model_name}.
    All validations are enforced here.
    """

{create_fields}


class {model_name}Read(BaseModel):
    """Schema for reading a {model_name}"""

    {id_read_type}
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

    if use_concerns:
        console.print("[cyan]Model Concerns: HasScopes, GuardsAttributes[/cyan]")

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
        console.print("\n[yellow]Run migration:[/yellow]")
        console.print(f'  fastpy db:migrate -m "Create {table_name} table"')


@app.command("make:controller")
def make_controller(name: str = typer.Argument(..., help="Controller name (e.g., BlogPost)")):
    """Create a new controller with CRUD operations using Active Record pattern"""
    controller_name = to_pascal_case(name) + "Controller"
    model_name = to_pascal_case(name)
    file_name = to_snake_case(name) + "_controller.py"
    file_path = Path(f"app/controllers/{file_name}")
    snake_name = to_snake_case(name)

    if file_path.exists():
        console.print(f"[red]Controller already exists:[/red] {file_path}")
        raise typer.Exit(1)

    controller_template = f'''from typing import List, Optional, Dict, Any

from app.models.{snake_name} import {model_name}, {model_name}Create, {model_name}Update
from app.utils.exceptions import NotFoundException


class {controller_name}:
    """
    Controller for {model_name} operations.
    Uses Active Record pattern - all database operations are handled by the model.
    """

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 100) -> List[{model_name}]:
        """Get all non-deleted {snake_name}s"""
        return await {model_name}.query().limit(limit).offset(skip).get()

    @staticmethod
    async def get_paginated(
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """Get paginated {snake_name}s with sorting"""
        query = {model_name}.query()
        if sort_by:
            query = query.order_by(sort_by, sort_order)
        return await query.paginate(page=page, per_page=per_page)

    @staticmethod
    async def get_by_id(id: int) -> {model_name}:
        """Get {snake_name} by ID or raise 404"""
        return await {model_name}.find_or_fail(id)

    @staticmethod
    async def create(data: {model_name}Create) -> {model_name}:
        """
        Create a new {snake_name}.
        Validations are handled by Pydantic schema.
        """
        return await {model_name}.create(**data.model_dump())

    @staticmethod
    async def update(id: int, data: {model_name}Update) -> {model_name}:
        """
        Update a {snake_name}.
        Only provided fields are updated.
        """
        {snake_name} = await {model_name}.find_or_fail(id)
        await {snake_name}.update(**data.model_dump(exclude_unset=True))
        return {snake_name}

    @staticmethod
    async def delete(id: int) -> dict:
        """Soft delete a {snake_name}"""
        {snake_name} = await {model_name}.find_or_fail(id)
        await {snake_name}.delete()
        return {{"message": "{model_name} deleted successfully"}}

    @staticmethod
    async def force_delete(id: int) -> dict:
        """Permanently delete a {snake_name}"""
        {snake_name} = await {model_name}.find_or_fail(id)
        await {snake_name}.delete(force=True)
        return {{"message": "{model_name} permanently deleted"}}

    @staticmethod
    async def restore(id: int) -> {model_name}:
        """Restore a soft deleted {snake_name}"""
        {snake_name} = await {model_name}.query().with_trashed().where(id=id).first()
        if not {snake_name}:
            raise NotFoundException("{model_name} not found")
        await {snake_name}.restore()
        return {snake_name}

    @staticmethod
    async def count() -> int:
        """Count total {snake_name}s"""
        return await {model_name}.query().count()

    @staticmethod
    async def exists(id: int) -> bool:
        """Check if {snake_name} exists"""
        return await {model_name}.query().where(id=id).exists()
'''

    file_path.write_text(controller_template)
    console.print(f"[green]✓[/green] Controller created: {file_path}")
    console.print("[cyan]Using Active Record pattern (no session dependency)[/cyan]")


@app.command("make:route")
def make_route(
    name: str = typer.Argument(..., help="Route name (e.g., BlogPost)"),
    protected: bool = typer.Option(False, "--protected", "-p", help="Add authentication"),
    no_binding: bool = typer.Option(False, "--no-binding", help="Disable route model binding (enabled by default)"),
    validation: bool = typer.Option(False, "--validation", "-v", help="Use FormRequest validation (Laravel-style)"),
):
    """Create a new route file with all CRUD endpoints using Active Record and Route Model Binding"""
    model_name = to_pascal_case(name)
    controller_name = model_name + "Controller"
    file_name = to_snake_case(name) + "_routes.py"
    file_path = Path(f"app/routes/{file_name}")
    route_prefix = pluralize(to_snake_case(name))
    snake_name = to_snake_case(name)

    if file_path.exists():
        console.print(f"[red]Route already exists:[/red] {file_path}")
        raise typer.Exit(1)

    # Auth import if protected
    auth_import = ""
    auth_dep = ""
    if protected:
        auth_import = "\nfrom app.utils.auth import get_current_active_user\nfrom app.models.user import User"
        auth_dep = ", current_user: User = Depends(get_current_active_user)"

    # Route model binding is enabled by default
    use_binding = not no_binding

    # FormRequest validation imports
    if validation:
        validation_import = f"\nfrom app.validation import validated\nfrom app.requests.{snake_name}_request import Create{model_name}Request, Update{model_name}Request"
        create_param = f"request: Create{model_name}Request = validated(Create{model_name}Request)"
        update_param = f"request: Update{model_name}Request = validated(Update{model_name}Request)"
        create_data = "request.validated_data"
        update_data = "request.validated_data"
    else:
        validation_import = ""
        create_param = f"data: {model_name}Create"
        update_param = f"data: {model_name}Update"
        create_data = "data"
        update_data = "data.model_dump(exclude_unset=True)"

    if use_binding:
        binding_import = "\nfrom app.utils.binding import bind_or_fail, bind_trashed"
        route_template = f'''from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status

from app.controllers.{snake_name}_controller import {controller_name}
from app.models.{snake_name} import {model_name}, {model_name}Create, {model_name}Update, {model_name}Read
from app.config.settings import settings{auth_import}{binding_import}{validation_import}

router = APIRouter()


@router.get("/", response_model=List[{model_name}Read])
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000){auth_dep}
):
    """Get all {snake_name}s"""
    return await {controller_name}.get_all(skip, limit)


@router.get("/paginated")
async def get_paginated(
    page: int = Query(1, ge=1),
    per_page: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"){auth_dep}
) -> Dict[str, Any]:
    """Get paginated {snake_name}s with sorting"""
    return await {controller_name}.get_paginated(page, per_page, sort_by, sort_order)


@router.get("/count")
async def count({auth_dep.lstrip(", ") if auth_dep else ""}) -> Dict[str, int]:
    """Get total count"""
    total = await {controller_name}.count()
    return {{"count": total}}


@router.get("/{{id}}", response_model={model_name}Read)
async def get_one({snake_name}: {model_name} = bind_or_fail({model_name}){auth_dep}):
    """Get {snake_name} by ID (auto-resolved via route model binding)"""
    return {snake_name}


@router.head("/{{id}}", status_code=status.HTTP_200_OK)
async def check_exists(id: int{auth_dep}):
    """Check if {snake_name} exists"""
    exists = await {controller_name}.exists(id)
    if not exists:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return None


@router.post("/", response_model={model_name}Read, status_code=201)
async def create({create_param}{auth_dep}):
    """Create a new {snake_name}"""
    return await {controller_name}.create({create_data})


@router.put("/{{id}}", response_model={model_name}Read)
async def update(
    {update_param},
    {snake_name}: {model_name} = bind_or_fail({model_name}){auth_dep}
):
    """Full update a {snake_name} (auto-resolved via route model binding)"""
    await {snake_name}.update(**{update_data})
    return {snake_name}


@router.patch("/{{id}}", response_model={model_name}Read)
async def partial_update(
    {update_param},
    {snake_name}: {model_name} = bind_or_fail({model_name}){auth_dep}
):
    """Partial update a {snake_name} (auto-resolved via route model binding)"""
    await {snake_name}.update(**{update_data})
    return {snake_name}


@router.delete("/{{id}}")
async def delete({snake_name}: {model_name} = bind_or_fail({model_name}){auth_dep}):
    """Soft delete a {snake_name} (auto-resolved via route model binding)"""
    await {snake_name}.delete()
    return {{"message": "{model_name} deleted successfully"}}


@router.post("/{{id}}/restore", response_model={model_name}Read)
async def restore({snake_name}: {model_name} = bind_trashed({model_name}){auth_dep}):
    """Restore a soft deleted {snake_name} (includes trashed records)"""
    await {snake_name}.restore()
    return {snake_name}
'''
    else:
        # Template without binding (legacy mode)
        route_template = f'''from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status

from app.controllers.{snake_name}_controller import {controller_name}
from app.models.{snake_name} import {model_name}, {model_name}Create, {model_name}Update, {model_name}Read
from app.config.settings import settings{auth_import}{validation_import}

router = APIRouter()


@router.get("/", response_model=List[{model_name}Read])
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000){auth_dep}
):
    """Get all {snake_name}s"""
    return await {controller_name}.get_all(skip, limit)


@router.get("/paginated")
async def get_paginated(
    page: int = Query(1, ge=1),
    per_page: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"){auth_dep}
) -> Dict[str, Any]:
    """Get paginated {snake_name}s with sorting"""
    return await {controller_name}.get_paginated(page, per_page, sort_by, sort_order)


@router.get("/count")
async def count({auth_dep.lstrip(", ") if auth_dep else ""}) -> Dict[str, int]:
    """Get total count"""
    total = await {controller_name}.count()
    return {{"count": total}}


@router.get("/{{id}}", response_model={model_name}Read)
async def get_one(id: int{auth_dep}):
    """Get {snake_name} by ID"""
    return await {controller_name}.get_by_id(id)


@router.head("/{{id}}", status_code=status.HTTP_200_OK)
async def check_exists(id: int{auth_dep}):
    """Check if {snake_name} exists"""
    exists = await {controller_name}.exists(id)
    if not exists:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return None


@router.post("/", response_model={model_name}Read, status_code=201)
async def create({create_param}{auth_dep}):
    """Create a new {snake_name}"""
    return await {controller_name}.create({create_data})


@router.put("/{{id}}", response_model={model_name}Read)
async def update(id: int, {update_param}{auth_dep}):
    """Full update a {snake_name}"""
    return await {controller_name}.update(id, {update_data})


@router.patch("/{{id}}", response_model={model_name}Read)
async def partial_update(id: int, {update_param}{auth_dep}):
    """Partial update a {snake_name}"""
    return await {controller_name}.update(id, {update_data})


@router.delete("/{{id}}")
async def delete(id: int{auth_dep}):
    """Soft delete a {snake_name}"""
    return await {controller_name}.delete(id)


@router.post("/{{id}}/restore", response_model={model_name}Read)
async def restore(id: int{auth_dep}):
    """Restore a soft deleted {snake_name}"""
    return await {controller_name}.restore(id)
'''

    file_path.write_text(route_template)
    console.print(f"[green]✓[/green] Route created: {file_path}")

    if protected:
        console.print("[cyan]Routes are protected with authentication[/cyan]")

    if use_binding:
        console.print("[cyan]Routes use route model binding (auto-resolve models from route params)[/cyan]")
    else:
        console.print("[yellow]Route model binding disabled. Use default to enable.[/yellow]")

    if validation:
        console.print("[cyan]Using FormRequest validation (Laravel-style)[/cyan]")
        console.print(f"[yellow]Create request classes:[/yellow]")
        console.print(f"  fastpy make:request Create{model_name} --model {model_name}")
        console.print(f"  fastpy make:request Update{model_name} --model {model_name} --update")

    console.print("[cyan]Using Active Record pattern (no session dependency)[/cyan]")

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
    no_binding: bool = typer.Option(False, "--no-binding", help="Disable route model binding (enabled by default)"),
    validation: bool = typer.Option(False, "--validation", "-v", help="Generate FormRequest classes for validation"),
):
    """
    Create model, controller, and routes all at once.

    Uses Active Record pattern and Route Model Binding by default.

    Examples:
        fastpy make:resource Post -f title:string:required -f body:text -m -p
        fastpy make:resource Product -f name:string:required -f price:decimal:required -m
        fastpy make:resource Contact -f name:string:required -f email:email:required -m -p -v
    """
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

    # Generate FormRequest classes if validation is enabled
    if validation:
        model_name = to_pascal_case(name)
        make_request(f"Create{model_name}", fields=None, model=name, update=False)
        make_request(f"Update{model_name}", fields=None, model=name, update=True)

    make_route(name, protected=protected, no_binding=no_binding, validation=validation)

    if migration:
        table_name = pluralize(to_snake_case(name))
        console.print("\n[yellow]Run migration:[/yellow]")
        console.print(f'  fastpy db:migrate -m "Create {table_name} table"')

    console.print(f"\n[green]✓ Resource '{name}' created successfully![/green]")
    features = ["Active Record", "Route Model Binding"]
    if validation:
        features.append("FormRequest Validation")
    console.print(f"[cyan]Using: {' + '.join(features)}[/cyan]")


# ============================================
# Request Command (Laravel-style FormRequest)
# ============================================

@app.command("make:request")
def make_request(
    name: str = typer.Argument(..., help="Request name (e.g., CreateContact)"),
    fields: List[str] = typer.Option(
        None,
        "--field",
        "-f",
        help="Field with rules (e.g., -f email:required|email|unique:users)",
    ),
    model: str = typer.Option(None, "--model", "-m", help="Associated model name"),
    update: bool = typer.Option(False, "--update", "-u", help="Generate update request (nullable fields)"),
):
    """
    Create a Laravel-style form request class with validation rules.

    Examples:
        fastpy make:request CreateContact -f name:required|max:255 -f email:required|email|unique:contacts
        fastpy make:request UpdateUser --model User --update
        fastpy make:request StorePost -f title:required|max:200 -f body:required
    """
    request_name = to_pascal_case(name)
    if not request_name.endswith("Request"):
        request_name += "Request"

    # Determine file name and path
    base_name = name.replace("Request", "")
    file_name = to_snake_case(base_name) + "_request.py"
    file_path = Path(f"app/requests/{file_name}")

    # Ensure requests directory exists
    Path("app/requests").mkdir(exist_ok=True)
    init_path = Path("app/requests/__init__.py")
    if not init_path.exists():
        init_path.write_text('"""Form request classes for validation."""\n')

    if file_path.exists():
        console.print(f"[red]Request already exists:[/red] {file_path}")
        raise typer.Exit(1)

    # Parse fields and generate rules
    rules = {}
    if fields:
        for field_str in fields:
            # Format: field_name:rules (e.g., email:required|email|unique:users)
            if ":" in field_str:
                parts = field_str.split(":", 1)
                field_name = parts[0]
                rules_str = parts[1]
                rules[field_name] = rules_str
            else:
                rules[field_str] = "required"
    elif model:
        # Default rules for update vs create
        if update:
            rules = {
                "name": "max:255",
                "email": f"email|unique:{pluralize(to_snake_case(model))},email,{{id}}",
            }
        else:
            rules = {
                "name": "required|max:255",
                "email": f"required|email|unique:{pluralize(to_snake_case(model))}",
            }
    else:
        # Default example rules
        rules = {
            "name": "required|max:255",
        }

    # Generate rules dict as string with proper formatting
    rules_lines = []
    for k, v in rules.items():
        rules_lines.append(f'        "{k}": "{v}",')
    rules_str = "\n".join(rules_lines)

    request_template = f'''"""
{request_name} form request.
"""
from typing import ClassVar, Dict

from app.validation.form_request import FormRequest


class {request_name}(FormRequest):
    """
    Form request for {to_snake_case(base_name).replace("_", " ")} validation.

    Usage:
        from app.requests.{to_snake_case(base_name)}_request import {request_name}
        from app.validation import validated

        @router.post("/")
        async def create(request: {request_name} = validated({request_name})):
            return await Model.create(**request.validated_data)
    """

    rules: ClassVar[Dict[str, str]] = {{
{rules_str}
    }}

    # Custom error messages (optional)
    messages: ClassVar[Dict[str, str]] = {{
        # "field.rule": "Custom error message",
    }}

    # Custom attribute names for error messages (optional)
    attributes: ClassVar[Dict[str, str]] = {{
        # "field": "readable name",
    }}

    def authorize(self, user=None) -> bool:
        """
        Determine if the user is authorized to make this request.
        Override to add custom authorization logic.
        """
        return True

    def prepare_for_validation(self, data: Dict) -> Dict:
        """
        Transform data before validation.
        Override to add custom transformations (e.g., trim strings).
        """
        return data
'''

    file_path.write_text(request_template)
    console.print(f"[green]✓[/green] Request created: {file_path}")

    # Show usage example
    console.print("\n[yellow]Usage Example:[/yellow]")
    console.print(f'''
from app.requests.{to_snake_case(base_name)}_request import {request_name}
from app.validation import validated

@router.post("/")
async def create(request: {request_name} = validated({request_name})):
    return await Model.create(**request.validated_data)
''')

    # Show rules
    console.print("[cyan]Validation Rules:[/cyan]")
    for field, field_rules in rules.items():
        console.print(f"  {field}: {field_rules}")


# ============================================
# Service and Repository Commands
# ============================================

@app.command("make:service")
def make_service(name: str = typer.Argument(..., help="Service name (e.g., Payment)")):
    """Create a new service class using Active Record pattern"""
    service_name = to_pascal_case(name) + "Service"
    model_name = to_pascal_case(name)
    file_name = to_snake_case(name) + "_service.py"
    file_path = Path(f"app/services/{file_name}")
    snake_name = to_snake_case(name)

    if file_path.exists():
        console.print(f"[red]Service already exists:[/red] {file_path}")
        raise typer.Exit(1)

    service_template = f'''"""
{model_name} service for business logic.

Uses Active Record pattern - no repository or session dependencies needed.
"""
from typing import Any, Dict, List, Optional

from app.models.{snake_name} import {model_name}, {model_name}Create, {model_name}Update
from app.utils.exceptions import NotFoundException


class {service_name}:
    """
    Service for {model_name} business logic.

    Uses Active Record pattern for database operations.
    Add complex business logic here that doesn't belong in controllers.
    """

    @staticmethod
    async def create({snake_name}_data: {model_name}Create) -> {model_name}:
        """
        Create a new {snake_name} with business logic.

        Add any pre/post processing, validation, or side effects here.
        """
        # Example: Add business logic before creation
        data = {snake_name}_data.model_dump()

        # Create using Active Record
        return await {model_name}.create(**data)

    @staticmethod
    async def update(id: int, {snake_name}_data: {model_name}Update) -> {model_name}:
        """
        Update a {snake_name} with business logic.

        Add any pre/post processing, validation, or side effects here.
        """
        {snake_name} = await {model_name}.find_or_fail(id)

        # Example: Add business logic before update
        data = {snake_name}_data.model_dump(exclude_unset=True)

        # Update using Active Record
        await {snake_name}.update(**data)
        return {snake_name}

    @staticmethod
    async def delete(id: int, force: bool = False) -> None:
        """Delete a {snake_name} (soft delete by default)"""
        {snake_name} = await {model_name}.find_or_fail(id)
        await {snake_name}.delete(force=force)

    @staticmethod
    async def get_by_id(id: int) -> {model_name}:
        """Get {snake_name} by ID or raise 404"""
        return await {model_name}.find_or_fail(id)

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 100) -> List[{model_name}]:
        """Get all {snake_name}s with pagination"""
        return await {model_name}.query().limit(limit).offset(skip).get()

    @staticmethod
    async def get_paginated(page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get paginated {snake_name}s"""
        return await {model_name}.query().paginate(page=page, per_page=per_page)

    # ==========================================================================
    # CUSTOM BUSINESS LOGIC - Add your methods below
    # ==========================================================================

    # Example: Complex business operation
    # @staticmethod
    # async def process_{snake_name}(id: int) -> {model_name}:
    #     """Example of complex business logic"""
    #     {snake_name} = await {model_name}.find_or_fail(id)
    #
    #     # Complex logic here...
    #     # - Validate business rules
    #     # - Call external services
    #     # - Fire events
    #
    #     await {snake_name}.update(processed=True)
    #     return {snake_name}
'''

    file_path.write_text(service_template)
    console.print(f"[green]✓[/green] Service created: {file_path}")
    console.print("[cyan]Using Active Record pattern (no repository dependency)[/cyan]")


@app.command("make:repository")
def make_repository(name: str = typer.Argument(..., help="Repository name (e.g., Payment)")):
    """Create a new repository class (optional - Active Record is preferred)"""
    repo_name = to_pascal_case(name) + "Repository"
    model_name = to_pascal_case(name)
    file_name = to_snake_case(name) + "_repository.py"
    file_path = Path(f"app/repositories/{file_name}")
    snake_name = to_snake_case(name)

    if file_path.exists():
        console.print(f"[red]Repository already exists:[/red] {file_path}")
        raise typer.Exit(1)

    repo_template = f'''"""
{model_name} repository for database operations.

NOTE: In most cases, prefer using Active Record pattern directly:
    - {model_name}.create(**data)
    - {model_name}.find_or_fail(id)
    - {model_name}.query().where(status='active').get()

Use repositories when you need:
    - Complex queries that don't fit in model scopes
    - Custom caching logic
    - Multi-model operations
    - Testing with mocks
"""
from typing import Optional, List, Dict, Any

from app.models.{snake_name} import {model_name}


class {repo_name}:
    """
    Repository for {model_name} queries.

    Uses Active Record under the hood for database operations.
    Add complex query methods that don't fit as model scopes.
    """

    @staticmethod
    async def find_by_id(id: int) -> Optional[{model_name}]:
        """Find {snake_name} by ID"""
        return await {model_name}.find(id)

    @staticmethod
    async def find_or_fail(id: int) -> {model_name}:
        """Find {snake_name} by ID or raise 404"""
        return await {model_name}.find_or_fail(id)

    @staticmethod
    async def all(skip: int = 0, limit: int = 100) -> List[{model_name}]:
        """Get all {snake_name}s"""
        return await {model_name}.query().limit(limit).offset(skip).get()

    @staticmethod
    async def create(data: Dict[str, Any]) -> {model_name}:
        """Create a new {snake_name}"""
        return await {model_name}.create(**data)

    @staticmethod
    async def update(id: int, data: Dict[str, Any]) -> {model_name}:
        """Update a {snake_name}"""
        {snake_name} = await {model_name}.find_or_fail(id)
        await {snake_name}.update(**data)
        return {snake_name}

    @staticmethod
    async def delete(id: int, force: bool = False) -> None:
        """Delete a {snake_name}"""
        {snake_name} = await {model_name}.find_or_fail(id)
        await {snake_name}.delete(force=force)

    @staticmethod
    async def count() -> int:
        """Count total {snake_name}s"""
        return await {model_name}.query().count()

    @staticmethod
    async def exists(id: int) -> bool:
        """Check if {snake_name} exists"""
        return await {model_name}.query().where(id=id).exists()

    # ==========================================================================
    # CUSTOM QUERY METHODS - Use Query Scopes when possible
    # ==========================================================================

    # Example: Complex query that might not fit as a model scope
    # @staticmethod
    # async def get_with_related(id: int) -> Optional[{model_name}]:
    #     """Get {snake_name} with related data (complex join)"""
    #     # Use raw SQLAlchemy if needed for complex queries
    #     pass

    # TIP: For simple queries, prefer model scopes:
    # class {model_name}(BaseModel, HasScopes, table=True):
    #     @classmethod
    #     def scope_active(cls, query):
    #         return query.where(cls.status == 'active')
    #
    # Usage: await {model_name}.query().active().get()
'''

    file_path.write_text(repo_template)
    console.print(f"[green]✓[/green] Repository created: {file_path}")
    console.print("[yellow]Note:[/yellow] Repositories are optional. Prefer Active Record and Query Scopes for most cases.")
    console.print("[cyan]Example:[/cyan] await {model_name}.query().where(status='active').get()")


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
    """Create a test file using Active Record pattern"""
    model_name = to_pascal_case(name)
    file_name = f"test_{to_snake_case(name)}.py"
    file_path = Path(f"tests/{file_name}")
    snake_name = to_snake_case(name)
    plural_name = pluralize(snake_name)

    # Ensure tests directory exists
    Path("tests").mkdir(exist_ok=True)

    if file_path.exists():
        console.print(f"[red]Test file already exists:[/red] {file_path}")
        raise typer.Exit(1)

    test_template = f'''"""
Tests for {model_name} model and endpoints.

Uses Active Record pattern for database operations.
"""
import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from app.models.{snake_name} import {model_name}, {model_name}Create


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def {snake_name}_data():
    """Sample {snake_name} data for testing"""
    return {{
        "name": "Test {model_name}",
        # Add more fields as needed
    }}


@pytest.fixture
async def created_{snake_name}({snake_name}_data):
    """Create a {snake_name} using Active Record for testing"""
    {snake_name} = await {model_name}.create(**{snake_name}_data)
    yield {snake_name}
    # Cleanup: force delete after test
    try:
        await {snake_name}.delete(force=True)
    except Exception:
        pass


# =============================================================================
# ACTIVE RECORD UNIT TESTS
# =============================================================================

class Test{model_name}ActiveRecord:
    """Test Active Record methods on {model_name} model"""

    @pytest.mark.asyncio
    async def test_create_{snake_name}(self, {snake_name}_data):
        """Test creating {snake_name} with Active Record"""
        {snake_name} = await {model_name}.create(**{snake_name}_data)
        assert {snake_name}.id is not None
        assert {snake_name}.name == {snake_name}_data["name"]
        # Cleanup
        await {snake_name}.delete(force=True)

    @pytest.mark.asyncio
    async def test_find_{snake_name}(self, created_{snake_name}):
        """Test finding {snake_name} by ID"""
        found = await {model_name}.find(created_{snake_name}.id)
        assert found is not None
        assert found.id == created_{snake_name}.id

    @pytest.mark.asyncio
    async def test_find_or_fail_{snake_name}(self, created_{snake_name}):
        """Test find_or_fail raises on missing {snake_name}"""
        from app.utils.exceptions import NotFoundException

        # Should succeed
        found = await {model_name}.find_or_fail(created_{snake_name}.id)
        assert found.id == created_{snake_name}.id

        # Should raise NotFoundException
        with pytest.raises(NotFoundException):
            await {model_name}.find_or_fail(99999)

    @pytest.mark.asyncio
    async def test_update_{snake_name}(self, created_{snake_name}):
        """Test updating {snake_name} with Active Record"""
        await created_{snake_name}.update(name="Updated {model_name}")
        assert created_{snake_name}.name == "Updated {model_name}"

        # Verify persisted
        refreshed = await {model_name}.find(created_{snake_name}.id)
        assert refreshed.name == "Updated {model_name}"

    @pytest.mark.asyncio
    async def test_soft_delete_{snake_name}(self, {snake_name}_data):
        """Test soft delete (default behavior)"""
        {snake_name} = await {model_name}.create(**{snake_name}_data)
        await {snake_name}.delete()

        # Should not be found in normal queries
        found = await {model_name}.find({snake_name}.id)
        assert found is None

        # Should be found with with_trashed
        trashed = await {model_name}.query().with_trashed().where(id={snake_name}.id).first()
        assert trashed is not None
        assert trashed.deleted_at is not None

        # Cleanup
        await trashed.delete(force=True)

    @pytest.mark.asyncio
    async def test_restore_{snake_name}(self, {snake_name}_data):
        """Test restoring soft deleted {snake_name}"""
        {snake_name} = await {model_name}.create(**{snake_name}_data)
        await {snake_name}.delete()

        # Restore
        trashed = await {model_name}.query().with_trashed().where(id={snake_name}.id).first()
        await trashed.restore()

        # Should now be found
        found = await {model_name}.find({snake_name}.id)
        assert found is not None
        assert found.deleted_at is None

        # Cleanup
        await found.delete(force=True)

    @pytest.mark.asyncio
    async def test_query_builder(self, {snake_name}_data):
        """Test query builder and scopes"""
        {snake_name} = await {model_name}.create(**{snake_name}_data)

        # Test basic query
        results = await {model_name}.query().get()
        assert len(results) > 0

        # Test count
        count = await {model_name}.query().count()
        assert count > 0

        # Test exists
        exists = await {model_name}.query().where(id={snake_name}.id).exists()
        assert exists is True

        # Cleanup
        await {snake_name}.delete(force=True)


# =============================================================================
# API ENDPOINT TESTS
# =============================================================================

class Test{model_name}Endpoints:
    """Test {model_name} API endpoints"""

    @pytest.mark.asyncio
    async def test_create_{snake_name}_endpoint(self, {snake_name}_data):
        """Test POST /api/{plural_name}/"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/{plural_name}/",
                json={snake_name}_data
            )
            assert response.status_code == 201
            data = response.json()
            assert "id" in data
            assert data["name"] == {snake_name}_data["name"]

    @pytest.mark.asyncio
    async def test_get_{plural_name}_endpoint(self):
        """Test GET /api/{plural_name}/"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/{plural_name}/")
            assert response.status_code == 200
            assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_{snake_name}_by_id_endpoint(self, created_{snake_name}):
        """Test GET /api/{plural_name}/{{id}}"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(f"/api/{plural_name}/{{created_{snake_name}.id}}")
            assert response.status_code == 200
            assert response.json()["id"] == created_{snake_name}.id

    @pytest.mark.asyncio
    async def test_get_{snake_name}_not_found(self):
        """Test GET /api/{plural_name}/{{id}} returns 404"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/{plural_name}/99999")
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_{snake_name}_endpoint(self, created_{snake_name}):
        """Test PUT /api/{plural_name}/{{id}}"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            update_data = {{"name": "Updated {model_name}"}}
            response = await client.put(
                f"/api/{plural_name}/{{created_{snake_name}.id}}",
                json=update_data
            )
            assert response.status_code == 200
            assert response.json()["name"] == "Updated {model_name}"

    @pytest.mark.asyncio
    async def test_delete_{snake_name}_endpoint(self, {snake_name}_data):
        """Test DELETE /api/{plural_name}/{{id}} (soft delete)"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # First create a {snake_name}
            create_response = await client.post(
                "/api/{plural_name}/",
                json={snake_name}_data
            )
            created_id = create_response.json()["id"]

            # Then delete it (soft delete)
            response = await client.delete(f"/api/{plural_name}/{{created_id}}")
            assert response.status_code == 200

            # Verify it's soft deleted (not found via API)
            get_response = await client.get(f"/api/{plural_name}/{{created_id}}")
            assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_restore_{snake_name}_endpoint(self, {snake_name}_data):
        """Test POST /api/{plural_name}/{{id}}/restore"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # Create and soft delete
            create_response = await client.post(
                "/api/{plural_name}/",
                json={snake_name}_data
            )
            created_id = create_response.json()["id"]
            await client.delete(f"/api/{plural_name}/{{created_id}}")

            # Restore
            response = await client.post(f"/api/{plural_name}/{{created_id}}/restore")
            assert response.status_code == 200

            # Verify restored
            get_response = await client.get(f"/api/{plural_name}/{{created_id}}")
            assert get_response.status_code == 200
'''

    file_path.write_text(test_template)
    console.print(f"[green]✓[/green] Test file created: {file_path}")
    console.print("[cyan]Includes Active Record unit tests and API endpoint tests[/cyan]")


@app.command("make:factory")
def make_factory(name: str = typer.Argument(..., help="Factory name (e.g., User)")):
    """Create a test factory with Active Record integration"""
    model_name = to_pascal_case(name)
    factory_name = to_pascal_case(name) + "Factory"
    file_name = f"{to_snake_case(name)}_factory.py"
    file_path = Path(f"tests/factories/{file_name}")
    snake_name = to_snake_case(name)

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

Uses Active Record pattern for database operations.
"""
import factory
from faker import Faker
from typing import Dict, Any, List

from app.models.{snake_name} import {model_name}

fake = Faker()


class {factory_name}(factory.Factory):
    """
    Factory for creating {model_name} instances.

    Usage:
        # Build (in-memory, not persisted)
        {snake_name} = {factory_name}.build()

        # Create dictionary for API testing
        data = {factory_name}.build_dict()

        # Create via Active Record (persisted)
        {snake_name} = await {factory_name}.create_async()

        # Create batch via Active Record
        {snake_name}s = await {factory_name}.create_batch_async(10)
    """

    class Meta:
        model = {model_name}

    # Define attributes (customize based on your model)
    name = factory.LazyFunction(lambda: fake.name())
    # email = factory.LazyFunction(lambda: fake.unique.email())
    # description = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    # is_active = True

    @classmethod
    def build_dict(cls, **kwargs) -> Dict[str, Any]:
        """Build a dictionary for API testing"""
        instance = cls.build(**kwargs)
        return {{
            k: v for k, v in instance.__dict__.items()
            if not k.startswith('_') and v is not None
        }}

    @classmethod
    def build_batch_dict(cls, size: int, **kwargs) -> List[Dict[str, Any]]:
        """Build multiple dictionaries for API testing"""
        return [cls.build_dict(**kwargs) for _ in range(size)]

    @classmethod
    async def create_async(cls, **kwargs) -> {model_name}:
        """
        Create and persist using Active Record.

        Example:
            {snake_name} = await {factory_name}.create_async()
            {snake_name} = await {factory_name}.create_async(name="Custom Name")
        """
        data = cls.build_dict(**kwargs)
        return await {model_name}.create(**data)

    @classmethod
    async def create_batch_async(cls, size: int, **kwargs) -> List[{model_name}]:
        """
        Create multiple records using Active Record.

        Example:
            {snake_name}s = await {factory_name}.create_batch_async(10)
        """
        return [await cls.create_async(**kwargs) for _ in range(size)]

    @classmethod
    async def cleanup(cls, *instances):
        """Force delete instances (for test cleanup)"""
        for instance in instances:
            try:
                await instance.delete(force=True)
            except Exception:
                pass
'''

    file_path.write_text(factory_template)
    console.print(f"[green]✓[/green] Factory created: {file_path}")
    console.print("[cyan]Includes Active Record async methods for database testing[/cyan]")


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
    message: str = typer.Option(None, "--message", "-m", help="Migration message (auto-generates migration first)"),
):
    """
    Run database migrations.

    If -m is provided, auto-generates a new migration first, then runs all migrations.

    Examples:
        fastpy db:migrate                    # Just run pending migrations
        fastpy db:migrate -m "Add posts"     # Generate + run migrations
    """
    # If message provided, auto-generate migration first
    if message:
        console.print(f"[cyan]Generating migration: {message}...[/cyan]")

        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            console.print("[green]✓[/green] Migration generated")
            # Extract migration file from output
            for line in result.stdout.split("\n"):
                if "Generating" in line and ".py" in line:
                    console.print(f"  {line.strip()}")
        else:
            console.print("[red]✗[/red] Failed to generate migration")
            console.print(result.stderr)
            raise typer.Exit(1)

    # Run migrations
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


@app.command("db:make")
def db_make(
    message: str = typer.Argument(..., help="Migration message"),
):
    """
    Generate a new migration without running it.

    Examples:
        fastpy db:make "Create posts table"
        fastpy db:make "Add slug to posts"
    """
    console.print(f"[cyan]Generating migration: {message}...[/cyan]")

    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", message],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        console.print("[green]✓[/green] Migration generated")
        # Extract migration file from output
        for line in result.stdout.split("\n"):
            if "Generating" in line and ".py" in line:
                console.print(f"  {line.strip()}")
        console.print("\n[dim]Run 'fastpy db:migrate' to apply this migration[/dim]")
    else:
        console.print("[red]✗[/red] Failed to generate migration")
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

@app.command("ai:init")
def ai_init(
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

## Key Architectural Principles

This project follows **Laravel-style patterns** adapted for Python/FastAPI:

1. **Active Record Pattern** - Models handle their own persistence (no session passing)
2. **Route Model Binding** - Auto-resolve route `{id}` params to model instances (enabled by default)
3. **Model Concerns** - Laravel-style traits (`HasScopes`, `GuardsAttributes`, `HasCasts`, etc.)
4. **FormRequest Validation** - Laravel-style validation with `rules`, `messages`, `authorize()`
5. **Soft Deletes by Default** - `deleted_at` timestamp, `delete()` vs `delete(force=True)`
6. **Query Scopes** - Reusable, chainable query constraints
7. **Facades for Common Services** - Clean interfaces for Http, Mail, Cache, Storage, Queue, Events
8. **Code Generation with Sensible Defaults** - Generators include best practices automatically
9. **MVC + Repository/Service Pattern Support** - Flexible architecture options
10. **Standard Response Format** - Consistent API responses with `success_response()`, `error_response()`

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
fastpy serve
# Or: uvicorn main:app --reload

# List all routes
fastpy route:list
```

## Code Generation (FastCLI)

```bash
# Generate complete resource with ALL best practices:
# - Active Record pattern
# - Route Model Binding (auto-resolve {id} to model)
# - Model Concerns (HasScopes, GuardsAttributes)
# - Soft deletes
fastpy make:resource Post -f title:string:required,max:200 -f body:text:required -m -p

# With FormRequest validation (Laravel-style)
fastpy make:resource Post -f title:string:required -m -p -v

# Disable route model binding if needed
fastpy make:resource Post -f title:string:required -m -p --no-binding

# Individual generators
fastpy make:model Post -f title:string:required -m      # Model + migration + concerns
fastpy make:controller Post                              # Active Record controller
fastpy make:route Post --protected                       # Routes with binding (default)
fastpy make:route Post --protected --no-binding          # Routes without binding
fastpy make:route Post --protected --validation          # Routes with FormRequest
fastpy make:request CreatePost --model Post              # FormRequest class
fastpy make:request UpdatePost --model Post --update     # Update FormRequest
fastpy make:service Post                                 # Service class
fastpy make:repository Post                              # Repository class
fastpy make:middleware Logging                           # Middleware
fastpy make:test Post                                    # Test file
fastpy make:factory Post                                 # Test factory
fastpy make:seeder Post                                  # Database seeder
fastpy make:enum Status -v active -v inactive            # Enum
fastpy make:exception PaymentFailed -s 400               # Custom exception

# List all commands
fastpy list
```

## Global CLI Commands

```bash
# Project creation
fastpy new my-project                    # Create new Fastpy project
fastpy new my-project --branch dev       # From specific branch

# AI-powered code generation
fastpy ai "Create a blog with posts"     # Natural language generation
fastpy ai "Add comments to posts" -e     # Execute commands automatically

# Configuration & diagnostics
fastpy config                            # Show current config
fastpy config --init                     # Create config file
fastpy init                              # Initialize Fastpy config
fastpy doctor                            # Diagnose environment issues

# Utilities
fastpy version                           # Show CLI version
fastpy upgrade                           # Update CLI to latest
fastpy docs                              # Open documentation
fastpy libs                              # List available facades
fastpy libs http --usage                 # Show facade usage examples
```

## Database Commands

```bash
fastpy db:migrate                         # Run pending migrations
fastpy db:migrate -m "Add posts"          # Generate + run migrations
fastpy db:make "Add slug to posts"        # Generate migration only
fastpy db:rollback                        # Rollback one migration
fastpy db:rollback --steps 3              # Rollback multiple
fastpy db:fresh                           # Drop all & re-migrate
fastpy db:seed                            # Run all seeders
fastpy db:seed --seeder User --count 50   # Run specific seeder
```

## Deployment Commands

```bash
# Initialize deployment configuration
fastpy deploy:init                        # Interactive setup wizard

# Nginx configuration
fastpy deploy:nginx                       # Generate and install nginx config

# SSL certificates (Let's Encrypt)
fastpy deploy:ssl                         # Obtain SSL certificate for domain

# Process managers (choose one)
fastpy deploy:systemd                     # Configure systemd service
fastpy deploy:pm2                         # Configure PM2 (ecosystem.config.js)
fastpy deploy:supervisor                  # Configure Supervisor

# Full deployment (runs all steps)
fastpy deploy:run                         # Deploy with configured process manager

# Status and diagnostics
fastpy deploy:status                      # Show deployment status
fastpy deploy:check                       # Check server requirements
fastpy deploy:install                     # Install missing requirements

# Domain management
fastpy domain:add example.com             # Add domain to CORS whitelist
fastpy domain:remove example.com          # Remove domain
fastpy domain:list                        # List all domains

# Environment variables
fastpy env:set KEY value                  # Set environment variable
fastpy env:get KEY                        # Get environment variable
fastpy env:list                           # List all env variables

# Service control
fastpy service:start                      # Start application
fastpy service:stop                       # Stop application
fastpy service:restart                    # Restart application
fastpy service:status                     # Show service status
fastpy service:logs                       # View application logs
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
- `default:value` - Default value

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
│   ├── base.py         # BaseModel with Active Record methods
│   └── concerns/       # Laravel-style model traits
├── repositories/     # Data access layer (BaseRepository)
├── routes/           # API route definitions
├── seeders/          # Database seeders
├── services/         # Business logic services (BaseService)
└── utils/
    ├── auth.py         # JWT & password hashing
    ├── binding.py      # Route model binding
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

### Active Record Methods

```python
# Create
user = await User.create(name="John", email="john@example.com")

# Find
user = await User.find(1)                          # Returns None if not found
user = await User.find_or_fail(1)                  # Raises NotFoundException

# Query
users = await User.where(active=True)              # List of matching records
user = await User.first_where(email="john@example.com")
user = await User.first_or_fail(email="john@example.com")

# Update
user.name = "Jane"
await user.save()

await user.update(name="Jane", email="jane@example.com")

# Delete
await user.delete()              # Soft delete
await user.delete(force=True)    # Hard delete
```

## Model Concerns (Laravel-style Traits)

Mix in Laravel-style functionality to your models:

```python
from app.models.base import BaseModel
from app.models.concerns import (
    HasCasts, HasAttributes, HasEvents, HasScopes, GuardsAttributes
)

class Post(BaseModel, HasCasts, HasAttributes, HasEvents, HasScopes, GuardsAttributes, table=True):
    # ... model definition
```

### Attribute Casting

Auto-convert database values to Python types:

```python
class Post(BaseModel, HasCasts, table=True):
    _casts = {
        'settings': 'json',        # JSON string <-> dict
        'is_active': 'boolean',    # 1/0 <-> True/False
        'metadata': 'dict',        # Ensure dict type
        'tags': 'list',            # Ensure list type
        'price': 'decimal:2',      # Decimal with 2 places
        'published_at': 'datetime',
    }

# Usage
post.settings = {'featured': True}  # Stored as JSON string
print(post.settings)                 # Returns dict: {'featured': True}
```

**Available cast types:** `boolean`, `integer`, `float`, `string`, `json`, `dict`, `list`, `date`, `datetime`, `decimal:N`

### Accessors and Mutators

Computed properties and value transformers:

```python
from app.models.concerns import accessor, mutator

class User(BaseModel, HasAttributes, table=True):
    first_name: str
    last_name: str
    password: str

    # Virtual attributes to include in serialization
    _appends = ['full_name']
    _hidden = ['password']

    @accessor
    def full_name(self) -> str:
        """Computed property."""
        return f"{self.first_name} {self.last_name}"

    @mutator('password')
    def hash_password(self, value: str) -> str:
        """Transform value before storing."""
        from app.utils.auth import get_password_hash
        return get_password_hash(value)

# Usage
user.full_name          # "John Doe"
user.password = "secret" # Automatically hashed
user.to_dict()          # Includes full_name, excludes password
```

### Model Events

Hook into model lifecycle:

```python
from app.models.concerns import HasEvents, ModelObserver

class UserObserver(ModelObserver):
    def creating(self, user):
        user.uuid = str(uuid4())

    def created(self, user):
        send_welcome_email(user)

    def deleting(self, user):
        # Return False to cancel deletion
        if user.is_admin:
            return False
        return True

class User(BaseModel, HasEvents, table=True):
    @classmethod
    def booted(cls):
        cls.observe(UserObserver())

        # Or inline handlers:
        cls.creating(lambda u: setattr(u, 'uuid', str(uuid4())))
```

**Events:** `creating`, `created`, `updating`, `updated`, `saving`, `saved`, `deleting`, `deleted`, `restoring`, `restored`

### Query Scopes

Reusable query constraints:

```python
class Post(BaseModel, HasScopes, table=True):
    @classmethod
    def scope_published(cls, query):
        return query.where(cls.is_published == True)

    @classmethod
    def scope_popular(cls, query, min_views: int = 1000):
        return query.where(cls.views >= min_views)

    @classmethod
    def scope_by_author(cls, query, author_id: int):
        return query.where(cls.author_id == author_id)

# Fluent query building
posts = await Post.query().published().popular(5000).latest().get()
posts = await Post.query().by_author(1).paginate(page=2, per_page=20)

# With soft deletes
posts = await Post.query().with_trashed().get()   # Include deleted
posts = await Post.query().only_trashed().get()   # Only deleted
```

**QueryBuilder methods:** `where()`, `where_in()`, `where_null()`, `order_by()`, `latest()`, `oldest()`, `limit()`, `offset()`, `get()`, `first()`, `count()`, `exists()`, `paginate()`

### Mass Assignment Protection

Protect against mass assignment vulnerabilities:

```python
class User(BaseModel, GuardsAttributes, table=True):
    # Whitelist: only these can be mass-assigned
    _fillable = ['name', 'email', 'password']

    # OR blacklist: everything except these
    _guarded = ['is_admin', 'role']

# Safe mass assignment
user = await User.create(**request.validated_data)  # Only fillable fields
user.fill(name="John", is_admin=True)               # is_admin ignored

# Bypass protection when needed
user.force_fill(is_admin=True)

# Temporarily disable protection
from app.models.concerns import Unguarded
with Unguarded(User):
    await User.create(is_admin=True)
```

## Route Model Binding

Auto-resolve route parameters to model instances (enabled by default in generated routes):

```python
from app.utils.binding import bind, bind_or_fail, bind_trashed

@router.get("/users/{id}")
async def show_user(user: User = bind(User)):
    return user  # Automatically fetched by ID

@router.get("/posts/{slug}")
async def show_post(post: Post = bind(Post, param="slug", field="slug")):
    return post  # Fetched by slug field

@router.put("/users/{id}")
async def update_user(
    user: User = bind_or_fail(User),
    request: UpdateUserRequest = validated(UpdateUserRequest)
):
    await user.update(**request.validated_data)
    return user

# Include soft-deleted records
@router.post("/posts/{id}/restore")
async def restore_post(post: Post = bind_trashed(Post)):
    await post.restore()
    return post
```

## FormRequest Validation (Laravel-style)

Validate requests using declarative rule classes:

```python
from app.validation import FormRequest, validated

class CreatePostRequest(FormRequest):
    rules = {
        'title': 'required|max:200',
        'body': 'required',
        'slug': 'required|unique:posts',
        'published': 'boolean',
    }

    messages = {
        'title.required': 'Please provide a title.',
        'slug.unique': 'This slug is already taken.',
    }

    def authorize(self, user=None) -> bool:
        return user is not None  # Only authenticated users

# Use with validated() dependency
@router.post("/posts")
async def create(request: CreatePostRequest = validated(CreatePostRequest)):
    return await Post.create(**request.validated_data)

# Combine with Route Model Binding for updates
@router.put("/posts/{id}")
async def update(
    post: Post = bind_or_fail(Post),
    request: UpdatePostRequest = validated(UpdatePostRequest)
):
    await post.update(**request.validated_data)
    return post
```

### Available Validation Rules

| Rule | Description | Example |
|------|-------------|---------|
| `required` | Field is required | `'name': 'required'` |
| `nullable` | Field can be null | `'bio': 'nullable'` |
| `email` | Valid email format | `'email': 'required\\|email'` |
| `max:N` | Maximum length/value | `'title': 'max:200'` |
| `min:N` | Minimum length/value | `'password': 'min:8'` |
| `unique:table` | Unique in database | `'email': 'unique:users'` |
| `exists:table` | Must exist in database | `'user_id': 'exists:users'` |
| `in:a,b,c` | Value in list | `'status': 'in:active,inactive'` |
| `confirmed` | Field matches `{field}_confirmation` | `'password': 'confirmed'` |
| `integer` | Must be integer | `'age': 'integer'` |
| `numeric` | Must be numeric | `'price': 'numeric'` |
| `boolean` | Must be boolean | `'active': 'boolean'` |

## Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user (JSON) |
| `/api/auth/login` | POST | Login (form-data, OAuth2) |
| `/api/auth/login/json` | POST | Login (JSON: email, password) |
| `/api/auth/refresh` | POST | Refresh access token |
| `/api/auth/me` | GET | Get current user |
| `/api/auth/change-password` | POST | Change password |
| `/api/auth/forgot-password` | POST | Request password reset |
| `/api/auth/reset-password` | POST | Reset password with token |
| `/api/auth/verify-email` | POST | Verify email address |
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
    NotFoundException,          # 404
    BadRequestException,        # 400
    UnauthorizedException,      # 401
    ForbiddenException,         # 403
    ConflictException,          # 409
    ValidationException,        # 422
    RateLimitException,         # 429
    ServiceUnavailableException # 503
)

raise NotFoundException("User not found")
raise ServiceUnavailableException("Database unavailable")
```

## Middleware

### Built-in Middleware

| Middleware | Header | Description |
|------------|--------|-------------|
| `RequestIDMiddleware` | `X-Request-ID` | Unique ID for request tracing |
| `TimingMiddleware` | `X-Response-Time` | Response time in ms |
| `RateLimitMiddleware` | `X-RateLimit-*` | Sliding window rate limiting |

### Request ID Middleware
Adds unique request ID for tracing:
```python
# Access in route
from starlette.requests import Request

@router.get("/")
async def route(request: Request):
    request_id = request.state.request_id
```

### Timing Middleware
Logs slow requests (>1s) and adds `X-Response-Time` header.

### Rate Limit Middleware
Configure in `.env`:
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100    # requests per window
RATE_LIMIT_WINDOW=60       # window in seconds
```

Response headers:
- `X-RateLimit-Limit` - Max requests allowed
- `X-RateLimit-Remaining` - Requests remaining
- `X-RateLimit-Reset` - Seconds until reset

### Creating Custom Middleware
```bash
fastpy make:middleware Logging
```

Example middleware structure:
```python
# app/middleware/logging_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Before request
        response = await call_next(request)
        # After request
        return response
```

Register in `main.py`:
```python
from app.middleware.logging_middleware import LoggingMiddleware
app.add_middleware(LoggingMiddleware)
```

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

## Fastpy Libs

Fastpy provides clean facades for common tasks. Import from `fastpy_cli.libs`:

```python
from fastpy_cli.libs import Http, Mail, Cache, Storage, Queue, Event, Notify, Hash, Crypt, Job, Notification
```

### Available Facades

| Facade | Description |
|--------|-------------|
| `Http` | HTTP client (GET, POST, PUT, DELETE) |
| `Mail` | Email sending (SMTP, SendGrid, Mailgun, SES) |
| `Cache` | Caching (Memory, File, Redis) |
| `Storage` | File storage (Local, S3, Memory) |
| `Queue` | Job queues (Sync, Memory, Redis, Database) |
| `Event` | Event dispatcher with listeners |
| `Notify` | Multi-channel notifications (Mail, Database, Slack, SMS) |
| `Hash` | Password hashing (bcrypt, argon2, sha256) |
| `Crypt` | Data encryption (Fernet, AES-256-CBC) |

### Http Facade

```python
from fastpy_cli.libs import Http

# Basic requests
response = Http.get('https://api.example.com/users')
response = Http.post('https://api.example.com/users', json={'name': 'John'})
response = Http.put(url, json=data)
response = Http.delete(url)

# With authentication
response = Http.with_token('bearer-token').get('/api/protected')
response = Http.with_basic_auth('user', 'pass').get(url)

# With headers
response = Http.with_headers({'X-Custom': 'value'}).get(url)

# Testing (fake responses)
Http.fake({'https://api.example.com/*': {'status': 200, 'json': {'ok': True}}})
response = Http.get('https://api.example.com/test')
Http.assert_sent('https://api.example.com/test')
```

### Mail Facade

```python
from fastpy_cli.libs import Mail

# Send email with template
Mail.to('user@example.com').subject('Welcome!').send('welcome', {'name': 'John'})

# Multiple recipients
Mail.to(['user1@example.com', 'user2@example.com']) \\
    .cc('manager@example.com') \\
    .bcc('archive@example.com') \\
    .subject('Team Update') \\
    .send('update', {'message': 'Hello team!'})

# Raw HTML
Mail.to('user@example.com').subject('Hello').html('<h1>Hello World</h1>').send()

# Attachments
Mail.to(email).attach('/path/to/file.pdf').send('invoice', data)

# Use specific driver
Mail.driver('sendgrid').to('user@example.com').send('template', data)
```

### Cache Facade

```python
from fastpy_cli.libs import Cache

# Store value
Cache.put('key', 'value', ttl=3600)  # 1 hour

# Get value
value = Cache.get('key', default='fallback')

# Check existence
if Cache.has('key'):
    print('Key exists')

# Remember (get or compute)
users = Cache.remember('users', lambda: fetch_users_from_db(), ttl=600)

# Delete
Cache.forget('key')
Cache.flush()  # Clear all

# Cache tags (for grouped invalidation)
Cache.tags(['users', 'active']).put('user:1', user_data)
Cache.tags(['users']).flush()  # Clear all user-related cache

# Increment/decrement
Cache.increment('visits')
Cache.decrement('stock', 5)

# Use specific store
Cache.store('redis').put('key', 'value')
```

### Storage Facade

```python
from fastpy_cli.libs import Storage

# Store file
Storage.put('avatars/user.jpg', file_content)

# Get file content
content = Storage.get('avatars/user.jpg')

# Get public URL
url = Storage.url('avatars/user.jpg')

# Check existence
if Storage.exists('avatars/user.jpg'):
    print('File exists')

# Delete
Storage.delete('avatars/user.jpg')

# List files
files = Storage.list('avatars/')

# Copy/move
Storage.copy('source.jpg', 'dest.jpg')
Storage.move('old.jpg', 'new.jpg')

# Use specific disk
Storage.disk('s3').put('backups/data.zip', content)
url = Storage.disk('s3').url('backups/data.zip')
```

### Queue/Jobs Facade

```python
from fastpy_cli.libs import Queue, Job

# Define a job
class SendEmailJob(Job):
    def __init__(self, user_id: int, template: str):
        self.user_id = user_id
        self.template = template

    def handle(self):
        user = get_user(self.user_id)
        send_email(user.email, self.template)

# Push job to queue
Queue.push(SendEmailJob(user_id=1, template='welcome'))

# Delay job (seconds)
Queue.later(60, SendEmailJob(user_id=1, template='reminder'))

# Chain jobs (run sequentially)
Queue.chain([
    ProcessOrderJob(order_id=1),
    SendConfirmationJob(order_id=1),
    UpdateInventoryJob(order_id=1),
])

# Use specific queue
Queue.on('emails').push(SendEmailJob(user_id=1, template='welcome'))
```

### Event Facade

```python
from fastpy_cli.libs import Event

# Listen to events
Event.listen('user.registered', lambda data: send_welcome_email(data['user']))
Event.listen('order.created', lambda data: notify_admin(data['order']))

# Dispatch event
Event.dispatch('user.registered', {'user': user})

# Wildcard listeners
Event.listen('user.*', lambda data: log_user_activity(data))
Event.listen('*.created', lambda data: log_creation(data))

# Event subscriber class
class UserSubscriber:
    def subscribe(self, events):
        events.listen('user.registered', self.on_registered)
        events.listen('user.deleted', self.on_deleted)

    def on_registered(self, data):
        print(f"User registered: {data['user'].id}")

    def on_deleted(self, data):
        print(f"User deleted: {data['user'].id}")

Event.subscribe(UserSubscriber())
```

### Notifications Facade

```python
from fastpy_cli.libs import Notify, Notification

# Define notification
class OrderShippedNotification(Notification):
    def __init__(self, order):
        self.order = order

    def via(self, notifiable) -> list:
        return ['mail', 'database', 'slack']

    def to_mail(self, notifiable) -> dict:
        return {
            'subject': 'Your order has shipped!',
            'template': 'order_shipped',
            'data': {'order': self.order}
        }

    def to_database(self, notifiable) -> dict:
        return {
            'type': 'order_shipped',
            'data': {'order_id': self.order.id}
        }

    def to_slack(self, notifiable) -> dict:
        return {'text': f'Order #{self.order.id} has shipped!'}

    def to_sms(self, notifiable) -> str:
        return f'Order #{self.order.id} shipped!'

# Send notification
Notify.send(user, OrderShippedNotification(order))

# Send to multiple users
Notify.send(users, OrderShippedNotification(order))

# On-demand (anonymous) notification
Notify.route('mail', 'guest@example.com') \\
    .route('slack', '#orders') \\
    .notify(OrderShippedNotification(order))
```

### Hash Facade

```python
from fastpy_cli.libs import Hash

# Hash a password
hashed = Hash.make('password')

# Verify password
if Hash.check('password', hashed):
    print('Password is valid!')

# Check if rehash needed (for upgrading security parameters)
if Hash.needs_rehash(hashed):
    new_hash = Hash.make('password')

# Use specific algorithm
hashed = Hash.driver('argon2').make('password')  # argon2 (recommended for new apps)
hashed = Hash.driver('bcrypt').make('password')  # bcrypt (default)
hashed = Hash.driver('sha256').make('password')  # PBKDF2-SHA256 (fallback)

# Configure bcrypt rounds
Hash.configure('bcrypt', {'rounds': 14})
```

### Crypt Facade

```python
from fastpy_cli.libs import Crypt

# Generate encryption key (do once, save to .env)
key = Crypt.generate_key()
# Add to .env: APP_KEY=<key>

# Set key (or use APP_KEY environment variable)
Crypt.set_key(key)

# Encrypt data
encrypted = Crypt.encrypt('secret data')

# Encrypt complex data (auto JSON serialized)
encrypted = Crypt.encrypt({'user_id': 123, 'token': 'abc'})

# Decrypt
data = Crypt.decrypt(encrypted)

# Use specific driver
encrypted = Crypt.driver('aes').encrypt('secret')  # AES-256-CBC
```

### Libs CLI Command

```bash
# List all available libs
fastpy libs

# View lib info and usage examples
fastpy libs http --usage
fastpy libs mail --usage
fastpy libs cache --usage
fastpy libs queue --usage
```

## User-Specific Instructions

- All table Actions should be in an ActionGroup
- Use JSON for all POST/PUT/PATCH request bodies
- Always use async/await for database operations
- Filter soft deletes in queries: `where(Model.deleted_at.is_(None))`
- **Prefer Fastpy libs** over raw implementations for: HTTP requests, email sending, caching, file storage, job queues, events, notifications, password hashing, and encryption
- When generating code that needs any of the above features, use the appropriate facade from `fastpy_cli.libs`
'''
    return base_content




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
        console.print("  fastpy update --cli          # Update CLI only")
        console.print("  fastpy update --utils        # Update utility files")
        console.print("  fastpy update --middleware   # Update middleware")
        console.print("  fastpy update --all          # Update all files")
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


# ============================================
# Deploy Commands (Production Deployment)
# ============================================

@app.command("deploy:init")
def cmd_deploy_init(
    app_name: str = typer.Option(None, "--name", "-n", help="Application name"),
    domain: str = typer.Option(None, "--domain", "-d", help="Domain name"),
    port: int = typer.Option(8000, "--port", "-p", help="Application port"),
    non_interactive: bool = typer.Option(False, "--yes", "-y", help="Non-interactive mode"),
):
    """
    Initialize deployment configuration for production.

    Creates .fastpy/deploy.json with server configuration.

    Examples:
        fastpy deploy:init
        fastpy deploy:init --name myapp --domain api.example.com
        fastpy deploy:init -d api.example.com -p 8000 -y
    """
    from app.cli.deploy import deploy_init
    deploy_init(
        app_name=app_name,
        domain=domain,
        port=port,
        interactive=not non_interactive
    )


@app.command("deploy:nginx")
def cmd_deploy_nginx(
    apply: bool = typer.Option(False, "--apply", "-a", help="Apply configuration (requires sudo)"),
):
    """
    Generate Nginx reverse proxy configuration.

    Creates optimized Nginx config with:
    - Reverse proxy to your FastAPI app
    - WebSocket support
    - Security headers
    - Gzip compression
    - SSL configuration (if enabled)

    Examples:
        fastpy deploy:nginx              # Generate config file
        sudo fastpy deploy:nginx --apply # Apply to Nginx
    """
    from app.cli.deploy import deploy_nginx
    deploy_nginx(apply=apply)


@app.command("deploy:ssl")
def cmd_deploy_ssl():
    """
    Setup SSL/TLS with Let's Encrypt.

    Obtains and configures SSL certificate using certbot.
    Requires sudo and a valid domain pointing to this server.

    Example:
        sudo fastpy deploy:ssl
    """
    from app.cli.deploy import deploy_ssl
    deploy_ssl()


@app.command("deploy:systemd")
def cmd_deploy_systemd(
    apply: bool = typer.Option(False, "--apply", "-a", help="Apply configuration (requires sudo)"),
):
    """
    Generate systemd service for process management.

    Creates a systemd service that:
    - Runs your app with Gunicorn/Uvicorn
    - Auto-restarts on failure
    - Starts on boot
    - Includes security hardening

    Examples:
        fastpy deploy:systemd              # Generate service file
        sudo fastpy deploy:systemd --apply # Install and start service
    """
    from app.cli.deploy import deploy_systemd
    deploy_systemd(apply=apply)


@app.command("deploy:pm2")
def cmd_deploy_pm2(
    apply: bool = typer.Option(False, "--apply", "-a", help="Start with PM2"),
):
    """
    Generate PM2 ecosystem configuration.

    Creates ecosystem.config.js for PM2 process management.
    PM2 is ideal for Node.js environments or when you prefer
    a universal process manager.

    Features:
    - Auto-restart on failure
    - Log management
    - Cluster mode support
    - Easy monitoring (pm2 monit)

    Examples:
        fastpy deploy:pm2              # Generate config
        fastpy deploy:pm2 --apply      # Generate and start
    """
    from app.cli.deploy import deploy_pm2
    deploy_pm2(apply=apply)


@app.command("deploy:supervisor")
def cmd_deploy_supervisor(
    apply: bool = typer.Option(False, "--apply", "-a", help="Apply configuration (requires sudo)"),
):
    """
    Generate Supervisor configuration.

    Creates a Supervisor config file for process management.
    Supervisor is a reliable, traditional process manager.

    Features:
    - Auto-restart on failure
    - Process groups
    - Web interface (optional)
    - Log rotation

    Examples:
        fastpy deploy:supervisor              # Generate config
        sudo fastpy deploy:supervisor --apply # Install and start
    """
    from app.cli.deploy import deploy_supervisor
    deploy_supervisor(apply=apply)


@app.command("deploy:run")
def cmd_deploy_run(
    apply: bool = typer.Option(False, "--apply", "-a", help="Apply all configurations (requires sudo)"),
):
    """
    Run full deployment (Nginx + process manager + SSL).

    Generates all deployment configurations and optionally applies them.
    Uses the process manager configured in deploy:init (systemd, pm2, or supervisor).

    Examples:
        fastpy deploy:run              # Generate all configs
        sudo fastpy deploy:run --apply # Apply everything
    """
    from app.cli.deploy import deploy_full
    deploy_full(apply=apply)


@app.command("deploy:status")
def cmd_deploy_status():
    """
    Show deployment status and configuration.

    Displays:
    - Current configuration
    - Service status
    - Nginx status
    - SSL certificate status
    """
    from app.cli.deploy import show_status
    show_status()


@app.command("deploy:check")
def cmd_deploy_check():
    """
    Check server requirements for deployment.

    Verifies that all required packages are installed:
    - nginx
    - certbot
    - gunicorn
    - uvicorn
    """
    from app.cli.deploy import check_requirements

    requirements = check_requirements()

    table = Table(title="Server Requirements")
    table.add_column("Package", style="cyan")
    table.add_column("Status", style="green")

    for pkg, installed in requirements.items():
        status = "[green]✓ Installed[/green]" if installed else "[red]✗ Missing[/red]"
        table.add_row(pkg, status)

    console.print(table)

    missing = [k for k, v in requirements.items() if not v]
    if missing:
        console.print(f"\n[yellow]Missing packages:[/yellow] {', '.join(missing)}")
        console.print("Run: [cyan]sudo fastpy deploy:install[/cyan] to install them")


@app.command("deploy:install")
def cmd_deploy_install():
    """
    Install server requirements (nginx, certbot, gunicorn).

    Requires sudo. Installs:
    - nginx
    - certbot
    - python3-certbot-nginx
    - gunicorn
    - uvicorn[standard]

    Example:
        sudo fastpy deploy:install
    """
    from app.cli.deploy import install_requirements
    install_requirements()


# ============================================
# Domain Management Commands
# ============================================

@app.command("domain:add")
def cmd_domain_add(
    domain: str = typer.Argument(..., help="Domain to add (e.g., https://app.example.com)"),
    frontend: bool = typer.Option(False, "--frontend", "-f", help="Mark as frontend domain"),
):
    """
    Add a domain to allowed CORS origins.

    Adds the domain to your deployment config and updates .env.
    Use --frontend flag for frontend applications.

    Examples:
        fastpy domain:add https://app.example.com
        fastpy domain:add https://dashboard.example.com --frontend
        fastpy domain:add example.com  # Auto-adds https://
    """
    from app.cli.deploy import domain_add
    domain_type = "frontend" if frontend else "cors"
    domain_add(domain, domain_type)


@app.command("domain:remove")
def cmd_domain_remove(
    domain: str = typer.Argument(..., help="Domain to remove"),
):
    """
    Remove a domain from allowed origins.

    Example:
        fastpy domain:remove https://old-app.example.com
    """
    from app.cli.deploy import domain_remove
    domain_remove(domain)


@app.command("domain:list")
def cmd_domain_list():
    """
    List all configured domains for CORS.

    Shows:
    - Primary domain
    - CORS origins
    - Frontend domains
    """
    from app.cli.deploy import domain_list
    domain_list()


# ============================================
# Environment Management Commands
# ============================================

@app.command("env:set")
def cmd_env_set(
    key_value: str = typer.Argument(..., help="KEY=value pair to set"),
):
    """
    Set an environment variable in .env file.

    Examples:
        fastpy env:set DATABASE_URL=postgresql://...
        fastpy env:set DEBUG=false
        fastpy env:set "SECRET_KEY=my-secret-key"
    """
    if "=" not in key_value:
        console.print("[red]Error:[/red] Format must be KEY=value")
        raise typer.Exit(1)

    key, value = key_value.split("=", 1)
    from app.cli.deploy import env_set
    env_set(key, value)


@app.command("env:get")
def cmd_env_get(
    key: str = typer.Argument(..., help="Environment variable key"),
):
    """
    Get an environment variable from .env file.

    Example:
        fastpy env:get DATABASE_URL
    """
    from app.cli.deploy import env_get
    value = env_get(key)
    if value is not None:
        console.print(f"{key}={value}")
    else:
        console.print(f"[yellow]{key} not found[/yellow]")


@app.command("env:list")
def cmd_env_list():
    """
    List all environment variables from .env file.

    Sensitive values (secrets, passwords, keys) are masked.
    """
    from app.cli.deploy import env_list
    env_list()


# ============================================
# Service Management Commands
# ============================================

@app.command("service:start")
def cmd_service_start():
    """Start the application service."""
    from app.cli.deploy import DeployConfig

    if not DeployConfig.exists():
        console.print("[red]No deployment config found. Run 'fastpy deploy:init' first.[/red]")
        raise typer.Exit(1)

    config = DeployConfig.load()
    result = subprocess.run(
        ["sudo", "systemctl", "start", config.app_name],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        console.print(f"[green]✓[/green] Service {config.app_name} started")
    else:
        console.print(f"[red]✗[/red] Failed to start: {result.stderr}")


@app.command("service:stop")
def cmd_service_stop():
    """Stop the application service."""
    from app.cli.deploy import DeployConfig

    if not DeployConfig.exists():
        console.print("[red]No deployment config found.[/red]")
        raise typer.Exit(1)

    config = DeployConfig.load()
    result = subprocess.run(
        ["sudo", "systemctl", "stop", config.app_name],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        console.print(f"[green]✓[/green] Service {config.app_name} stopped")
    else:
        console.print(f"[red]✗[/red] Failed to stop: {result.stderr}")


@app.command("service:restart")
def cmd_service_restart():
    """Restart the application service."""
    from app.cli.deploy import DeployConfig

    if not DeployConfig.exists():
        console.print("[red]No deployment config found.[/red]")
        raise typer.Exit(1)

    config = DeployConfig.load()
    result = subprocess.run(
        ["sudo", "systemctl", "restart", config.app_name],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        console.print(f"[green]✓[/green] Service {config.app_name} restarted")
    else:
        console.print(f"[red]✗[/red] Failed to restart: {result.stderr}")


@app.command("service:status")
def cmd_service_status():
    """Show application service status."""
    from app.cli.deploy import DeployConfig

    if not DeployConfig.exists():
        console.print("[red]No deployment config found.[/red]")
        raise typer.Exit(1)

    config = DeployConfig.load()
    result = subprocess.run(
        ["systemctl", "status", config.app_name],
        capture_output=True, text=True
    )
    console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)


@app.command("service:logs")
def cmd_service_logs(
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines to show"),
):
    """
    View application logs.

    Examples:
        fastpy service:logs
        fastpy service:logs -f        # Follow logs
        fastpy service:logs -n 100    # Last 100 lines
    """
    from app.cli.deploy import DeployConfig

    if not DeployConfig.exists():
        console.print("[red]No deployment config found.[/red]")
        raise typer.Exit(1)

    config = DeployConfig.load()

    cmd = ["journalctl", "-u", config.app_name, f"-n{lines}"]
    if follow:
        cmd.append("-f")

    subprocess.run(cmd)


# ============================================
# Setup Commands
# ============================================

@app.command("setup")
def cmd_setup(
    skip_db: bool = typer.Option(False, "--skip-db", help="Skip database configuration"),
    skip_migrations: bool = typer.Option(False, "--skip-migrations", help="Skip migrations"),
    skip_admin: bool = typer.Option(False, "--skip-admin", help="Skip admin user creation"),
    skip_hooks: bool = typer.Option(False, "--skip-hooks", help="Skip pre-commit hooks"),
):
    """
    Complete interactive project setup.

    Run after creating venv and installing dependencies. Handles database config,
    migrations, admin user, and pre-commit hooks.

    Examples:
        fastpy setup                    # Full interactive setup
        fastpy setup --skip-db          # Skip database configuration
        fastpy setup --skip-migrations  # Setup without running migrations
    """
    from app.cli.setup import full_setup
    full_setup(
        skip_db=skip_db,
        skip_migrations=skip_migrations,
        skip_admin=skip_admin,
        skip_hooks=skip_hooks,
    )


@app.command("setup:env")
def cmd_setup_env():
    """
    Initialize .env file from .env.example.

    Creates backup if .env already exists.
    """
    from app.cli.setup import setup_env
    setup_env()


@app.command("setup:db")
def cmd_setup_db(
    driver: str = typer.Option(None, "--driver", "-d", help="Database driver (mysql, postgresql, sqlite)"),
    host: str = typer.Option(None, "--host", "-h", help="Database host"),
    port: int = typer.Option(None, "--port", "-p", help="Database port"),
    username: str = typer.Option(None, "--username", "-u", help="Database username"),
    password: str = typer.Option(None, "--password", help="Database password"),
    database: str = typer.Option(None, "--database", "-n", help="Database name"),
    no_create: bool = typer.Option(False, "--no-create", help="Don't create database"),
    non_interactive: bool = typer.Option(False, "--yes", "-y", help="Non-interactive mode"),
):
    """
    Configure database connection.

    Supports MySQL, PostgreSQL, and SQLite. Updates .env file and optionally
    creates the database.

    Examples:
        fastpy setup:db                              # Interactive setup
        fastpy setup:db -d mysql -n my_app          # MySQL with database name
        fastpy setup:db -d postgresql --no-create   # PostgreSQL without auto-create
        fastpy setup:db -d sqlite                   # SQLite (no server needed)
    """
    from app.cli.setup import setup_db
    setup_db(
        driver=driver,
        host=host,
        port=port,
        username=username,
        password=password,
        database=database,
        create=not no_create,
        interactive=not non_interactive,
    )


@app.command("setup:secret")
def cmd_setup_secret(
    length: int = typer.Option(64, "--length", "-l", help="Secret key length"),
):
    """
    Generate secure secret key for JWT tokens.

    Uses Python's cryptographic random for security.
    Updates SECRET_KEY in .env file.

    Examples:
        fastpy setup:secret             # Generate 64-char key
        fastpy setup:secret -l 128      # Generate 128-char key
    """
    from app.cli.setup import setup_secret
    setup_secret(length=length)


@app.command("setup:hooks")
def cmd_setup_hooks():
    """
    Install pre-commit hooks for code quality.

    Requires git repository and pre-commit package.

    Examples:
        fastpy setup:hooks
    """
    from app.cli.setup import setup_hooks
    setup_hooks()


@app.command("make:admin")
def cmd_make_admin(
    name: str = typer.Option(None, "--name", "-n", help="Admin name"),
    email: str = typer.Option(None, "--email", "-e", help="Admin email"),
    password: str = typer.Option(None, "--password", "-p", help="Admin password"),
    non_interactive: bool = typer.Option(False, "--yes", "-y", help="Non-interactive mode"),
):
    """
    Create a super admin user.

    Requires database to be configured and migrations to be run.

    Examples:
        fastpy make:admin                                           # Interactive
        fastpy make:admin -n "Admin" -e admin@example.com -p secret # Non-interactive
    """
    from app.cli.setup import setup_admin
    setup_admin(
        name=name,
        email=email,
        password=password,
        interactive=not non_interactive,
    )


@app.command("db:setup")
def cmd_db_setup(
    auto_generate: bool = typer.Option(True, "--auto-generate/--no-auto-generate", help="Auto-generate initial migration"),
):
    """
    Run database migrations.

    Optionally generates initial migration if none exist.

    Examples:
        fastpy db:setup                 # Run migrations
        fastpy db:setup --no-auto-generate  # Skip auto-generation
    """
    from app.cli.setup import run_migrations
    run_migrations(auto_generate=auto_generate)


# ============================================
# Update List Command with Deploy Commands
# ============================================

# List Command - All available commands
@app.command("list")
def list_all_commands():
    """List all available commands with examples"""
    table = Table(title="Fastpy Commands")
    table.add_column("Command", style="cyan", width=25)
    table.add_column("Description", style="green", width=35)
    table.add_column("Example", style="yellow")

    commands = [
        # Server
        ("serve", "Start dev server", "fastpy serve --port 8000"),
        ("route:list", "List all routes", "fastpy route:list"),
        # Code generation
        ("make:model", "Create model", "fastpy make:model Post -f title:string:required -m"),
        ("make:controller", "Create controller", "fastpy make:controller Post"),
        ("make:route", "Create routes", "fastpy make:route Post -p"),
        ("make:resource", "Create all at once", "fastpy make:resource Post -i -m -p"),
        ("make:request", "Create form request", "fastpy make:request CreatePost -f title:required"),
        ("make:service", "Create service", "fastpy make:service Payment"),
        ("make:repository", "Create repository", "fastpy make:repository Payment"),
        ("make:middleware", "Create middleware", "fastpy make:middleware Logging"),
        ("make:test", "Create test file", "fastpy make:test User"),
        ("make:factory", "Create test factory", "fastpy make:factory User"),
        ("make:seeder", "Create seeder", "fastpy make:seeder User"),
        ("make:enum", "Create enum", "fastpy make:enum Status -v active -v inactive"),
        ("make:exception", "Create exception", "fastpy make:exception NotFound -s 404"),
        # Database
        ("db:migrate", "Run migrations", "fastpy db:migrate -m 'Add posts'"),
        ("db:make", "Generate migration", "fastpy db:make 'Add slug'"),
        ("db:rollback", "Rollback migrations", "fastpy db:rollback -s 2"),
        ("db:fresh", "Fresh database", "fastpy db:fresh"),
        ("db:seed", "Run seeders", "fastpy db:seed -c 20"),
        # Deployment
        ("deploy:init", "Initialize deployment", "fastpy deploy:init -d api.example.com"),
        ("deploy:nginx", "Generate Nginx config", "fastpy deploy:nginx --apply"),
        ("deploy:ssl", "Setup SSL certificate", "sudo fastpy deploy:ssl"),
        ("deploy:systemd", "Create systemd service", "fastpy deploy:systemd --apply"),
        ("deploy:run", "Full deployment", "sudo fastpy deploy:run --apply"),
        ("deploy:status", "Show deploy status", "fastpy deploy:status"),
        ("deploy:check", "Check requirements", "fastpy deploy:check"),
        ("deploy:install", "Install requirements", "sudo fastpy deploy:install"),
        # Domain management
        ("domain:add", "Add CORS domain", "fastpy domain:add https://app.example.com"),
        ("domain:remove", "Remove domain", "fastpy domain:remove https://old.example.com"),
        ("domain:list", "List domains", "fastpy domain:list"),
        # Environment
        ("env:set", "Set env variable", "fastpy env:set DEBUG=false"),
        ("env:get", "Get env variable", "fastpy env:get DATABASE_URL"),
        ("env:list", "List env variables", "fastpy env:list"),
        # Service management
        ("service:start", "Start service", "sudo fastpy service:start"),
        ("service:stop", "Stop service", "sudo fastpy service:stop"),
        ("service:restart", "Restart service", "sudo fastpy service:restart"),
        ("service:status", "Service status", "fastpy service:status"),
        ("service:logs", "View logs", "fastpy service:logs -f"),
        # Setup
        ("setup", "Full interactive setup", "fastpy setup"),
        ("setup:env", "Initialize .env file", "fastpy setup:env"),
        ("setup:db", "Configure database", "fastpy setup:db -d mysql"),
        ("setup:secret", "Generate secret key", "fastpy setup:secret"),
        ("setup:hooks", "Install pre-commit", "fastpy setup:hooks"),
        ("make:admin", "Create admin user", "fastpy make:admin"),
        # Other
        ("ai:init", "AI config file", "fastpy ai:init claude"),
        ("update", "Update Fastpy files", "fastpy update --cli"),
    ]

    for cmd, desc, example in commands:
        table.add_row(cmd, desc, example)

    console.print(table)

    console.print("\n[cyan]Field Types:[/cyan]")
    console.print(f"  {', '.join(FIELD_TYPES.keys())}")

    console.print("\n[cyan]Validation Rules:[/cyan]")
    console.print("  required, nullable, unique, index, max:N, min:N, gt:N, lt:N, ge:N, le:N, foreign:table.column")

    console.print("\n[cyan]Deploy Quick Start:[/cyan]")
    console.print("  1. fastpy deploy:init                    # Configure deployment")
    console.print("  2. fastpy domain:add https://frontend.com  # Add frontend domain")
    console.print("  3. sudo fastpy deploy:run --apply        # Deploy everything")


if __name__ == "__main__":
    app()
