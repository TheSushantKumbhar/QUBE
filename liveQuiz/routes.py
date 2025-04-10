from flask import Blueprint, render_template, request, redirect, url_for,session
from createQuiz.routes import login_required
from utils.auth_helpers import get_current_user
from models.quizModel import Quiz  # adjust according to your project structure

live = Blueprint('live', __name__, url_prefix='/live')

from liveQuiz.websockets import socketio

# Home route (optional, could be in main app.py)
@live.route('/')
def live_home():
    return render_template('liveQuiz/liveQuizHome.html',username=session.get('username'),profile_pic=session.get('profile_pic'))

# Host quiz selection page
@live.route('/host', methods=['GET'])
@login_required
def host_room():
    current_user = get_current_user()
    quizzes = Quiz.query.filter_by(user_id=current_user.id).all()
    return render_template('liveQuiz/hostView.html', quizzes=quizzes,current_user = current_user,username=session.get('username'),profile_pic=session.get('profile_pic'))

# Join room page
@live.route('/join', methods=['GET'])
def join_room():
    return render_template('liveQuiz/joinQuiz.html',username=session.get('username'),profile_pic=session.get('profile_pic'))    

# View created quizzes to host
@live.route('/CreateQuiz', methods=['GET'])
@login_required
def create_Quiz():
    current_user = get_current_user()
    quizzes = Quiz.query.filter_by(user_id=current_user.id).all()
    return render_template('liveQuiz/createQuiz.html', quizzes=quizzes,username=session.get('username'),profile_pic=session.get('profile_pic'))
