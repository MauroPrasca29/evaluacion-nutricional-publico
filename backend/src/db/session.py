"""
Database session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

from core.config import settings, get_database_url

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    get_database_url(),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before use
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
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

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def drop_tables():
    """Drop all database tables (use with caution!)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise

class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def test_connection() -> bool:
        """Test database connection"""
        try:
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    @staticmethod
    def get_connection_info() -> dict:
        """Get database connection information"""
        return {
            "url": get_database_url(),
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "echo": settings.DEBUG
        }
    
    @staticmethod
    def execute_raw_sql(sql: str, params: dict = None) -> list:
        """Execute raw SQL query"""
        db = SessionLocal()
        try:
            result = db.execute(sql, params or {})
            return result.fetchall()
        except Exception as e:
            logger.error(f"Error executing raw SQL: {e}")
            raise
        finally:
            db.close()

# Initialize database manager
db_manager = DatabaseManager()
