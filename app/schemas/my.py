from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.models.task import TaskImportance, TaskStatus


class MyTaskShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    due_date: datetime
    importance: TaskImportance
    author_id: int
    assignee_id: int
    project_id: int


class MyProjectShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    category_id: int


class MyFilter(BaseModel):
    task_status: TaskStatus | None = None
    due_date_to: datetime | None = None
    as_author: bool = True
    as_assignee: bool = True
