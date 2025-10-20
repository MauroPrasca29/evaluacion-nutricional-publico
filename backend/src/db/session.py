"""
Database session management for Nutritional Assessment API
-----------------------------------------------------------
Compatible with local Docker and Railway environments.
Handles SQLAlchemy engine, session, and table utilities.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging
import os

from src.core.config import settings, get_database_url  # Ajusta si tu estructura cambia

logger = logging.getLogger(__name__)

# ============================================================
# Database Engine
# ============================================================

def _get_engine():
    """
    Crea el engine de SQLAlchemy con fallback local si falla la URL principal.
    """
    try:
        db_url = get_database_url()
        if not db_url:
            # Fallback si no está definida DATABASE_URL
            db_url = (
                f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:"  # usuario
                f"{os.getenv('POSTGRES_PASSWORD', 'postgres')}@"           # contraseña
                f"{os.getenv('POSTGRES_HOST', 'db')}:"                     # host del contenedor
                f"{os.getenv('POSTGRES_PORT', '5432')}/"                   # puerto
                f"{os.getenv('POSTGRES_DB', 'railway')}"                   # base de datos
            )

        engine = create_engine(
            db_url,
            pool_size=getattr(settings, "DATABASE_POOL_SIZE", 5),
            max_overflow=getattr(settings, "DATABASE_MAX_OVERFLOW", 10),
            pool_pre_ping=True,
            echo=getattr(settings, "DEBUG", False),
            future=True,  # ✅ Requerido para SQLAlchemy 2.x
        )

        logger.info(f"✅ Database engine created successfully → {db_url}")
        return engine

    except Exception as e:
        logger.error(f"❌ Error creating database engine: {e}")
        raise


engine = _get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================
# Dependency for FastAPI
# ============================================================

def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection for DB sessions.
    Use it in routes like:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================
# Table Management Utilities
# ============================================================

def create_tables():
    """Create all database tables (usually at startup)."""
    try:
        from src.db.models import Base  # ensure models are imported
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """Drop all database tables (use with caution!)."""
    try:
        from src.db.models import Base
        Base.metadata.drop_all(bind=engine)
        logger.warning("⚠️ Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


# ============================================================
# High-Level Database Manager
# ============================================================

class DatabaseManager:
    """High-level database utilities."""

    @staticmethod
    def test_connection() -> bool:
        """Test if database connection works."""
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))  # ✅ SQLAlchemy 2.x requiere text()
            db.close()
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False

    @staticmethod
    def get_connection_info() -> dict:
        """Return connection parameters."""
        return {
            "url": get_database_url(),
            "pool_size": getattr(settings, "DATABASE_POOL_SIZE", 5),
            "max_overflow": getattr(settings, "DATABASE_MAX_OVERFLOW", 10),
            "echo": getattr(settings, "DEBUG", False),
        }

    @staticmethod
    def execute_raw_sql(sql: str, params: dict = None) -> list:
        """Execute raw SQL safely."""
        db = SessionLocal()
        try:
            result = db.execute(text(sql), params or {})
            return result.fetchall()
        except Exception as e:
            logger.error(f"Error executing raw SQL: {e}")
            raise
        finally:
            db.close()


# ============================================================
# Initialize Database Manager
# ============================================================

db_manager = DatabaseManager()
