from flask import Blueprint, render_template, request, jsonify, flash, redirect, session,url_for, session as flask_session
from models.models import User
from models.quizModel import Quiz
live = Blueprint('live', __name__)


def get_current_user():
    """Fetch the logged-in user from session"""
    user_email = session.get('user')
    if user_email:
        return User.query.filter_by(email=user_email).first()
    return None

from functools import wraps

def login_required(func):
    """Decorator to ensure user is logged in"""
    @wraps(func)  # Preserve the original function name
    def wrapper(*args, **kwargs):
        if not get_current_user():
            return redirect('/auth/login')  # Ensure correct Firebase login route
        return func(*args, **kwargs)
    return wrapper


@live.route('/Home',methods=['GET','POST'])
def live_home():
    return render_template('liveQuiz/liveQuizHome.html')


@live.route('/CreateQuiz',mothods=['GET','POST'])
def Create_Quiz():
    user = get_current_user()
    quizzes = Quiz.query.filter_by(user_id=user.id).all()
    return render_template('liveQuiz/createQuiz.html')

