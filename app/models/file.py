from sqlalchemy import Column, Integer, String
from app.core.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
