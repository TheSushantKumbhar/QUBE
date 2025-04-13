from extensions import db
from datetime import datetime
from models.models import User


class Quiz(db.Model):
    __tablename__ = "quizzes"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    is_live = db.Column(db.Boolean, default=False)
    
    always_available = db.Column(db.Boolean, default=True)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)

    time_limit = db.Column(db.Integer, default=0)  # 0 means no time limit
    time_unit = db.Column(db.String(10), default='minutes')  # 'minutes' or 'hours'
    
    user = db.relationship("User", backref=db.backref("quizzes", cascade="all, delete-orphan"))
    questions = db.relationship("Question", backref="quiz", cascade="all, delete-orphan")


class Question(db.Model):
    __tablename__ = "questions"
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    question_type = db.Column(db.String(20), nullable=False, default="single")  # 'single' or 'multiple'
    position = db.Column(db.Integer, nullable=False)  # Order in quiz

    options = db.relationship("Option", backref="question", cascade="all, delete-orphan")


class Option(db.Model):
    __tablename__ = "options"
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    position = db.Column(db.Integer, nullable=False)  # Order in question


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, nullable=True)

    quiz = db.relationship("Quiz", backref=db.backref("attempts", cascade="all, delete-orphan"))
    user = db.relationship("User", backref=db.backref("attempts", cascade="all, delete-orphan"))


class UserAnswer(db.Model):
    __tablename__ = "user_answers"
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey("options.id", ondelete="CASCADE"), nullable=False)
    
    attempt = db.relationship("QuizAttempt", backref=db.backref("answers", cascade="all, delete-orphan"))
    question = db.relationship("Question")
    option = db.relationship("Option")

    __table_args__ = (db.UniqueConstraint("attempt_id", "question_id", "option_id", name="uq_attempt_question_option"),)



db.Index("idx_quiz_user", Quiz.user_id)
db.Index("idx_question_quiz", Question.quiz_id)
db.Index("idx_option_question", Option.question_id)
db.Index("idx_attempt_quiz", QuizAttempt.quiz_id)
db.Index("idx_attempt_user", QuizAttempt.user_id)
db.Index("idx_user_answer_attempt", UserAnswer.attempt_id)
