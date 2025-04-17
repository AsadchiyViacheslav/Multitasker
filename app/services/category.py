from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_category(self, user_id: int, category_data: CategoryCreate):
        existing = self.db.query(Category).filter(
            Category.user_id == user_id,
            Category.name == category_data.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Категория с таким именем уже существует"
            )

        category = Category(**category_data.dict(), user_id=user_id)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_user_categories(self, user_id: int):
        return self.db.query(Category).filter(Category.user_id == user_id).all()

    def update_category(self, category_id: int, user_id: int, data: CategoryUpdate):
        category = self.db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user_id
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )

        for key, value in data.dict(exclude_unset=True).items():
            setattr(category, key, value)

        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category_id: int, user_id: int):
        category = self.db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user_id
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )

        self.db.delete(category)
        self.db.commit()
