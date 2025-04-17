from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.task import TaskImportance, TaskStatus
from typing import Optional


class TaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(max_length=100)
    description: str | None = Field(None, max_length=10000)
    due_date: datetime
    importance: TaskImportance = TaskImportance.NOT_URGENT
    assignee_email: EmailStr | None = None
    project_id: int


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=10000)
    due_date: datetime | None = None
    importance: TaskImportance | None = None
    task_status: TaskStatus | None = None
    assignee_email: EmailStr | None = None


class TaskFilter(BaseModel):
    project_id: int | None = None
    assignee_id: int | None = None
    author_id: int | None = None
    importance: TaskImportance | None = None
    task_status: TaskStatus | None = None
    due_date_to: datetime | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    assignee_id: int
    title: str
    description: str | None
    due_date: datetime
    importance: TaskImportance = TaskImportance.NOT_URGENT
    project_id: int
    task_status: TaskStatus
