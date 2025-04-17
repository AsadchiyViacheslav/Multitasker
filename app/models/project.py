from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    icon_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"))

    category = relationship("Category", back_populates="projects")
    creator = relationship("User", back_populates="created_projects")
    members = relationship("ProjectUserAssociation", back_populates="project")
    tasks = relationship("Task", back_populates="project",
                         cascade="all, delete-orphan")
