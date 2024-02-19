# schemas.py

from pydantic import BaseModel
from typing import List, Optional

# Define a schema for the skill with rating
class SkillBase(BaseModel):
    skill: str

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    rating: int
    class Config:
        orm_mode = True

class SkillUpdate(BaseModel):
    skill: str
    rating: int

# Define a schema for the User
class UserBase(BaseModel):
    name: str
    company: str
    email: str
    phone: str

class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[SkillUpdate]] = None


class User(UserBase):
    skills: List[Skill] = []
    
    class Config:
        orm_mode = True

class SkillFrequency(BaseModel):
    skill_name: str
    frequency: int

    class Config:
        orm_mode = True
