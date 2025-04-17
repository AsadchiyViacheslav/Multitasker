from sqlalchemy.orm import Session
from app.models.file import File
from app.models.user import User
from app.models.project import Project
from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse
from app.core.config import settings
from pathlib import Path
from datetime import datetime
import os
import mimetypes


class FileService:
    FILE_DIR = Path("files")
    FILE_DIR.mkdir(parents=True, exist_ok=True)

    def __init__(self, db: Session):
        self.db = db

    def save_file(self, file: UploadFile) -> int:
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail="Можно загружать только изображения")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"file_{timestamp}{Path(file.filename).suffix}"
        file_path = self.FILE_DIR / filename

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        db_file = File(url=f"{self.FILE_DIR}/{filename}")
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)

        return {"file_id": db_file.id}

    def get_user_avatar_file(self, user_id: int) -> FileResponse:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="Пользователь не найден")
        if not user.avatar_id:
            raise HTTPException(
                status_code=404, detail="Аватар не привязан к пользователю")

        return self._get_file_response_by_id(user.avatar_id)

    def get_project_file(self, project_id: int) -> FileResponse:
        project = self.db.query(Project).filter(
            Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")
        if not project.icon_id:
            raise HTTPException(status_code=404, detail="У проекта нет иконки")

        return self._get_file_response_by_id(project.icon_id)

    async def _get_file_response_by_id(self, file_id: int) -> FileResponse:
        file_record = self.db.query(File).filter(File.id == file_id).first()
        if not file_record:
            raise HTTPException(
                status_code=404, detail="Файл не найден в базе")

        file_path = file_record.url
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404, detail="Файл не найден на сервере")

        media_type, _ = mimetypes.guess_type(file_path)
        if not media_type:
            media_type = "application/octet-stream"

        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type=media_type
        )
