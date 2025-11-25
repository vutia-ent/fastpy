# API Service Example

Build a microservice for task management.

## Overview

This example creates a task management API with:

- Projects and tasks
- Task assignments
- Status tracking
- Activity logging

---

## Models

### Project

```bash
python cli.py make:resource Project \
  -f name:string:required,max:200 \
  -f description:text:nullable \
  -f status:string:required,index \
  -f start_date:date:nullable \
  -f due_date:date:nullable \
  -f owner_id:integer:required,foreign:users.id \
  -m -p
```

### Task

```bash
python cli.py make:resource Task \
  -f title:string:required,max:255 \
  -f description:text:nullable \
  -f status:string:required,index \
  -f priority:string:required,index \
  -f due_date:datetime:nullable \
  -f completed_at:datetime:nullable \
  -f project_id:integer:required,foreign:projects.id \
  -f assignee_id:integer:nullable,foreign:users.id \
  -f creator_id:integer:required,foreign:users.id \
  -m -p
```

### Activity

```bash
python cli.py make:model Activity \
  -f action:string:required,index \
  -f entity_type:string:required,index \
  -f entity_id:integer:required,index \
  -f changes:json:nullable \
  -f user_id:integer:required,foreign:users.id \
  -m
```

---

## Enums

### Task Status

```bash
python cli.py make:enum TaskStatus
```

```python
# app/enums/task_status.py

from enum import Enum


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    ARCHIVED = "archived"
```

### Task Priority

```bash
python cli.py make:enum TaskPriority
```

```python
# app/enums/task_priority.py

from enum import Enum


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
```

---

## Task Service

```python
# app/services/task_service.py

from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.task import Task, TaskCreate, TaskUpdate
from app.models.activity import Activity
from app.enums.task_status import TaskStatus
from app.utils.exceptions import NotFoundException, BadRequestException


class TaskService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(
        self,
        data: TaskCreate,
        creator_id: int
    ) -> Task:
        task = Task(
            **data.model_dump(),
            creator_id=creator_id,
            status=TaskStatus.TODO
        )
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)

        # Log activity
        await self._log_activity(
            "created",
            "task",
            task.id,
            creator_id,
            {"title": task.title}
        )

        return task

    async def update_task(
        self,
        task_id: int,
        data: TaskUpdate,
        user_id: int
    ) -> Task:
        task = await self._get_task(task_id)

        changes = {}
        for key, value in data.model_dump(exclude_unset=True).items():
            old_value = getattr(task, key)
            if old_value != value:
                changes[key] = {"old": old_value, "new": value}
                setattr(task, key, value)

        if changes:
            task.touch()
            await self._log_activity(
                "updated",
                "task",
                task.id,
                user_id,
                changes
            )

        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def assign_task(
        self,
        task_id: int,
        assignee_id: int,
        user_id: int
    ) -> Task:
        task = await self._get_task(task_id)

        old_assignee = task.assignee_id
        task.assignee_id = assignee_id
        task.touch()

        await self._log_activity(
            "assigned",
            "task",
            task.id,
            user_id,
            {"old_assignee": old_assignee, "new_assignee": assignee_id}
        )

        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def change_status(
        self,
        task_id: int,
        status: TaskStatus,
        user_id: int
    ) -> Task:
        task = await self._get_task(task_id)

        old_status = task.status
        task.status = status

        if status == TaskStatus.DONE:
            task.completed_at = datetime.now(timezone.utc)
        elif old_status == TaskStatus.DONE:
            task.completed_at = None

        task.touch()

        await self._log_activity(
            "status_changed",
            "task",
            task.id,
            user_id,
            {"old_status": old_status, "new_status": status}
        )

        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def get_task_activities(
        self,
        task_id: int,
        limit: int = 50
    ) -> List[Activity]:
        query = (
            select(Activity)
            .where(
                Activity.entity_type == "task",
                Activity.entity_id == task_id
            )
            .order_by(Activity.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def _get_task(self, task_id: int) -> Task:
        query = select(Task).where(
            Task.id == task_id,
            Task.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundException("Task not found")
        return task

    async def _log_activity(
        self,
        action: str,
        entity_type: str,
        entity_id: int,
        user_id: int,
        changes: dict = None
    ):
        activity = Activity(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            user_id=user_id
        )
        self.session.add(activity)
```

