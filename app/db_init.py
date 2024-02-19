import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Skill, UserSkill

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def init_db():
    db = SessionLocal()
    try:
        with open('HTN_2023_BE_Challenge_Data.json', 'r') as file:
            data = json.load(file)

        for user_data in data:
            # Check for unique email and phone
            if db.query(User).filter((User.email == user_data['email']) | (User.phone == user_data['phone'])).first():
                logging.warning(f"Skipping user with duplicate email or phone: {user_data['email']} / {user_data['phone']}")
                continue

            user = User(
                name=user_data['name'],
                company=user_data['company'],
                email=user_data['email'],
                phone=user_data['phone']
            )
            db.add(user)
            db.flush()  # Assign ID without committing

            # Track seen skills for the current user to catch duplicates before committing
            seen_skills = set()

            for skill_data in user_data['skills']:
                skill_name = skill_data['skill']
                if skill_name in seen_skills:
                    logging.warning(f"Skipping duplicate skill entry for user: {user_data['email']}, Skill: {skill_name}")
                    continue
                seen_skills.add(skill_name)

                skill = db.query(Skill).filter_by(skill_name=skill_name).first()
                if not skill:
                    skill = Skill(skill_name=skill_name)
                    db.add(skill)
                    db.flush()  # Assign ID without committing

                user_skill = UserSkill(user_id=user.user_id, skill_id=skill.skill_id, rating=skill_data['rating'])
                db.add(user_skill)

            db.commit()  # Commit after processing all skills for a user

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
