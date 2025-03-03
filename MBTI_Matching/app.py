# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mbti_matching.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    mbti = db.Column(db.String(4))
    preferred_mbti = db.Column(db.String(4))
    answer1 = db.Column(db.Integer)  # 質問1の回答
    answer2 = db.Column(db.Integer)  # 質問2の回答
    answer3 = db.Column(db.Integer)  # 質問3の回答
    answer4 = db.Column(db.Integer)  # 質問4の回答
    answer5 = db.Column(db.Integer)  # 質問5の回答

# Question model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)

# Answer model
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seeker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    seeker = db.relationship('User', foreign_keys=[seeker_id], backref='seeker_matches')
    company = db.relationship('User', foreign_keys=[company_id], backref='company_matches')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # フォームデータの取得
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = request.form['role']
            mbti = request.form.get('mbti')  # 求職者のMBTI
            preferred_mbti = request.form.get('preferred_mbti')  # 企業のPreferred MBTI

            # 企業のPreferred Answers（質問回答）
            answer1 = request.form.get('answer1', type=int)
            answer2 = request.form.get('answer2', type=int)
            answer3 = request.form.get('answer3', type=int)
            answer4 = request.form.get('answer4', type=int)
            answer5 = request.form.get('answer5', type=int)

            # デバッグ用ログ
            print(f"Debug: username={username}, email={email}, role={role}, mbti={mbti}, preferred_mbti={preferred_mbti}")

            # 同じメールアドレスのユーザーが存在するか確認
            user = User.query.filter_by(email=email).first()
            if user:
                flash('Email address already exists')
                return redirect(url_for('register'))

            # 求職者と企業でデータを分岐して保存
            if role == 'seeker':
                new_user = User(
                    username=username,
                    email=email,
                    role=role,
                    password=generate_password_hash(password, method='scrypt'),
                    mbti=mbti
                )
            elif role == 'company':
                # 企業のデータが正しく取得されているか検証
                if not (preferred_mbti and answer1 and answer2 and answer3 and answer4 and answer5):
                    flash('All fields are required for company registration')
                    return redirect(url_for('register'))

                new_user = User(
                    username=username,
                    email=email,
                    role=role,
                    password=generate_password_hash(password, method='scrypt'),
                    preferred_mbti=preferred_mbti,
                    answer1=answer1,
                    answer2=answer2,
                    answer3=answer3,
                    answer4=answer4,
                    answer5=answer5
                )
            else:
                flash('Invalid role selected')
                return redirect(url_for('register'))

            # データベースに保存
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))

        except Exception as e:
            # エラーをキャッチしてログに記録
            print(f"Debug: An error occurred during registration: {e}")
            flash('An unexpected error occurred. Please try again.')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        # パスワードをハッシュ化された値と比較
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'seeker':
        return redirect(url_for('questionnaire'))
    else:
        return redirect(url_for('company_dashboard'))

@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    questions = [
        {"id": 1, "text": "Do you prefer working in a team?"},
        {"id": 2, "text": "Are you comfortable with fast-paced environments?"},
        {"id": 3, "text": "Do you value creativity in your work?"},
        {"id": 4, "text": "How important is work-life balance for you?"},
        {"id": 5, "text": "Do you enjoy problem-solving tasks?"},
    ]

    if request.method == 'POST':
        answers = {
            f"question_{q['id']}": request.form.get(f"question_{q['id']}")
            for q in questions
        }
        user = User.query.get(current_user.id)
        user.answer1 = answers.get("question_1")
        user.answer2 = answers.get("question_2")
        user.answer3 = answers.get("question_3")
        user.answer4 = answers.get("question_4")
        user.answer5 = answers.get("question_5")
        db.session.commit()
        flash("Questionnaire submitted successfully.")
        return redirect(url_for('results'))

    return render_template('questionnaire.html', questions=questions)

def calculate_question_score(ideal_answer, user_answer):
    max_score = 100
    difference = abs(ideal_answer - user_answer)
    if difference >= 4:
        score = 0
    else:
        score = max_score - (difference * 25)
    return score

def save_matching_results(seeker_id, matched_company_ids):
    for company_id in matched_company_ids:
        match = Match(seeker_id=seeker_id, company_id=company_id)
        db.session.add(match)
    db.session.commit()

