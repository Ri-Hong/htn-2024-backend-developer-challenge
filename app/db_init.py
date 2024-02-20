from datetime import datetime
import json
import logging
import random  # Import the random module
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Event, Hardware, User, Skill, UserSkill

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def init_db():
    db = SessionLocal()
    try:
        # Load events data from events.json file
        with open('events.json', 'r') as file:
            events_data = json.load(file)

        # Insert events data
        for event_data in events_data:
            # Convert epoch milliseconds to datetime
            event_data['start_time'] = datetime.utcfromtimestamp(event_data['start_time'] / 1000.0)
            event_data['end_time'] = datetime.utcfromtimestamp(event_data['end_time'] / 1000.0)

            # Check if event already exists
            if not db.query(Event).filter_by(event_id=event_data['id']).first():
                event = Event(
                    event_id=event_data['id'],
                    name=event_data['name'],
                    start_time=event_data['start_time'],
                    end_time=event_data['end_time'],
                    description=event_data['description'],
                    location=event_data['location']
                )
                db.add(event)
        db.commit()  # Commit after processing all events

        # Load hardware data from the hardware.json file
        with open('hardware.json', 'r') as file:
            hardware_data = json.load(file)

        # Insert hardware data
        for hardware in hardware_data:
            hardware = Hardware(
                name=hardware['name'],
                serial_number=hardware['serial_number']
            )   
            db.add(hardware)
        db.commit()  # Commit after processing all hardware


        # Load users data from HTN_2023_BE_Challenge_Data.json file
        with open('HTN_2023_BE_Challenge_Data.json', 'r') as file:
            data = json.load(file)

        for user_data in data:
            # Check for unique email and phone
            if db.query(User).filter((User.email == user_data['email']) | (User.phone == user_data['phone'])).first():
                logging.warning(f"Skipping user with duplicate email or phone: {user_data['email']} / {user_data['phone']}")
                continue

            # Randomly decide whether or not the user is checked in
            checked_in = random.choice([True, False])

            user = User(
                name=user_data['name'],
                company=user_data['company'],
                email=user_data['email'],
                phone=user_data['phone'],
                checked_in=checked_in  # Set the randomly determined checked_in status
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
