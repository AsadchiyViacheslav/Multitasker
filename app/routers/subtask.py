from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.subtask import SubtaskCreate, SubtaskUpdate, SubtaskResponse, SubtaskFilter
from app.models.user import User
from app.services.subtask import SubtaskService
from app.models.task import TaskStatus

router = APIRouter(prefix="/subtasks", tags=["Подзадачи"])


@router.post("/create", summary="Create Subtask", description="Создать новую подзадачу", response_model=SubtaskResponse, status_code=201)
async def create_new_subtask(
        subtask_data: SubtaskCreate,
        db: Session = Depends(get_db),
        current_user_id: int = Depends(get_current_user)
):
    subtask_service = SubtaskService(db)
    return subtask_service.create_subtask(current_user_id, subtask_data)


@router.get("/", summary="Get Subtasks", description="Получить подзадачи по фильтрам", response_model=List[SubtaskResponse], status_code=200)
async def get_filtered_subtasks(
        filters=SubtaskFilter,
        db: Session = Depends(get_db),
        current_user_id: int = Depends(get_current_user)
):
    subtask_service = SubtaskService(db)
    return subtask_service.get_subtasks(filters, current_user_id)


@router.get("/{subtask_id}", summary="Get Subtask", description="Получить подзадачу по Id", response_model=SubtaskResponse, status_code=200)
async def get_subtask_details(
        subtask_id: int,
        db: Session = Depends(get_db),
        current_user_id: int = Depends(get_current_user)
):
    subtask_service = SubtaskService(db)
    return subtask_service.get_subtask_by_id(subtask_id, current_user_id)


@router.put("/{subtask_id}", summary="Update Subtask", description="Обновить информацию о подзадаче", response_model=SubtaskResponse, status_code=200)
async def update_existing_subtask(
        subtask_id: int,
        subtask_data: SubtaskUpdate,
        db: Session = Depends(get_db),
        current_user_id: int = Depends(get_current_user)
):
    subtask_service = SubtaskService(db)
    return subtask_service.update_subtask(subtask_id, current_user_id, subtask_data)


@router.delete("/{subtask_id}", summary="Delete subtask", description="Удалить подзадачу")
async def delete_existing_subtask(
        subtask_id: int,
        db: Session = Depends(get_db),
        current_user_id: int = Depends(get_current_user)
):
    subtask_service = SubtaskService(db)
    subtask_service.delete_subtask(subtask_id, current_user_id)
