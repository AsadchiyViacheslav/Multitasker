from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProjectUserAssociation(Base):
    __tablename__ = "project_user_association"

    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(String(50))

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="projects")
