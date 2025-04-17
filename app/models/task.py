from datetime import datetime
from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship, backref
from app.core.database import Base

class TaskStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    END = "end"

class TaskImportance(str, Enum):
    VERY_URGENT = "very_urgent"
    URGENT = "urgent"
    CAN_WAIT = "can_wait"
    NOT_URGENT = "not_urgent"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(10000))
    due_date = Column(DateTime, nullable=False)
    importance = Column(SQLEnum(TaskImportance), default=TaskImportance.NOT_URGENT)
    task_status = Column(SQLEnum(TaskStatus), default=TaskStatus.IN_PROGRESS, nullable=False)

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    project = relationship("Project", back_populates="tasks")
    author = relationship("User", foreign_keys=[author_id], back_populates="authored_tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")

    subtasks = relationship(
        "Task",
        foreign_keys=[parent_id],
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete-orphan",
        lazy="selectin"
    )