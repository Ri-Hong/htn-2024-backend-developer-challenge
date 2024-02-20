# schemas.py

from datetime import datetime
from pydantic import field_validator, BaseModel, ConfigDict
from typing import List, Optional


# Define a schema for the skill with rating
class SkillBase(BaseModel):
    skill: str

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    rating: int
    model_config = ConfigDict(from_attributes=True)

class SkillUpdate(BaseModel):
    skill: str
    rating: int

# Define a schema for the User
class UserBase(BaseModel):
    name: str
    company: str
    email: str
    phone: str
    checked_in: bool

class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    checked_in: Optional[bool] = None
    skills: Optional[List[SkillUpdate]] = None


class User(UserBase):
    skills: List[Skill] = []
    model_config = ConfigDict(from_attributes=True)

class SkillFrequency(BaseModel):
    skill_name: str
    frequency: int
    model_config = ConfigDict(from_attributes=True)

class EventBase(BaseModel):
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str

    @field_validator('start_time', 'end_time', mode="before")
    @classmethod
    def format_datetime(cls, value):
        """
        If the value is a datetime, format it as a string.
        """
        if isinstance(value, datetime):
            return value.isoformat()
        return value

class EventCreate(EventBase):
    pass

class Event(EventBase):
    event_id: int
    model_config = ConfigDict(from_attributes=True)

class HardwareBase(BaseModel):
    name: str
    serial_number: str

class HackerDashboard(BaseModel):
    user_info: UserBase
    signed_out_hardware: List[HardwareBase]
    checked_in_events: List[EventBase]
    model_config = ConfigDict(from_attributes=True)
