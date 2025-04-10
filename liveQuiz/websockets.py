# File: websocket.py
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import time
from models.quizModel import Quiz, Question
from models.models import User
from sqlalchemy.orm import joinedload

socketio = SocketIO()

rooms = {}  # room_code: {host_id, participants: {sid: username}, quiz, current_q, leaderboard, timer, question_end_time}

@socketio.on('create_room')
def create_room(data):
    room_code = data['room_code']
    quiz_id = data['quiz_id']
    host_id = data['host_id']
    quiz = Quiz.query.options(joinedload(Quiz.questions)).get(quiz_id)

    if room_code in rooms:
        emit('error', {'message': 'Room already exists'})
        return

    # Process questions and correct answers properly
    processed_questions = []
    for q in quiz.questions:
        correct_indices = []
        options = []
        for i, opt in enumerate(q.options):
            options.append(opt.text)
            if opt.is_correct:
                correct_indices.append(i)  # Store indices of correct options
                
        processed_questions.append({
            'id': q.id,
            'text': q.text,
            'options': options,
            'correct_indices': correct_indices  # Store which indices are correct
        })

    rooms[room_code] = {
        'host_id': host_id,
        'participants': {},
        'quiz': {
            'id': quiz.id,
            'title': quiz.title,
            'questions': processed_questions
        },
        'current_q': 0,
        'leaderboard': {},
        'timer': None,
        'question_end_time': None
    }

    join_room(room_code)
    emit('room_created', {'room_code': room_code})

@socketio.on('join_room')
def join_room_handler(data):
    room_code = data['room_code']
    username = data['username']

    if room_code not in rooms:
        emit('error', {'message': 'Room not found'})
        return

    sid = request.sid  
    rooms[room_code]['participants'][sid] = username
    rooms[room_code]['leaderboard'][username] = 0  # Initialize score
    join_room(room_code)

    emit('joined_room', {'room_code': room_code, 'username': username})
    
    # If question is in progress, send the current question to the new participant
    room = rooms[room_code]
    if room['current_q'] < len(room['quiz']['questions']) and room['question_end_time']:
        remaining_time = max(0, int(room['question_end_time'] - time.time()))
        if remaining_time > 0:
            q = room['quiz']['questions'][room['current_q']]
            emit('new_question', {
                'question': q['text'],
                'options': q['options'],
                'qid': q['id'],
                'time': remaining_time  # Send remaining time
            })
    
    # Broadcast updated participants to everyone in the room
    usernames = list(rooms[room_code]['participants'].values())
    emit('update_participants', {'participants': usernames}, room=room_code)
    
    # Send current leaderboard to the new participant
    emit('leaderboard_update', room['leaderboard'])

@socketio.on('start_quiz')
def start_quiz(data):
    room_code = data['room_code']

    room = rooms.get(room_code)
    if not room:
        emit('error', {'message': 'Room not found'})
        return

    room['current_q'] = 0  # Reset to first question
    room['leaderboard'] = {name: 0 for name in room['participants'].values()}  # Reset scores
    send_question(room_code)

def send_question(room_code):
    room = rooms[room_code]
    questions = room['quiz']['questions']
    current_q = room['current_q']

    if current_q >= len(questions):
        socketio.emit('quiz_ended', {'leaderboard': room['leaderboard']}, room=room_code)
        return

    q = questions[current_q]
    question_time = 15  # Default time per question
    
    # Set end time for synchronization
    room['question_end_time'] = time.time() + question_time
    
    socketio.emit('new_question', {
        'question': q['text'],
        'options': q['options'],
        'qid': q['id'],
        'time': question_time
    }, room=room_code)

    # Schedule next question
    if room['timer']:
        socketio.sleep(0)  # Cancel any existing timers
    room['timer'] = socketio.start_background_task(question_timer, room_code, question_time)

def question_timer(room_code, seconds):
    socketio.sleep(seconds)
    room = rooms.get(room_code)
    if room:
        room['current_q'] += 1
        send_question(room_code)

@socketio.on('submit_answer')
def handle_answer(data):
    room_code = data['room_code']
    qid = data['qid']
    answer_index = data['answer']  # The index of the selected option
    sid = request.sid

    room = rooms.get(room_code)
    if not room:
        emit('error', {'message': 'Room not found'})
        return
    
    # Find the current question
    question = next((q for q in room['quiz']['questions'] if q['id'] == qid), None)
    username = room['participants'].get(sid)
    
    if not question or not username:
        return
        
    # Check if answer is correct using the index
    if answer_index in question['correct_indices']:
        # Calculate points based on remaining time
        remaining_time = max(0, room['question_end_time'] - time.time())
        points = max(1, int(remaining_time))  # Minimum 1 point, more for faster answers
        room['leaderboard'][username] = room['leaderboard'].get(username, 0) + points

    # Update leaderboard for everyone
    socketio.emit('leaderboard_update', room['leaderboard'], room=room_code)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    # Find which room this user is in
    for room_code, room in list(rooms.items()):
        if sid in room['participants']:
            username = room['participants'].pop(sid)
            # Don't remove from leaderboard - keep their score
            leave_room(room_code)
            emit('user_left', {'username': username}, room=room_code)
            
            # Update participants list
            usernames = list(room['participants'].values())
            emit('update_participants', {'participants': usernames}, room=room_code)
            
            # If room is empty except for host, consider cleaning up
            if not room['participants']:
                # Optional: Auto-cleanup empty rooms
                # rooms.pop(room_code, None)
                pass
            break

@socketio.on('end_quiz')
def end_quiz(data):
    room_code = data['room_code']
    room = rooms.get(room_code)
    if room:
        # Don't remove the room yet, just end the quiz
        if room['timer']:
            socketio.sleep(0)  # Cancel timer
            room['timer'] = None
        
        socketio.emit('quiz_ended', {'leaderboard': room['leaderboard']}, room=room_code)


# Add this function to your websocket.py file

@socketio.on('end_room')
def end_room(data):
    room_code = data['room_code']
    
    # Check if room exists
    if room_code not in rooms:
        emit('error', {'message': 'Room not found'})
        return
    
    # Notify all participants that the room is closing
    socketio.emit('room_closed', {
        'message': 'The host has ended this session. Thank you for participating!'
    }, room=room_code)
    
    # Remove the room from the rooms dictionary
    if room_code in rooms:
        rooms.pop(room_code)
    
    # Confirm to host
    emit('room_ended', {'success': True})