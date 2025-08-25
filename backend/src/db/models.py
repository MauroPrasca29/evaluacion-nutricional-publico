# SQLAlchemy models
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Child(Base):
    __tablename__ = "children"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    birth_date = Column(DateTime)
    gender = Column(String)
    guardian_name = Column(String)
    guardian_phone = Column(String)
    address = Column(Text)
    community = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    followups = relationship("FollowUp", back_populates="child")

class FollowUp(Base):
    __tablename__ = "followups"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    weight = Column(Float)
    height = Column(Float)
    bmi = Column(Float)
    arm_circumference = Column(Float)
    head_circumference = Column(Float)
    triceps_skinfold = Column(Float)
    abdominal_perimeter = Column(Float)
    hemoglobin = Column(Float)
    clinical_observations = Column(Text)
    nutritional_status = Column(String)
    recommendations = Column(Text)
    assessment_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    child = relationship("Child", back_populates="followups")
