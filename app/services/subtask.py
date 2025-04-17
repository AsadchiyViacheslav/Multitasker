from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from app.models.task import Task
from app.models.user import User
from app.models.project_user import ProjectUserAssociation
from app.schemas.subtask import SubtaskCreate, SubtaskUpdate, SubtaskFilter
from typing import List, Optional


class SubtaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_subtask(self, user_id: int, data: SubtaskCreate) -> Task:
        parent_task = self.db.query(Task).filter(
            Task.id == data.parent_id
        ).first()
        if not parent_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Родительская задача не найдена"
            )

        author_in_project = self.db.query(ProjectUserAssociation).filter(
            ProjectUserAssociation.project_id == parent_task.project_id,
            ProjectUserAssociation.user_id == user_id
        ).first()
        if not author_in_project:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не состоите в проекте"
            )

        if data.assignee_email:
            assignee = self.db.query(User).filter(
                User.email == data.assignee_email
            ).first()
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Исполнитель не зарегистрирован"
                )

            assignee_in_project = self.db.query(ProjectUserAssociation).filter(
                ProjectUserAssociation.project_id == parent_task.project_id,
                ProjectUserAssociation.user_id == assignee.id
            ).first()

            if not assignee_in_project:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Исполнитель не состоит в проекте"
                )
        else:
            assignee = self.db.query(User).filter(User.id == user_id).first()

        subtask = Task(
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            importance=data.importance,
            project_id=parent_task.project_id,
            author_id=user_id,
            assignee_id=assignee.id,
            parent_id=data.parent_id,
            task_status="in_progress"
        )

        self.db.add(subtask)
        self.db.commit()
        self.db.refresh(subtask)
        return subtask

    def update_subtask(self, subtask_id: int, user_id: int, data: SubtaskUpdate):
        subtask = self.db.query(Task).filter(Task.id == subtask_id).first()
        if not subtask:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Подзадача не найдена"
            )

        is_author = subtask.author_id == user_id
        is_admin = self.db.query(ProjectUserAssociation).filter(
            ProjectUserAssociation.project_id == subtask.project_id,
            ProjectUserAssociation.user_id == user_id,
            ProjectUserAssociation.role == "admin"
        ).first()

        if not (is_author or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав на редактирование"
            )

        if data.assignee_email:
            new_assignee = self.db.query(User).filter(
                User.email == data.assignee_email).first()
            if not new_assignee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Новый исполнитель не найден"
                )

            assignee_in_project = self.db.query(ProjectUserAssociation).filter(
                ProjectUserAssociation.project_id == subtask.project_id,
                ProjectUserAssociation.user_id == new_assignee.id
            ).first()

            if not assignee_in_project:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Новый исполнитель не состоит в проекте"
                )

            subtask.assignee_id = new_assignee.id

        for key, value in data.dict(exclude={"assignee_email"}, exclude_unset=True).items():
            setattr(subtask, key, value)

        self.db.commit()
        return subtask

    def get_subtasks(self, filters: SubtaskFilter, current_user_id: int) -> List[Task]:
        user = self.db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="Пользователь не найден")

        query = self.db.query(Task).filter(Task.parent_id.isnot(None))

        if filters.parent_id:
            parent_task = self.db.query(Task).filter(
                Task.id == filters.parent_id).first()
            if not parent_task:
                raise HTTPException(
                    status_code=404, detail="Родительская задача не найдена")

            if not user.is_superuser:
                project_participation = self.db.query(ProjectUserAssociation).filter_by(
                    user_id=current_user_id,
                    project_id=parent_task.project_id
                ).first()
                if not project_participation:
                    raise HTTPException(
                        status_code=403,
                        detail="Нет доступа к подзадачам этой задачи"
                    )

            query = query.filter(Task.parent_id == filters.parent_id)
        else:
            if not user.is_superuser:
                query = query.filter(
                    (Task.author_id == current_user_id) | (
                        Task.assignee_id == current_user_id)
                )

        if filters.assignee_id:
            query = query.filter(Task.assignee_id == filters.assignee_id)
        if filters.author_id:
            query = query.filter(Task.author_id == filters.author_id)
        if filters.importance:
            query = query.filter(Task.importance == filters.importance)
        if filters.task_status:
            query = query.filter(Task.task_status == filters.task_status)
        if filters.due_date_to:
            query = query.filter(Task.due_date <= filters.due_date_to)

        return query.all()

    def get_subtask_by_id(self, subtask_id: int, current_user_id: int) -> Task:
        subtask = self.db.query(Task).filter(
            Task.id == subtask_id,
            Task.parent_id.isnot(None)
        ).first()

        if not subtask:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Подзадача не найдена"
            )

        user = self.db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        if not user.is_superuser:
            user_in_project = self.db.query(ProjectUserAssociation).filter(
                ProjectUserAssociation.project_id == subtask.project_id,
                ProjectUserAssociation.user_id == current_user_id
            ).first()

            if not user_in_project:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет доступа к этой подзадаче"
                )

        return subtask

    def delete_subtask(self, subtask_id: int, user_id: int):
        subtask = self.db.query(Task).filter(Task.id == subtask_id).first()
        if not subtask or not subtask.parent_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Подзадача не найдена"
            )

        is_author = subtask.author_id == user_id
        is_admin = self.db.query(ProjectUserAssociation).filter(
            ProjectUserAssociation.project_id == subtask.project_id,
            ProjectUserAssociation.user_id == user_id,
            ProjectUserAssociation.role == "admin"
        ).first()

        if not (is_author or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав на удаление"
            )

        self.db.delete(subtask)
        self.db.commit()
