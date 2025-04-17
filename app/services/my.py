from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List

from app.models.project import Project
from app.models.project_user import ProjectUserAssociation
from app.models.task import Task
from app.schemas.my import MyTaskShort, MyProjectShort, MyFilter


class MyService:
    def __init__(self, db: Session):
        self.db = db

    def get_my_tasks(self, user_id: int, filters: MyFilter) -> List[MyTaskShort]:
        query = self.db.query(Task).options(
            joinedload(Task.author),
            joinedload(Task.assignee)
        )

        conditions = []
        if filters.as_author:
            conditions.append(Task.author_id == user_id)
        if filters.as_assignee:
            conditions.append(Task.assignee_id == user_id)

        if conditions:
            query = query.filter(or_(*conditions))
        else:
            return []

        if filters.task_status is not None:
            query = query.filter(Task.task_status == filters.task_status)
        if filters.due_date_to:
            query = query.filter(Task.due_date <= filters.due_date_to)

        return query.all()

    def get_my_projects(self, user_id: int) -> List[MyProjectShort]:
        return self.db.query(Project).join(
            ProjectUserAssociation,
            ProjectUserAssociation.project_id == Project.id
        ).filter(
            ProjectUserAssociation.user_id == user_id
        ).options(
            joinedload(Project.category)
        ).all()
