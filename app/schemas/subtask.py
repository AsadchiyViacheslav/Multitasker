from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.task import TaskImportance, TaskStatus
from typing import Optional


class SubtaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(max_length=100)
    description: str | None = Field(None, max_length=10000)
    due_date: datetime
    importance: TaskImportance = TaskImportance.NOT_URGENT
    assignee_email: EmailStr | None = None
    parent_id: int


class SubtaskCreate(SubtaskBase):
    pass


class SubtaskUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=10000)
    due_date: datetime | None = None
    importance: TaskImportance | None = None
    task_status: TaskStatus | None = None
    assignee_email: EmailStr | None = None


class SubtaskFilter(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    parent_id: int | None = None
    assignee_id: int | None = None
    author_id: int | None = None
    importance: str | None = None
    task_status: TaskStatus | None = None
    due_date_to: datetime | None = None


class SubtaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: int
    author_id: int
    assignee_id: int
    project_id: int
    task_status: TaskStatus
    title: str
    description: str | None = None
    due_date: datetime
    importance: TaskImportance