@app.route('/results')
@login_required
def results():
    user = User.query.get(current_user.id)
    if not user or user.role != "seeker":
        flash("You are not authorized to view this page.")
        return redirect(url_for('login'))
    
    companies = User.query.filter_by(role="company").all()
    matched_companies = []

    for company in companies:
        mbti_match = (company.preferred_mbti == user.mbti)
        total_score = 0
        question_count = 0

        for i in range(1, 6):
            ideal_answer = getattr(company, f"answer{i}")
            user_answer = getattr(user, f"answer{i}")

            if ideal_answer is not None and user_answer is not None:
                total_score += calculate_question_score(ideal_answer, user_answer)
                question_count += 1
        
        percentage_score = (total_score / question_count) if question_count > 0 else 0
        company_data = {
            "company": company,
            "mbti_match": mbti_match,
            "percentage_score": round(percentage_score, 2)
        }
        matched_companies.append(company_data)

    matched_companies.sort(key=lambda x: x['percentage_score'], reverse=True)
    top_matched = matched_companies[:10]

    # **ここにマッチング結果を保存**
    save_matching_results(user.id, [c['company'].id for c in top_matched])

    return render_template('results.html', matched=top_matched)
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get(current_user.id)
    if not user:
        flash("User not found")
        return redirect(url_for('dashboard'))

    # 質問文を定義
    questions = [
        "Do you prefer working in a team?",
        "Are you comfortable with fast-paced environments?",
        "Do you value creativity in your work?",
        "How important is work-life balance for you?",
        "Do you enjoy problem-solving tasks?"
    ]

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']

        if user.role == 'seeker':
            user.mbti = request.form['mbti']
        elif user.role == 'company':
            user.preferred_mbti = request.form['preferred_mbti']
            user.answer1 = request.form.get('answer1', type=int)
            user.answer2 = request.form.get('answer2', type=int)
            user.answer3 = request.form.get('answer3', type=int)
            user.answer4 = request.form.get('answer4', type=int)
            user.answer5 = request.form.get('answer5', type=int)

        db.session.commit()
        flash("Profile updated successfully!")
        return redirect(url_for('dashboard'))

    return render_template('edit_profile.html', user=user, questions=questions)


    import sqlite3
@app.route('/company_dashboard')
@login_required
def company_dashboard():
    if current_user.role != 'company':
        flash('Access denied.')
        return redirect(url_for('index'))

    # デバッグ用: ログイン中の企業情報を表示
    print(f"DEBUG: Current company ID: {current_user.id}")
    print(f"DEBUG: Preferred MBTI: {current_user.preferred_mbti}")
    print(f"DEBUG: Answers: {current_user.answer1}, {current_user.answer2}, {current_user.answer3}, {current_user.answer4}, {current_user.answer5}")

    # すべての求職者を取得
    seekers = User.query.filter_by(role='seeker').all()
    print(f"DEBUG: Seekers found: {len(seekers)}")
    for seeker in seekers:
        print(f"DEBUG: Seeker Username: {seeker.username}, MBTI: {seeker.mbti}, Answers: "
              f"{seeker.answer1}, {seeker.answer2}, {seeker.answer3}, {seeker.answer4}, {seeker.answer5}")

    matched_seekers = []

    for seeker in seekers:
        # マッチングスコアを計算
        total_score = 0
        question_count = 0

        for i in range(1, 6):
            ideal_answer = getattr(current_user, f"answer{i}")
            seeker_answer = getattr(seeker, f"answer{i}")

            # デバッグ用: 各質問の回答を表示
            print(f"DEBUG: Question {i}: Company Answer = {ideal_answer}, Seeker Answer = {seeker_answer}")

            if ideal_answer is not None and seeker_answer is not None:
                total_score += calculate_question_score(ideal_answer, seeker_answer)
                question_count += 1

        percentage_score = (total_score / question_count) if question_count > 0 else 0
        mbti_match = (current_user.preferred_mbti == seeker.mbti)

        # デバッグ用: スコアとMBTI一致の結果を表示
        print(f"DEBUG: Seeker: {seeker.username}, MBTI Match: {mbti_match}, Total Score: {percentage_score}")

        if question_count > 0:
            matched_seekers.append({
                "username": seeker.username,
                "email": seeker.email,
                "mbti": seeker.mbti,
                "percentage_score": round(percentage_score, 2),
                "mbti_match": mbti_match
            })
    
    # スコアでソート
    matched_seekers.sort(key=lambda x: x['percentage_score'], reverse=True)
    print(f"DEBUG: Matched Seekers: {matched_seekers}")

    # MBTIマッチと非マッチを分けて上位5件ずつ取得
    mbti_matched_seekers = [s for s in matched_seekers if s['mbti_match']]
    mbti_unmatched_seekers = [s for s in matched_seekers if not s['mbti_match']]

    top_matched = mbti_matched_seekers[:5]
    top_unmatched = mbti_unmatched_seekers[:5]

    final_seekers = top_matched + top_unmatched

    # テンプレートに渡す直前に再度確認
    print(f"DEBUG: Final Seekers after limit: {final_seekers}")

    return render_template('company_dashboard.html', seekers=final_seekers)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
