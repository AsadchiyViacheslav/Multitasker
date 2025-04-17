from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.redis import redis_client
from app.schemas.user import (
    UserRegister,
    UserLogin,
    ForgotPassword,
    ResetPassword,
)
from app.services.auth import AuthService
security = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/register", summary="Register", description="Регистрация нового пользователя", status_code=201)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> dict:
    auth_service = AuthService(db)
    return auth_service.register_user(user_data)


@router.post("/login", summary="Login", description="Вход существующего пользователя", status_code=200)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
) -> dict:
    auth_service = AuthService(db)
    return auth_service.authenticate_user(user_data)


@router.post("/forgot-password", summary="Forgot Password", description="Отправка кода для восстановления пароля", status_code=200)
async def forgot_password(
    email: str,
    db: Session = Depends(get_db)
) -> dict:
    auth_service = AuthService(db)
    return auth_service.forgot_password(email)


@router.post("/reset-password", summary="Reset Password", description="Смена пароля по коду", status_code=200)
async def reset_password(
    reset_data: ResetPassword,
    db: Session = Depends(get_db)
) -> dict:
    auth_service = AuthService(db)
    return auth_service.reset_password(reset_data)


@router.post("/logout", summary="Logout", description="Выход из аккаунта", status_code=200)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    redis_client.setex(
        token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, "blacklisted")
    return {"message": "Вы вышли из системы"}
