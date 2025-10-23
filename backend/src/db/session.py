# backend/src/db/session.py
# -*- coding: utf-8 -*-
"""
Database session management for Nutritional Assessment API
-----------------------------------------------------------
Compatible con Docker local y Railway.
Maneja engine SQLAlchemy, SessionLocal y helpers de conexión.
"""

from __future__ import annotations

import os
import logging
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

# ============================================================
# Carga de configuración (con fallback si no existe core.config)
# ============================================================
try:
    # Nota: dentro del contenedor, el root es 'src', así que NO uses 'from src.core...'
    from core.config import settings, get_database_url  # type: ignore
except Exception:
    # Fallback si no existe core.config o falla el import
    class _FallbackSettings:
        DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
        DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
        DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    settings = _FallbackSettings()  # type: ignore

    def get_database_url() -> str | None:
        return os.getenv("DATABASE_URL")


# ============================================================
# Normalización de URL y creación del Engine
# ============================================================
def _normalized_db_url(raw_url: str | None) -> str:
    """
    Normaliza el esquema para forzar driver psycopg2 cuando sea necesario.
    Acepta:
      - postgresql://...
      - postgres://... (lo convierte)
    """
    if not raw_url:
        # Fallback: construir desde variables sueltas
        raw_url = (
            f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:"
            f"{os.getenv('POSTGRES_PASSWORD', 'postgres')}@"
            f"{os.getenv('POSTGRES_HOST', 'db')}:"
            f"{os.getenv('POSTGRES_PORT', '5432')}/"
            f"{os.getenv('POSTGRES_DB', 'railway')}"
        )

    # Forzar driver explícito
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg2://", 1)
    if raw_url.startswith("postgresql://"):
        return raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return raw_url


def _create_engine():
    try:
        db_url = _normalized_db_url(get_database_url())
        engine = create_engine(
            db_url,
            pool_size=getattr(settings, "DATABASE_POOL_SIZE", 5),
            max_overflow=getattr(settings, "DATABASE_MAX_OVERFLOW", 10),
            pool_pre_ping=True,
            echo=getattr(settings, "DEBUG", False),
            future=True,  # API 2.x
        )
        logger.info(f"✅ Database engine created successfully → {db_url}")
        return engine
    except Exception as e:
        logger.error(f"❌ Error creating database engine: {e}")
        raise


engine = _create_engine()

SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    future=True,
)


# ============================================================
# Dependencia para FastAPI
# ============================================================
def get_db() -> Generator[Session, None, None]:
    """
    Uso en rutas:
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        try:
            db.close()
        except Exception as exc:
            logger.warning("No se pudo cerrar la sesión de DB: %s", exc)


# ============================================================
# Utilidades opcionales
# ============================================================
def test_connection() -> bool:
    """Devuelve True si SELECT 1 responde."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False


__all__ = ["engine", "SessionLocal", "get_db", "test_connection"]
