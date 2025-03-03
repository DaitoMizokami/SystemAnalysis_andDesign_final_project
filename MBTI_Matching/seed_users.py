from app import app, db, User
from werkzeug.security import generate_password_hash
import random

# MBTI types
mbti_types = ['ISTJ', 'ISFJ', 'INFJ', 'INTJ', 'ISTP', 'ISFP', 'INFP', 'INTP',
              'ESTP', 'ESFP', 'ENFP', 'ENTP', 'ESTJ', 'ESFJ', 'ENFJ', 'ENTJ']

# Sample company names
company_names = [
    "TechInnovate", "EcoSolutions", "FinanceForward", "HealthHub", "CreativeMinds",
    "DataDynamics", "GreenEnergy", "SmartSystems", "GlobalConnect", "FutureWorks"
]

def create_job_seeker(index):
    return User(
        username=f"jobseeker{index}",
        email=f"jobseeker{index}@example.com",
        password=generate_password_hash("password123", method='sha256'),
        role="seeker",
        mbti=random.choice(mbti_types)
    )

def create_company(index):
    return User(
        username=company_names[index],
        email=f"company{index}@example.com",
        password=generate_password_hash("password123", method='sha256'),
        role="company",
        preferred_mbti=random.choice(mbti_types)
    )

def seed_users():
    with app.app_context():
        # Create 10 job seekers
        for i in range(10):
            db.session.add(create_job_seeker(i))

        # Create 10 companies
        for i in range(10):
            db.session.add(create_company(i))

        db.session.commit()
        print("Sample users seeded successfully.")

if __name__ == "__main__":
    seed_users()

