from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User
from app.schemas.user import (
    UserRegister,
    UserLogin,
    ForgotPassword,
    ResetPassword,
)
from app.services.email import send_reset_code_email
from app.core.security import get_password_hash, verify_password, generate_reset_code, create_access_token


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: UserRegister) -> dict:
        existing_user = self.db.query(User).filter(
            User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже зарегистрирован"
            )

        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
        )

        self.db.add(db_user)
        self.db.commit()

        access_token = create_access_token(
            data={"sub": db_user.email}
        )
        return {"access_token": access_token, "token_type": "bearer"}

    def authenticate_user(self, user_data: UserLogin) -> dict:
        user = self.db.query(User).filter(
            User.email == user_data.email).first()
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(
            data={"sub": user.email}
        )
        return {"access_token": access_token, "token_type": "bearer"}

    def forgot_password(self, email: str) -> dict:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь с таким email не найден"
            )

        reset_code = generate_reset_code()
        user.reset_password_code = reset_code
        user.reset_code_expires = datetime.utcnow() + timedelta(minutes=15)
        self.db.commit()

        send_reset_code_email(email, reset_code)
        return {"message": "Код для сброса пароля отправлен на вашу почту"}

    def reset_password(self, reset_data: ResetPassword) -> dict:
        user = self.db.query(User).filter(
            User.reset_password_code == reset_data.code,
            User.reset_code_expires > datetime.utcnow()
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неправильный код или срок действия кода истек"
            )

        if reset_data.new_password != reset_data.new_password_rep:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароли не совпадают"
            )

        user.hashed_password = get_password_hash(reset_data.new_password)
        user.reset_password_code = None
        user.reset_code_expires = None
        self.db.commit()

        return {"message": "Пароль успешно обновлен"}
