from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SMTP_USER: str
    SMTP_PASSWORD: str
    API_BASE_URL: str = "http://localhost:8000/"
    MAX_AVATAR_SIZE_MB: int = 20

    class Config:
        env_file = ".env"


settings = Settings()
