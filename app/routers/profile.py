from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer
from app.core.database import get_db
from app.schemas.profile import ProfileResponse, UpdateProfileRequest, ChangePasswordRequest
from app.core.security import get_current_user
from app.services.profile import ProfileService
from app.services.file import FileService


router = APIRouter(prefix="/profile", tags=["Профиль"])
security = HTTPBearer()


@router.get("/", summary="Get Profile", description="Получить свой профиль", response_model=ProfileResponse, status_code=200)
async def get_profile(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    profile_service = ProfileService(db)
    return profile_service.get_user_profile(current_user_id)


@router.get("/{user_id}", summary="Get Profile By ID", description="Получить профиль по Id", response_model=ProfileResponse, status_code=200)
async def get_user_by_id_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    profile_service = ProfileService(db)
    return profile_service.get_user_by_id(user_id)


@router.get("/avatar/{user_id}", summary="Get User Avatar", description="Получить аватар пользователя", status_code=200)
async def get_user_avatar(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    file_service = FileService(db)
    return await file_service.get_user_avatar_file(user_id)


@router.put("/update", summary="Update Profile", description="Обновить данные профиля", response_model=ProfileResponse, status_code=200)
async def update_profile(
    update_data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    profile_service = ProfileService(db)
    return profile_service.update_profile(
        current_user_id,
        update_data.name,
        update_data.avatar_id
    )


@router.put("/change-password", summary="Change Password", description="Смена пароля на новый", status_code=200)
async def change_user_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> dict:
    profile_service = ProfileService(db)
    return profile_service.change_password(current_user_id, password_data)


@router.post("/upload-file", summary="Upload File", description="Загрузить фотографию", status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
) -> dict:

    file_service = FileService(db)
    return file_service.save_file(file)
