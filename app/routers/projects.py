from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.security import get_current_user
from app.core.database import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectCreateResponse,
    ProjectResponse,
    ProjectFilter,
    ProjectUpdate,
    ProjectMemberResponse,
    AddMemberRequest
)
from app.services.project import ProjectService
from app.services.file import FileService

router = APIRouter(prefix="/projects", tags=["Проекты"])


@router.post("/create", summary="Create Project", description="Создать новый проект", response_model=ProjectCreateResponse, status_code=201)
def create_project_endpoint(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    project_service = ProjectService(db)
    return project_service.create_project(current_user_id, data)


@router.post("/{project_id}/add_members", summary="Add Member", description="Добавить пользователя в проект", status_code=201)
def add_member_endpoint(
    project_id: int,
    data: AddMemberRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> dict:
    project_service = ProjectService(db)
    return project_service.add_member(project_id, current_user_id, data)


@router.get("/", summary="Get Project", description="Получить проекты по фильтрам", response_model=List[ProjectResponse], status_code=200)
def get_projects_endpoint(
    filters: ProjectFilter = Depends(),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    project_service = ProjectService(db)
    return project_service.get_projects(filters, current_user_id)


@router.get("/{project_id}/members", summary="Get Project Members", description="Получить всех участников проекта", response_model=List[ProjectMemberResponse], status_code=200)
def get_project_members_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    project_service = ProjectService(db)
    return project_service.get_project_members(project_id, current_user_id)


@router.get("/get_icon", summary="Get Icon", description="Получить иконку проекта", status_code=200)
async def get_icon(
    project_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file_service = FileService(db)
    return await file_service.get_project_file(project_id)


@router.put("/{project_id}/update", summary="Update Project", description="Обновить информацию о проекте", response_model=ProjectResponse, status_code=200)
def update_project_endpoint(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    project_service = ProjectService(db)
    return project_service.update_project(project_id, current_user_id, data)


@router.delete("/{project_id}/delete", summary="Delete Project", description="Удаление проекта")
def delete_project_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> dict:
    project_service = ProjectService(db)
    project_service.delete_project(project_id, current_user_id)


@router.delete("/{project_id}/remove_member/{user_id_to_remove}", summary="Remove Member", description="Удалить участника проекта")
def remove_member_endpoint(
    project_id: int,
    user_id_to_remove: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> dict:
    project_service = ProjectService(db)
    project_service.remove_member(
        project_id, current_user_id, user_id_to_remove)
