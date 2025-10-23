"""
core/config.py
Configuración central del backend (FastAPI + DB + Redis + CORS)
Compatible con entorno local y Railway
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""

    # === Application ===
    APP_NAME: str = "Nutritional Assessment API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # === Security ===
    SECRET_KEY: str = os.getenv("SECRET_KEY", "nutritional_secret_key_2024_very_secure")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    # === Database ===
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "railway")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", 10))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", 20))

    # === Redis (for caching and sessions) ===
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")

    # === CORS ===
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:80",
        "http://127.0.0.1:80",
    ]
    ALLOWED_HOSTS: List[str] = ["*"]

    # === File uploads ===
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "text/csv"
    ]

    # === Email ===
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_TLS: bool = True

    # === Logging ===
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")

    # === Monitoring ===
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(parents=True, exist_ok=True)


# ============================================================
# Instance + Helpers
# ============================================================

settings = Settings()


def get_database_url() -> str:
    """
    Return the proper database URL.
    - Uses DATABASE_URL if provided (Railway)
    - Otherwise builds from POSTGRES_* values (Docker local)
    """
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    return (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


def validate_settings():
    """Ensure required settings exist."""
    missing = []
    for key in ["SECRET_KEY", "DATABASE_URL"]:
        if not getattr(settings, key, None):
            missing.append(key)
    if missing:
        raise ValueError(f"Missing required settings: {', '.join(missing)}")


validate_settings()

print(f"✅ Loaded config for environment: {settings.ENVIRONMENT}")
