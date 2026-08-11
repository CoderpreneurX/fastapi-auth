import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    # APP
    SECRET_KEY: str = ""
    APP_NAME: str = "FastAPI Auth"

    # DATABASE
    DATABASE_URL: str = ""

    # SMTP
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False

    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = SECRET_KEY
    JWT_EXPIRY_SECONDS: int = 86400  # 24 hours
    JWT_ISSUER: str = APP_NAME  # Optional
    JWT_AUDIENCE: str | None = None  # Optional

    # TOKENS
    EMAIL_VERIFICATION_TOKEN_EXPIRE_SECONDS: int = 86400

    # FRONTEND
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
