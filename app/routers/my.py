from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.my import MyTaskShort, MyProjectShort, MyFilter
from app.services.my import MyService
from app.models.user import User
from app.models.task import TaskStatus

router = APIRouter(prefix="/my", tags=["Моё"])


@router.get("/tasks", summary="Get My Tasks", description="Получить мои задачи", response_model=List[MyTaskShort], status_code=200)
async def get_my_tasks_list(
    task_status: Optional[TaskStatus] = Query(None),
    due_date_to: Optional[datetime] = Query(None),
    as_author: bool = Query(True),
    as_assignee: bool = Query(True),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    filters = MyFilter(
        task_status=task_status,
        due_date_to=due_date_to,
        as_author=as_author,
        as_assignee=as_assignee
    )
    service = MyService(db)
    return service.get_my_tasks(current_user_id, filters)


@router.get("/projects", summary="Get My projects", description="Получить мои задачи", response_model=List[MyProjectShort], status_code=200)
async def get_my_projects_list(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    service = MyService(db)
    return service.get_my_projects(current_user_id)
