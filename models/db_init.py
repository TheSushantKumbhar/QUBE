from extensions import db
from models.models import  User
from models.quizModel import Quiz,Question,Option,QuizAttempt,UserAnswer

def create_database(app):
    with app.app_context():
        db.create_all()
