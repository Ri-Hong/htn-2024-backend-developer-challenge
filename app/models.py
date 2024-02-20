import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    company = Column(String)
    email = Column(String, unique=True)
    phone = Column(String, unique=True)
    checked_in = Column(Boolean, default=False)
    skills = relationship("UserSkill", back_populates="user")
    scan_events = relationship("ScanEvent", back_populates="user")

class Skill(Base):
    __tablename__ = 'Skills'

    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String, unique=True)
    users = relationship("UserSkill", back_populates="skill")

class UserSkill(Base):
    __tablename__ = 'UserSkills'

    user_id = Column(Integer, ForeignKey('Users.user_id'), primary_key=True)
    skill_id = Column(Integer, ForeignKey('Skills.skill_id'), primary_key=True)
    rating = Column(Integer)
    user = relationship("User", back_populates="skills")
    skill = relationship("Skill", back_populates="users")

class Event(Base):
    __tablename__ = 'Events'

    event_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    description = Column(String)
    location = Column(String)
    scan_events = relationship("ScanEvent", back_populates="event")

class ScanEvent(Base):
    __tablename__ = 'ScanEvents'

    scan_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    event_id = Column(Integer, ForeignKey('Events.event_id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="scan_events")
    event = relationship("Event", back_populates="scan_events")

class Hardware(Base):
    __tablename__ = 'Hardware'

    hardware_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    serial_number = Column(String, unique=True)
    signed_out_by_user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=True)

    # Relationship to the User model (assuming a User can sign out multiple hardware items)
    user = relationship("User", backref="signed_out_hardware")
