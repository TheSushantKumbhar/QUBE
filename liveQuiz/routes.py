from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from models.models import User
from models.quizModel import Quiz, Question, Option
from models.liveQuizModels import LiveQuizRoom, LiveQuizParticipant, LiveQuizAnswer
from extensions import db
from createQuiz.routes import get_current_user, login_required
import random, string
import json

from liveQuiz.websockets import socketio 
from flask_socketio import SocketIO, emit, join_room, leave_room

live = Blueprint('live', __name__)


@live.route('/Home',methods=['GET','POST'])
def live_home():
    return render_template('liveQuiz/liveQuizHome.html')


@live.route('/CreateQuiz',methods=['GET','POST'])
@login_required
def Create_Quiz():
    user = get_current_user()
    quizzes = Quiz.query.filter_by(user_id=user.id).all()
    return render_template('liveQuiz/createQuiz.html',quizzes=quizzes)

@live.route('/join',methods =['GET','POST'] )
def join_quiz():
    return render_template('liveQuiz/joinQuiz.html')


@live.route('/quiz/live/<int:quiz_id>')
@login_required
def view_live_quiz(quiz_id):
    user = get_current_user()
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user owns this quiz
    if quiz.user_id != user.id:
        flash('You do not have permission to access this quiz', 'error')
        return redirect(url_for('quiz.my_quizzes'))
    
    # Check if there's already an active room for this quiz
    live_room = LiveQuizRoom.query.filter_by(quiz_id=quiz_id, is_active=True).first()
    
    return render_template('liveQuiz/liveQuizView.html', quiz=quiz, live_room=live_room, quiz_id=quiz.id)

@live.route('/quiz/live/<int:quiz_id>/create', methods=['POST'])
@login_required
def create_live_room(quiz_id):
    user = get_current_user()
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user owns this quiz
    if quiz.user_id != user.id:
        flash('You do not have permission to create a live room for this quiz', 'error')
        return redirect(url_for('quiz.my_quizzes'))
        
    # Check if there's already an active room for this quiz
    existing_room = LiveQuizRoom.query.filter_by(quiz_id=quiz_id, is_active=True).first()
    if existing_room:
        flash('There is already an active room for this quiz', 'warning')
        # Redirect directly to host view for the existing room
        return redirect(url_for('live.host_view', room_code=existing_room.room_code))
    
    # Generate a unique room code
    while True:
        room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not LiveQuizRoom.query.filter_by(room_code=room_code).first():
            break
    
    # Get question time from form
    question_time = request.form.get('question_time', 30, type=int)
    
    # Create a new live room
    new_room = LiveQuizRoom(
        room_code=room_code,
        quiz_id=quiz_id,
        host_id=user.id,
        question_time=question_time
    )
    
    db.session.add(new_room)
    db.session.commit()
    
    # Redirect directly to host view
    return redirect(url_for('live.host_view', room_code=room_code))

@live.route('/quiz/live/host/<string:room_code>')
@login_required
def host_view(room_code):
    user = get_current_user()
    
    # Get the room
    room = LiveQuizRoom.query.filter_by(room_code=room_code, is_active=True).first_or_404()
    
    # Check if user is the host
    if room.host_id != user.id:
        flash('You do not have permission to access the host view for this room', 'error')
        return redirect(url_for('quiz.my_quizzes'))
    
    # Get the quiz
    quiz = Quiz.query.get_or_404(room.quiz_id)
    
    # Get participants
    participants = LiveQuizParticipant.query.filter_by(room_id=room.id).all()
    
    return render_template('liveQuiz/hostView.html', room=room, quiz=quiz, participants=participants)


@live.route('/quiz/live/end', methods=['POST'])
@login_required
def end_live_room():
    user = get_current_user()
    room_code = request.form.get('room_code')
    
    if not room_code:
        flash('Invalid request', 'error')
        return redirect(url_for('quiz.my_quizzes'))
    
    # Get the room
    room = LiveQuizRoom.query.filter_by(room_code=room_code, is_active=True).first()
    
    if not room:
        flash('Room not found or already ended', 'error')
        return redirect(url_for('quiz.my_quizzes'))
    
    # Check if user is the host
    if room.host_id != user.id:
        flash('You do not have permission to end this room', 'error')
        return redirect(url_for('quiz.my_quizzes'))
    
    # End the room
    room.is_active = False
    db.session.commit()
    
    # Emit socket event to notify all participants
    socketio.emit('room_ended', {}, room=room_code)
    
    flash('Live quiz session ended successfully', 'success')
    return redirect(url_for('live.view_live_quiz', quiz_id=room.quiz_id))


# Update the host button URL in the liveQuizView.html template
@live.route('/quiz/live/<int:quiz_id>/update_host_link', methods=['POST'])
@login_required
def update_host_link(quiz_id):
    user = get_current_user()
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user owns this quiz
    if quiz.user_id != user.id:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    # Get active room
    room = LiveQuizRoom.query.filter_by(quiz_id=quiz_id, is_active=True).first()
    
    if not room:
        return jsonify({'success': False, 'error': 'No active room found'}), 404
    
    host_url = url_for('live.host_view', room_code=room.room_code)
    
    return jsonify({'success': True, 'host_url': host_url})