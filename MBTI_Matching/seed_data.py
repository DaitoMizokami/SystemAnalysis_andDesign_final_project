# seed_data.py
from app import db, User, app
from werkzeug.security import generate_password_hash
import random

with app.app_context():
    mbti_list = ["INTJ", "ENTP", "INFP", "ESFJ", "ISTJ", "ENFJ", "ISTP", "ISFJ", "ENTJ", "INTP", "ENFP", "ISFP", "ESTJ", "ESFP", "ESTP", "INFJ"]
    # パスワードは全て「password」
    hashed_pw = generate_password_hash("password", method='scrypt')

    for i in range(1, 21):
        chosen_mbti = random.choice(mbti_list)
        answer1 = random.randint(1, 5)
        answer2 = random.randint(1, 5)
        answer3 = random.randint(1, 5)
        answer4 = random.randint(1, 5)
        answer5 = random.randint(1, 5)

        new_user = User(
            username=f"seeker{i}",
            email=f"seeker{i}@example.com",
            role="seeker",
            mbti=chosen_mbti,
            password=hashed_pw,
            answer1=answer1,
            answer2=answer2,
            answer3=answer3,
            answer4=answer4,
            answer5=answer5
        )
        db.session.add(new_user)

    db.session.commit()
    print("Seeker data inserted successfully!")
