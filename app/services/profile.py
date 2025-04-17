import os
from pathlib import Path
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from app.models.user import User
from app.models.file import File
from app.schemas.profile import ChangePasswordRequest
from typing import Optional


class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.avatar_dir = Path("files")
        self.avatar_dir.mkdir(parents=True, exist_ok=True)

    def get_user_profile(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="Пользователь не найден")
        return user

    def get_user_by_id(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="Пользователь не найден")
        return user

    def update_profile(
        self,
        user_id: int,
        name: Optional[str] = None,
        avatar_id: Optional[int] = None
    ) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="Пользователь не найден")

        if name is not None:
            user.name = name
        if avatar_id is not None:
            file_exists = self.db.query(File).filter(
                File.id == avatar_id).first() is not None
            if not file_exists:
                raise HTTPException(
                    status_code=404, detail="Файла не существует")
            user.avatar_id = avatar_id

        self.db.commit()
        return user

    def change_password(self, user_id: int, data: ChangePasswordRequest) -> dict:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, detail="Пользователь не найден")

        if not verify_password(data.old_password, user.hashed_password):
            raise HTTPException(
                status_code=400, detail="Неверный старый пароль")

        if data.new_password != data.confirm_password:
            raise HTTPException(
                status_code=400, detail="Новые пароли не совпадают")

        user.hashed_password = get_password_hash(data.new_password)
        self.db.commit()
        return {"message": "Пароль обновлен"}
