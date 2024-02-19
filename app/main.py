from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from .database import get_db  # Make sure this import matches your project structure
from . import schemas, models  # Adjust imports as necessary

app = FastAPI()

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    result = []
    for user in users:
        # Fetch skills through the UserSkill association and then access the Skill model
        skills = [
            {"skill_id": user_skill.skill.skill_id, "skill_name": user_skill.skill.skill_name, "rating": user_skill.rating}
            for user_skill in user.skills  # Assuming 'skills' is properly set up as a relationship on the User model
        ]
        user_dict = {
            "user_id": user.user_id,
            "name": user.name,
            "company": user.company,
            "email": user.email,
            "phone": user.phone,
            "skills": skills
        }
        result.append(schemas.User(**user_dict))  # Ensure this matches your schema class name exactly
    return result
