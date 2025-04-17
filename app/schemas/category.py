from pydantic import BaseModel, Field, ConfigDict


class CategoryScheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(CategoryScheme):
    name: str = Field(max_length=100)
    color: str = Field(default='#ffffff', min_length=2, max_length=7)


class CategoryUpdate(CategoryScheme):
    name: str | None = None
    color: str | None = None


class CategoryResponse(CategoryScheme):
    id: int
    name: str
    color: str
