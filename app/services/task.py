from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional
from app.models.project import Project
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.models.project_user import ProjectUserAssociation
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilter


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, user_id: int, data: TaskCreate) -> Task:
        author_in_project = self.db.query(ProjectUserAssociation).filter(
            ProjectUserAssociation.project_id == data.project_id,
            ProjectUserAssociation.user_id == user_id
        ).first()

        if not author_in_project:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не состоите в этом проекте"
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
                ProjectUserAssociation.project_id == data.project_id,
                ProjectUserAssociation.user_id == assignee.id
            ).first()

            if not assignee_in_project:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Исполнитель не состоит в проекте"
                )
        else:
            assignee = self.db.query(User).filter(User.id == user_id).first()

        task = Task(
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            importance=data.importance,
            task_status=TaskStatus.IN_PROGRESS,
            project_id=data.project_id,
            author_id=user_id,
            assignee_id=assignee.id,
            parent_id=None
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task(self, task_id: int, user_id: int, data: TaskUpdate) -> Task:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )

        is_author = task.author_id == user_id
        is_admin = self.db.query(ProjectUserAssociation).filter(
            ProjectUserAssociation.project_id == task.project_id,
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
                ProjectUserAssociation.project_id == task.project_id,
                ProjectUserAssociation.user_id == new_assignee.id
            ).first()

            if not assignee_in_project:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Новый исполнитель не состоит в проекте"
                )

            task.assignee_id = new_assignee.id

        for key, value in data.dict(exclude={"assignee_email"}, exclude_unset=True).items():
            setattr(task, key, value)

        self.db.commit()
        return task

    def get_tasks(self, filters: TaskFilter, current_user_id: int) -> List[Task]:
        user = self.db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="Пользователь не найден")

        query = self.db.query(Task).filter(Task.parent_id == None)

        if filters.project_id:
            if not user.is_superuser:
                project_participation = self.db.query(ProjectUserAssociation).filter_by(
                    user_id=current_user_id,
                    project_id=filters.project_id
                ).first()
                if not project_participation:
                    raise HTTPException(
                        status_code=403,
                        detail="Нет доступа к проекту"
                    )

            query = query.filter(Task.project_id == filters.project_id)

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
        if filters.task_status is not None:
            query = query.filter(Task.task_status == filters.task_status)
        if filters.due_date_to:
            query = query.filter(Task.due_date <= filters.due_date_to)

        return query.all()

    def get_task_by_id(self, task_id: int, current_user_id: int) -> Task:
        task = self.db.query(Task).filter(Task.id == task_id).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )

        user = self.db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        if not user.is_superuser:
            user_in_project = self.db.query(ProjectUserAssociation).filter(
                ProjectUserAssociation.project_id == task.project_id,
                ProjectUserAssociation.user_id == current_user_id
            ).first()

            if not user_in_project:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет доступа к этой задаче"
                )
        return task

    def delete_task(self, task_id: int, user_id: int) -> dict:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )

        is_author = task.author_id == user_id
        is_admin = self.db.query(ProjectUserAssociation).filter(
            ProjectUserAssociation.project_id == task.project_id,
            ProjectUserAssociation.user_id == user_id,
            ProjectUserAssociation.role == "admin"
        ).first()

        if not (is_author or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав на удаление"
            )

        self.db.delete(task)
        self.db.commit()
