from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from .database import get_db  # Make sure this import matches your project structure
from . import schemas, models  # Adjust imports as necessary

app = FastAPI()

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, checked_in_only: bool = False, db: Session = Depends(get_db)):
    if skip < 0 or limit < 0:
        raise HTTPException(status_code=400, detail="Skip and limit query parameters must be non-negative")
    
    if checked_in_only:
        users = db.query(models.User).filter(models.User.checked_in == True).offset(skip).limit(limit).all()
    else:
        users = db.query(models.User).offset(skip).limit(limit).all()

    result = []
    for user in users:
        skills = [
            {"skill": user_skill.skill.skill_name, "rating": user_skill.rating}
            for user_skill in user.skills  # Assuming 'skills' is properly set up as a relationship on the User model
        ]
        user_dict = {
            "name": user.name,
            "company": user.company,
            "email": user.email,
            "phone": user.phone,
            "checked_in": user.checked_in,
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
        "checked_in": user.checked_in,
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
        "checked_in": user.checked_in,
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


@app.put("/users/{user_id}/checkin", response_model=schemas.User)
def checkin_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.checked_in:
        raise HTTPException(status_code=400, detail="User already checked in")
    
    user.checked_in = True
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
        "checked_in": user.checked_in,
        "skills": skills
    }

    return schemas.User(**user_dict)

@app.post("/scan/")
def scan_user(user_id: int, event_id: int, db: Session = Depends(get_db)):
    # Check if the event exists
    event = db.query(models.Event).filter(models.Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if the user exists
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the user is already scanned for the event
    existing_scan = db.query(models.ScanEvent).filter(
        models.ScanEvent.user_id == user_id,
        models.ScanEvent.event_id == event_id
    ).first()
    if existing_scan:
        raise HTTPException(status_code=400, detail="User already scanned for this event")

    # Create a new ScanEvent since the user hasn't been scanned for this event yet
    scan_event = models.ScanEvent(user_id=user_id, event_id=event_id)
    db.add(scan_event)
    db.commit()
    return {"message": "User scanned successfully"}


@app.get("/users/{user_id}/events/", response_model=List[schemas.Event])
def get_user_events(user_id: int, db: Session = Depends(get_db)):
    # Check if the user_id exists
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    scan_events = db.query(models.ScanEvent).filter(models.ScanEvent.user_id == user_id).all()
    event_ids = [scan_event.event_id for scan_event in scan_events]
    events = db.query(models.Event).filter(models.Event.event_id.in_(event_ids)).all()
    return events

@app.post("/hardware/{hardware_id}/signout")
def sign_out_hardware(hardware_id: int, user_id: int, db: Session = Depends(get_db)):
    hardware = db.query(models.Hardware).filter(models.Hardware.hardware_id == hardware_id).first()
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    
    if not hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if hardware.signed_out_by_user_id is not None:
        raise HTTPException(status_code=400, detail="Hardware is already signed out")
    
    hardware.signed_out_by_user_id = user_id
    db.commit()
    return {"message": f"Hardware {hardware.name} signed out by user {user_id} ({user.name})"}


@app.post("/hardware/{hardware_id}/return")
def return_hardware(hardware_id: int, db: Session = Depends(get_db)):
    hardware = db.query(models.Hardware).filter(models.Hardware.hardware_id == hardware_id).first()
    if not hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")
    if hardware.signed_out_by_user_id is None:
        raise HTTPException(status_code=400, detail="Hardware is not signed out")
    
    # Fetch the user who signed out the hardware
    user = db.query(models.User).filter(models.User.user_id == hardware.signed_out_by_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User who signed out the hardware not found")

    user_name = user.name  # Store user name before setting it to None
    hardware.signed_out_by_user_id = None
    db.commit()
    return {"message": f"Hardware {hardware.name} returned by user {user.user_id} ({user_name})"}


@app.get("/hacker/{user_id}/dashboard", response_model=schemas.HackerDashboard)
def get_hacker_dashboard(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    signed_out_hardware = db.query(models.Hardware).filter(models.Hardware.signed_out_by_user_id == user_id).all()
    checked_in_events = db.query(models.ScanEvent).filter(models.ScanEvent.user_id == user_id).all()

    dashboard_info = {
        "user_info": {
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "company": user.company,  # Make sure this field is included
            "checked_in": user.checked_in,  # Make sure this field is included
            "skills": [
                {"skill": skill.skill.skill_name, "rating": skill.rating}
                for skill in user.skills
            ],
        },
        "signed_out_hardware": [
            {"name": hardware.name, "serial_number": hardware.serial_number}
            for hardware in signed_out_hardware
        ],
        "checked_in_events": [
            {
                "name": event.event.name,
                "description": event.event.description,  # Make sure this field is included
                "start_time": event.event.start_time.isoformat(),
                "end_time": event.event.end_time.isoformat(),
                "location": event.event.location,  # Make sure this field is included
            }
            for event in checked_in_events
        ],
    }

    return dashboard_info