---

## Task Routes

```python
# app/routes/task_routes.py

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.services.task_service import TaskService
from app.controllers.task_controller import TaskController
from app.models.task import TaskCreate, TaskUpdate, TaskRead
from app.enums.task_status import TaskStatus
from app.enums.task_priority import TaskPriority
from app.utils.auth import get_current_active_user

router = APIRouter()


@router.get("/")
async def get_tasks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    project_id: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session)
):
    """Get tasks with filters"""
    result = await TaskController.get_filtered(
        session,
        page=page,
        per_page=per_page,
        project_id=project_id,
        status=status,
        priority=priority,
        assignee_id=assignee_id
    )
    return {
        "data": result.items,
        "pagination": {
            "page": result.page,
            "per_page": result.per_page,
            "total": result.total,
            "pages": result.pages
        }
    }


@router.post("/", response_model=TaskRead, status_code=201)
async def create_task(
    data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    """Create a new task"""
    service = TaskService(session)
    return await service.create_task(data, current_user.id)


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    """Update a task"""
    service = TaskService(session)
    return await service.update_task(task_id, data, current_user.id)


@router.post("/{task_id}/assign", response_model=TaskRead)
async def assign_task(
    task_id: int,
    assignee_id: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    """Assign task to user"""
    service = TaskService(session)
    return await service.assign_task(task_id, assignee_id, current_user.id)


@router.post("/{task_id}/status", response_model=TaskRead)
async def change_task_status(
    task_id: int,
    status: TaskStatus,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    """Change task status"""
    service = TaskService(session)
    return await service.change_status(task_id, status, current_user.id)


@router.get("/{task_id}/activities")
async def get_task_activities(
    task_id: int,
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    """Get task activity history"""
    service = TaskService(session)
    activities = await service.get_task_activities(task_id, limit)
    return {"data": activities}
```

---

## API Endpoints

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects/` | List projects |
| GET | `/api/projects/{id}` | Get project |
| POST | `/api/projects/` | Create project |
| PUT | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Delete project |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks/` | List with filters |
| GET | `/api/tasks/{id}` | Get task |
| POST | `/api/tasks/` | Create task |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| POST | `/api/tasks/{id}/assign` | Assign task |
| POST | `/api/tasks/{id}/status` | Change status |
| GET | `/api/tasks/{id}/activities` | Activity history |

---

## Usage Examples

### Create Task

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement login page",
    "description": "Create the user login page with form validation",
    "priority": "high",
    "due_date": "2024-02-01T17:00:00Z",
    "project_id": 1
  }'
```

### List Tasks

```bash
curl "http://localhost:8000/api/tasks/?project_id=1&status=in_progress&priority=high"
```

### Assign Task

```bash
curl -X POST "http://localhost:8000/api/tasks/1/assign?assignee_id=5" \
  -H "Authorization: Bearer TOKEN"
```

### Change Status

```bash
curl -X POST "http://localhost:8000/api/tasks/1/status?status=done" \
  -H "Authorization: Bearer TOKEN"
```

### Get Activity

```bash
curl http://localhost:8000/api/tasks/1/activities
```

Response:
```json
{
  "data": [
    {
      "action": "status_changed",
      "entity_type": "task",
      "entity_id": 1,
      "changes": {
        "old_status": "in_progress",
        "new_status": "done"
      },
      "user_id": 3,
      "created_at": "2024-01-15T14:30:00Z"
    },
    {
      "action": "assigned",
      "entity_type": "task",
      "entity_id": 1,
      "changes": {
        "old_assignee": null,
        "new_assignee": 5
      },
      "user_id": 1,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

## Next Steps

- [Blog Example](blog.md) - Content management
- [E-commerce Example](ecommerce.md) - Product catalog
- [Make Commands](../commands/make.md) - Generate more
