from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
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
            {"skill": user_skill.skill.skill_name, "rating": user_skill.rating}
            for user_skill in user.skills  # Assuming 'skills' is properly set up as a relationship on the User model
        ]
        user_dict = {
            "name": user.name,
            "company": user.company,
            "email": user.email,
            "phone": user.phone,
            "skills": skills
        }
        result.append(schemas.User(**user_dict))  # Ensure this matches your schema class name exactly
    return result

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        return None
    # Fetch skills through the UserSkill association and then access the Skill model
    skills = [
        {"skill": user_skill.skill.skill_name, "rating": user_skill.rating}
        for user_skill in user.skills
    ]
    user_dict = {
        "name": user.name,
        "company": user.company,
        "email": user.email,
        "phone": user.phone,
        "skills": skills
    }
    return schemas.User(**user_dict)


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user basic attributes
    update_data = user_update.dict(exclude_unset=True, exclude={"skills"})
    for key, value in update_data.items():
        setattr(user, key, value)

    # Initialize a set to keep track of processed skills
    processed_skills = set()

    # Handle skill updates
    if user_update.skills is not None:
        for skill_data in user_update.skills:
            # Skip if we've already processed an update for this skill
            if skill_data.skill in processed_skills:
                continue  # Skip this skill update
            
            # Add the skill to the set of processed skills
            processed_skills.add(skill_data.skill)
            
            # Validate the rating is between 1 and 5
            if not (1 <= skill_data.rating <= 5):
                raise HTTPException(status_code=400, detail=f"Invalid rating for skill: {skill_data.skill}. Rating must be between 1 and 5.")


            # Proceed with finding or creating the skill, and updating the rating as before
            skill = db.query(models.Skill).filter_by(skill_name=skill_data.skill).first()
            if not skill:
                skill = models.Skill(skill_name=skill_data.skill)
                db.add(skill)
                db.flush()  # To get the new skill ID
            
            user_skill = db.query(models.UserSkill).filter_by(user_id=user.user_id, skill_id=skill.skill_id).first()
            if user_skill:
                user_skill.rating = skill_data.rating
            else:
                db.add(models.UserSkill(user_id=user.user_id, skill_id=skill.skill_id, rating=skill_data.rating))

    db.commit()
    db.refresh(user)


    # Reconstruct the response with the updated skills
    skills = [
        {
            "skill": user_skill.skill.skill_name,
            "rating": user_skill.rating
        }
        for user_skill in user.skills
    ]

    user_dict = {
        "name": user.name,
        "company": user.company,
        "email": user.email,
        "phone": user.phone,
        "skills": skills
    }

    return schemas.User(**user_dict)


@app.get("/skills/", response_model=List[schemas.SkillFrequency])
def read_skill_frequencies(min_frequency: Optional[int] = Query(None), max_frequency: Optional[int] = Query(None), db: Session = Depends(get_db)):
    # Query to count the number of users with each skill
    query = (
        db.query(
            models.Skill.skill_name,  # Adjust attribute access as needed
            func.count(models.UserSkill.user_id).label("frequency")
        )
        .join(models.UserSkill, models.UserSkill.skill_id == models.Skill.skill_id)
        .group_by(models.Skill.skill_id)
    )
    
    # Apply filtering based on min_frequency and max_frequency
    if min_frequency is not None:
        query = query.having(func.count(models.UserSkill.user_id) >= min_frequency)
    if max_frequency is not None:
        query = query.having(func.count(models.UserSkill.user_id) <= max_frequency)
    
    skills = query.all()
    
    # Adjust the return to match your schema or desired format
    return [{"skill_name": skill.skill_name, "frequency": skill.frequency} for skill in skills]
