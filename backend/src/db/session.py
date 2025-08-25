# Database session management
from sqlalchemy.orm import Session
from .base import SessionLocal, engine, Base

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_session() -> Session:
    """Get database session"""
    return SessionLocal()
