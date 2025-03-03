from app import app, db, Question

questions = [
    "Do you prefer working in a team?",
    "Are you comfortable with fast-paced environments?",
    "Do you value creativity in your work?",
    "How important is work-life balance for you?",
    "Do you enjoy problem-solving tasks?"
]

def seed_questions():
    with app.app_context():
        for question_text in questions:
            question = Question(text=question_text)
            db.session.add(question)
        db.session.commit()
        print("Questions seeded successfully.")

if __name__ == "__main__":
    seed_questions()

