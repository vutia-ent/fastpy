#!/usr/bin/env python3
"""
Code generation CLI tool for FastAPI project
Usage: python cli.py [command] or artisan [command] (after pip install -e .)
"""
import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
import re

app = typer.Typer(help="Code generation CLI for FastAPI")
console = Console()


def to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case"""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase"""
    return "".join(word.capitalize() for word in name.split("_"))


@app.command("make:model")
def make_model(
    name: str = typer.Argument(..., help="Model name (e.g., BlogPost)"),
    migration: bool = typer.Option(False, "--migration", "-m", help="Create migration"),
):
    """Create a new model"""
    model_name = to_pascal_case(name)
    table_name = to_snake_case(name) + "s"  # Pluralize
    file_name = to_snake_case(name) + ".py"
    file_path = Path(f"app/models/{file_name}")

    if file_path.exists():
        console.print(f"[red]Model already exists:[/red] {file_path}")
        raise typer.Exit(1)

    model_template = f'''from typing import Optional
from sqlmodel import Field
from app.models.base import BaseModel


class {model_name}(BaseModel, table=True):
    """
    {model_name} model.
    Table name: {table_name}
    """

    __tablename__ = "{table_name}"

    name: str = Field(nullable=False, max_length=255)
    # Add more fields here


class {model_name}Create(BaseModel):
    """Schema for creating a {model_name}"""

    name: str = Field(min_length=1, max_length=255)


class {model_name}Read(BaseModel):
    """Schema for reading a {model_name}"""

    id: int
    name: str


class {model_name}Update(BaseModel):
    """Schema for updating a {model_name}"""

    name: Optional[str] = Field(default=None, max_length=255)
'''

    file_path.write_text(model_template)
    console.print(f"[green]✓[/green] Model created: {file_path}")

    # Update alembic env.py
    env_path = Path("alembic/env.py")
    if env_path.exists():
        content = env_path.read_text()
        import_line = f"from app.models.{to_snake_case(name)} import {model_name}  # noqa"
        if import_line not in content:
            # Add import after existing model imports
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
        """Create a new {to_snake_case(name)}"""
        item = {model_name}(**data.model_dump())
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item

    @staticmethod
    async def update(session: AsyncSession, id: int, data: {model_name}Update) -> {model_name}:
        """Update a {to_snake_case(name)}"""
        item = await {controller_name}.get_by_id(session, id)

        # Update fields
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
def make_route(name: str = typer.Argument(..., help="Route name (e.g., BlogPost)")):
    """Create a new route file"""
    model_name = to_pascal_case(name)
    controller_name = model_name + "Controller"
    file_name = to_snake_case(name) + "_routes.py"
    file_path = Path(f"app/routes/{file_name}")

    if file_path.exists():
        console.print(f"[red]Route already exists:[/red] {file_path}")
        raise typer.Exit(1)

    route_template = f'''from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.controllers.{to_snake_case(name)}_controller import {controller_name}
from app.models.{to_snake_case(name)} import {model_name}, {model_name}Create, {model_name}Update, {model_name}Read

router = APIRouter()


@router.get("/", response_model=List[{model_name}Read])
async def get_all(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    """Get all {to_snake_case(name)}s"""
    return await {controller_name}.get_all(session, skip, limit)


@router.get("/{{id}}", response_model={model_name}Read)
async def get_one(id: int, session: AsyncSession = Depends(get_session)):
    """Get {to_snake_case(name)} by ID"""
    return await {controller_name}.get_by_id(session, id)


@router.post("/", response_model={model_name}Read, status_code=201)
async def create(data: {model_name}Create, session: AsyncSession = Depends(get_session)):
    """Create a new {to_snake_case(name)}"""
    return await {controller_name}.create(session, data)


@router.put("/{{id}}", response_model={model_name}Read)
async def update(
    id: int, data: {model_name}Update, session: AsyncSession = Depends(get_session)
):
    """Update a {to_snake_case(name)}"""
    return await {controller_name}.update(session, id, data)


@router.delete("/{{id}}")
async def delete(id: int, session: AsyncSession = Depends(get_session)):
    """Soft delete a {to_snake_case(name)}"""
    return await {controller_name}.delete(session, id)


@router.post("/{{id}}/restore", response_model={model_name}Read)
async def restore(id: int, session: AsyncSession = Depends(get_session)):
    """Restore a soft deleted {to_snake_case(name)}"""
    return await {controller_name}.restore(session, id)
'''

    file_path.write_text(route_template)
    console.print(f"[green]✓[/green] Route created: {file_path}")
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
    migration: bool = typer.Option(False, "--migration", "-m", help="Create migration"),
):
    """Create model, controller, and routes all at once"""
    console.print(f"[cyan]Creating resource:[/cyan] {name}\n")

    make_model(name, migration=False)
    make_controller(name)
    make_route(name)

    if migration:
        table_name = to_snake_case(name) + "s"
        console.print("\n[yellow]Run migration commands:[/yellow]")
        console.print(f'  alembic revision --autogenerate -m "Create {table_name} table"')
        console.print("  alembic upgrade head")

    console.print(f"\n[green]✓ Resource '{name}' created successfully![/green]")


@app.command("list")
def list_commands():
    """List all available commands"""
    table = Table(title="Available CLI Commands")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="green")

    table.add_row("make:model", "Create a new model")
    table.add_row("make:controller", "Create a new controller")
    table.add_row("make:route", "Create a new route file")
    table.add_row("make:resource", "Create model, controller, and routes")
    table.add_row("list", "List all available commands")

    console.print(table)


if __name__ == "__main__":
    app()
