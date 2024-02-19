# crud.py

from sqlalchemy.orm import Session
from . import models, schemas

# CRUD operations for Participant
def get_participants(db: Session):
    return db.query(models.Participant).all()

def get_participant(db: Session, participant_id: int):
    return db.query(models.Participant).filter(models.Participant.id == participant_id).first()

def get_skill_ratings(db: Session, participant_id: int, skill_id: int):
    return db.query(models.participant_skill_table).filter(
        models.participant_skill_table.c.participant_id == participant_id, 
        models.participant_skill_table.c.skill_id == skill_id
    ).first()


def create_participant(db: Session, participant: schemas.ParticipantCreate):
    db_participant = models.Participant(**participant.dict())
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant

# CRUD operations for Skill
def get_skill(db: Session, skill_id: int):
    return db.query(models.Skill).filter(models.Skill.id == skill_id).first()

def get_skills(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Skill).offset(skip).limit(limit).all()

def create_skill(db: Session, skill: schemas.SkillCreate):
    db_skill = models.Skill(**skill.dict())
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

# CRUD operations for ParticipantSkills (Ratings)
def create_participant_skill(db: Session, participant_id: int, skill_id: int, rating: int):
    db_participant_skill = models.participant_skill_table.insert().values(
        participant_id=participant_id, 
        skill_id=skill_id, 
        rating=rating
    )
    db.execute(db_participant_skill)
    db.commit()
    return db.query(models.participant_skill_table).filter(
        models.participant_skill_table.c.participant_id == participant_id, 
        models.participant_skill_table.c.skill_id == skill_id
    ).first()


def update_participant_skills(db: Session, participant_id: int, participant_update: schemas.ParticipantUpdate):
    db_participant = db.query(models.Participant).filter(models.Participant.id == participant_id).first()
    if not db_participant:
        return None  # Participant not found

    update_data = participant_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_participant, key) and value is not None:
            setattr(db_participant, key, value)
    db.commit()
    # if participant_update.skills:
    #     for skill_update in participant_update.skills:
    #         skill = db.query(models.Skill).filter(models.Skill.id == skill_update.skill_id).first()
    #         if not skill:
    #             # If skill_id is not provided or doesn't exist, check by skill name; create if necessary
    #             if skill_update.skill:
    #                 skill = db.query(models.Skill).filter(models.Skill.skill == skill_update.skill).first()
    #                 if not skill:
    #                     skill = models.Skill(skill=skill_update.skill)
    #                     db.add(skill)
    #                     db.commit()
    #                     db.refresh(skill)
    #         # Now, update or add the skill rating
    #         if skill:
    #             assoc = db.query(models.participant_skill_table).filter_by(participant_id=participant_id, skill_id=skill.id).first()
    #             if assoc:
    #                 # Update rating
    #                 db.execute(
    #                     models.participant_skill_table.update().where(
    #                         models.participant_skill_table.c.participant_id == participant_id,
    #                         models.participant_skill_table.c.skill_id == skill.id
    #                     ).values(rating=skill_update.rating)
    #                 )
    #             else:
    #                 # Insert new skill rating
    #                 db.execute(
    #                     models.participant_skill_table.insert().values(
    #                         participant_id=participant_id, skill_id=skill.id, rating=skill_update.rating
    #                     )
    #                 )
    #         db.commit()
    return db_participant
