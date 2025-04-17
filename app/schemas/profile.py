from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
import re

PASSWORD_REGEX = r'^[A-Za-z0-9!#\$%&*\+\-\.<=>\?@^_]{8,16}$'


class UserScheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(UserScheme):
    id: int
    name: str | None = None
    email: EmailStr
    avatar_id: int | None = None


class UpdateProfileRequest(UserScheme):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    avatar_id: int | None = Field(default=None)


class ChangePasswordRequest(UserScheme):
    old_password: str = Field(min_length=8, max_length=16)
    new_password: str = Field(min_length=8, max_length=16)
    confirm_password: str = Field(min_length=8, max_length=16)

    @field_validator('new_password')
    def validate_password(cls, v):
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError('Пароль содержит недопустимые символы')
        return v
