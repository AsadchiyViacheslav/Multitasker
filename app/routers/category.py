from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.core.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["Категории проектов"])


@router.post("/create", summary="Create Category", description="Создание новой категории", response_model=CategoryResponse, status_code=201)
async def create_category_endpoint(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    category_service = CategoryService(db)
    return category_service.create_category(user_id, data)


@router.get("/", summary="Get Categories", description="Получить свои категории", response_model=list[CategoryResponse], status_code=200)
async def get_categories(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    category_service = CategoryService(db)
    return category_service.get_user_categories(user_id)


@router.put("/{category_id}/update", summary="Update Category", description="Обновить данные о категории", response_model=CategoryResponse, status_code=200)
async def update_category_endpoint(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    category_service = CategoryService(db)
    return category_service.update_category(category_id, user_id, data)


@router.delete("/{category_id}/delete", summary="Delete Category", description="Удалить существующую категорию")
async def delete_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
) -> dict:
    category_service = CategoryService(db)
    category_service.delete_category(category_id, user_id)
