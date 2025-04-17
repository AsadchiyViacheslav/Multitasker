from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String(50), nullable=True)
    avatar_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    reset_password_code = Column(String(6), nullable=True)
    reset_code_expires = Column(DateTime, nullable=True)
    is_superuser = Column(Boolean, default=False)

    categories = relationship("Category", back_populates="user")

    created_projects = relationship("Project", back_populates="creator")
    projects = relationship("ProjectUserAssociation", back_populates="user")

    authored_tasks = relationship(
        "Task", foreign_keys="Task.author_id", back_populates="author")
    assigned_tasks = relationship(
        "Task", foreign_keys="Task.assignee_id", back_populates="assignee")
