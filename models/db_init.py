from extensions import db
from models.quizModel import Quiz, Question
from models.models import  User

def create_database(app):
    with app.app_context():
        db.create_all()
