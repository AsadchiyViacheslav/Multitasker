from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, Field, model_validator
import re

PASSWORD_REGEX = r'^[A-Za-z0-9!#\$%&*\+\-\.<=>\?@^_]{8,16}$'


class UserScheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserRegister(UserScheme):
    email: EmailStr
    password: str = Field(min_length=8, max_length=16)
    password_rep: str = Field(min_length=8, max_length=16)

    @field_validator('password')
    def validate_password(cls, v):
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError('Пароль содержит недопустимые символы')
        return v

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.password_rep:
            raise ValueError('Пароли не совпадают')
        return self


class UserLogin(UserScheme):
    email: EmailStr
    password: str = Field(min_length=8, max_length=16)

    @field_validator('password')
    def validate_password(cls, v):
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError('Пароль содержит недопустимые символы')
        return v


class ForgotPassword(UserScheme):
    email: EmailStr


class ResetPassword(UserScheme):
    code: str
    new_password: str = Field(min_length=8, max_length=16)
    new_password_rep: str = Field(min_length=8, max_length=16)

    @field_validator('new_password')
    def validate_password(cls, v):
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError('Пароль содержит недопустимые символы')
        return v

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.new_password != self.new_password_rep:
            raise ValueError('Пароли не совпадают')
        return self
