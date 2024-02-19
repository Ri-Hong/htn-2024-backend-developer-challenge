# models.py

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    company = Column(String)
    email = Column(String, unique=True)
    phone = Column(String, unique=True)

class Skill(Base):
    __tablename__ = 'Skills'

    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String, unique=True)

class UserSkill(Base):
    __tablename__ = 'UserSkills'

    user_id = Column(Integer, ForeignKey('Users.user_id'), primary_key=True)
    skill_id = Column(Integer, ForeignKey('Skills.skill_id'), primary_key=True)
    rating = Column(Integer)
    user = relationship("User", back_populates="skills")
    skill = relationship("Skill")

User.skills = relationship("UserSkill", back_populates="user")
Skill.users = relationship("UserSkill", back_populates="skill")
