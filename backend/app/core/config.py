from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/medassist"

    # JWT
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI services
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Storage
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "./storage/audio"

    # Video calls
    DAILY_API_KEY: str = ""
    DAILY_DOMAIN: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
