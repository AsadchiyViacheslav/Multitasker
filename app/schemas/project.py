from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List


class ProjectScheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(ProjectScheme):
    name: str
    icon_id: int
    category_id: int


class ProjectUpdate(ProjectScheme):
    name: str | None = None
    icon_id: int | None = None
    category_id: int | None = None


class ProjectCreateResponse(ProjectScheme):
    id: int
    name: str
    icon_id: int
    category_id: int
    creator_id: int


class UserInfo(ProjectScheme):
    id: int
    name: str | None
    email: str


class ProjectMemberResponse(ProjectScheme):
    user: UserInfo
    role: str


class ProjectResponse(ProjectScheme):
    id: int
    name: str
    icon_id: int
    category_id: int
    creator_id: int
    members: List[ProjectMemberResponse]


class ProjectFilter(ProjectScheme):
    category_id: int | None = None


class AddMemberRequest(ProjectScheme):
    email: EmailStr
    role: str = "member"
