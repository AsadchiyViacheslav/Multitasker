from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskFilter
from app.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["Задачи"])


@router.post("/create", summary="Create Task", description="Создать новую задачу", response_model=TaskResponse, status_code=201)
async def create_new_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    task_service = TaskService(db)
    return task_service.create_task(current_user_id, task_data)


@router.get("/", summary="Get Tasks", description="Получить задачи по фильтрам", response_model=List[TaskResponse], status_code=200)
def get_tasks(
    filters: TaskFilter = Depends(),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    service = TaskService(db)
    return service.get_tasks(filters, current_user_id)


@router.get("/{task_id}", summary="Get Task", description="Получить задачу по Id", response_model=TaskResponse, status_code=200)
async def get_task_details(
    task_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    task_service = TaskService(db)
    return task_service.get_task_by_id(task_id, current_user_id)


@router.put("/{task_id}", summary="Update Task", description="Обновить информацию о задаче", response_model=TaskResponse, status_code=200)
async def update_existing_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    task_service = TaskService(db)
    return task_service.update_task(task_id, current_user_id, task_data)


@router.delete("/{task_id}", summary="Delete Task", description="Удалить задачу")
async def delete_existing_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    task_service = TaskService(db)
    task_service.delete_task(task_id, current_user_id)
