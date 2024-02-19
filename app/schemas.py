# schemas.py

from pydantic import BaseModel
from typing import List, Optional

# Define a schema for the skill with rating
class SkillBase(BaseModel):
    skill_name: str

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    skill_id: int
    rating: int
    class Config:
        orm_mode = True


# Define a schema for the User
class UserBase(BaseModel):
    name: str
    company: str
    email: str
    phone: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    user_id: int
    skills: List[Skill] = []
    
    class Config:
        orm_mode = True
