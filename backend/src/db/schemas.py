# Pydantic schemas for request/response validation
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Child schemas
class ChildBase(BaseModel):
    name: str
    birth_date: datetime
    gender: str
    guardian_name: str
    guardian_phone: str
    address: str
    community: str

class ChildCreate(ChildBase):
    pass

class Child(ChildBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# FollowUp schemas
class FollowUpBase(BaseModel):
    child_id: int
    weight: float
    height: float
    bmi: Optional[float] = None
    arm_circumference: Optional[float] = None
    head_circumference: Optional[float] = None
    triceps_skinfold: Optional[float] = None
    abdominal_perimeter: Optional[float] = None
    hemoglobin: Optional[float] = None
    clinical_observations: Optional[str] = None
    nutritional_status: Optional[str] = None
    recommendations: Optional[str] = None

class FollowUpCreate(FollowUpBase):
    pass

class FollowUp(FollowUpBase):
    id: int
    assessment_date: datetime
    
    class Config:
        from_attributes = True
