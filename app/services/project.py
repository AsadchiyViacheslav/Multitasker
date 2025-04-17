from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload
from app.models.project import Project
from app.models.category import Category
from app.models.project_user import ProjectUserAssociation
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectFilter, ProjectUpdate, AddMemberRequest


class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def create_project(self, user_id: int, data: ProjectCreate) -> Project:
        if data.category_id:
            category = self.db.query(Category).filter(
                Category.id == data.category_id
            ).first()

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Категория не найдена"
                )

        project = Project(**data.dict(), creator_id=user_id)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        admin_association = ProjectUserAssociation(
            project_id=project.id,
            user_id=user_id,
            role="admin"
        )
        self.db.add(admin_association)
        self.db.commit()

        return project

    def get_projects(self, filters: ProjectFilter, current_user_id: int) -> list[Project]:

        user = self.db.query(User).filter(User.id == current_user_id).first()

        if user.is_superuser:
            query = self.db.query(Project)
        else:
            query = self.db.query(Project).join(
                ProjectUserAssociation,
                ProjectUserAssociation.project_id == Project.id
            ).filter(
                ProjectUserAssociation.user_id == user.id
            )

        if filters.category_id:
            query = query.filter(Project.category_id == filters.category_id)

        query = query.options(joinedload(Project.category))

        return query.all()

    def get_project_members(self, project_id: int, current_user_id: int) -> list[dict]:
        user = self.db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="Пользователь не найден")

        if not user.is_superuser:
            if not self.db.query(ProjectUserAssociation).filter(
                ProjectUserAssociation.project_id == project_id,
                ProjectUserAssociation.user_id == current_user_id
            ).first():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет доступа к этому проекту"
                )

        project = self.db.query(Project).filter(
            Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        members = self.db.query(
            ProjectUserAssociation,
            User
        ).join(
            User, ProjectUserAssociation.user_id == User.id
        ).filter(
            ProjectUserAssociation.project_id == project_id
        ).all()

        return [
            {"user": user, "role": association.role}
            for association, user in members
        ]

    def update_project(self, project_id: int, user_id: int, data: ProjectUpdate) -> Project:
        project = self.db.query(Project).filter(
            Project.id == project_id,
            Project.creator_id == user_id
        ).first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        for key, value in data.dict(exclude_unset=True).items():
            setattr(project, key, value)

        self.db.commit()
        return project

    def delete_project(self, project_id: int, user_id: int):
        project = self.db.query(Project).filter(
            Project.id == project_id,
            Project.creator_id == user_id
        ).first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проект не найден"
            )

        self.db.delete(project)
        self.db.commit()

    def add_member(self, project_id: int, current_user_id: int, data: AddMemberRequest) -> dict:
        if not self.db.query(ProjectUserAssociation).filter(
                ProjectUserAssociation.project_id == project_id,
                ProjectUserAssociation.user_id == current_user_id,
                ProjectUserAssociation.role == "admin"
        ).first():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа"
            )

        user = self.db.query(User).filter(User.email == data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь с таким email не найден"
            )

        existing = self.db.query(ProjectUserAssociation).filter(
            ProjectUserAssociation.project_id == project_id,
            ProjectUserAssociation.user_id == user.id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь уже состоит в проекте"
            )

        association = ProjectUserAssociation(
            project_id=project_id,
            user_id=user.id,
            role=data.role
        )
        self.db.add(association)
        self.db.commit()
        return {"message": "Пользователь добавлен"}

    def remove_member(self, project_id: int, current_user_id: int, user_id_to_remove: int):
        is_admin = self.db.query(ProjectUserAssociation).filter(
            ProjectUserAssociation.project_id == project_id,
            ProjectUserAssociation.user_id == current_user_id,
            ProjectUserAssociation.role == "admin"
        ).first()

        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для удаления пользователя"
            )
        association = self.db.query(ProjectUserAssociation).filter(
            ProjectUserAssociation.project_id == project_id,
            ProjectUserAssociation.user_id == user_id_to_remove
        ).first()

        if not association:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не состоит в проекте"
            )

        if user_id_to_remove == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить самого себя"
            )

        self.db.delete(association)
        self.db.commit()
