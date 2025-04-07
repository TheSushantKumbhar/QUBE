from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from extensions import db
from models.liveQuizModels import LiveQuizRoom, LiveQuizParticipant, LiveQuizAnswer
from flask import request, session
import functools

socketio = SocketIO()

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

@socketio.on('connect')
def handle_connect():
    print('Client connected', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected', request.sid)
    
    # Check if this was a participant disconnecting
    participant_id = session.get('participant_id')
    if participant_id:
        participant = LiveQuizParticipant.query.get(participant_id)
        if participant:
            room = LiveQuizRoom.query.get(participant.room_id)
            if room:
                # Notify host about participant disconnection
                emit('participant_disconnected', {
                    'participant_id': participant_id,
                    'display_name': participant.display_name
                }, room=room.room_code)
                
                print(f"Participant {participant.display_name} disconnected from room: {room.room_code}")

@socketio.on('join_host_room')
@authenticated_only
def handle_join_host_room(data):
    room_code = data['room_code']
    
    # Get the room
    room = LiveQuizRoom.query.filter_by(room_code=room_code, is_active=True).first()
    
    if not room or room.host_id != session['user_id']:
        return {'success': False, 'error': 'Room not found or you are not the host'}
    
    join_room(room_code)
    print(f"Host joined room: {room_code}")
    
    emit('host_joined_room', {'success': True})

@socketio.on('join_participant_room')
def handle_join_participant_room(data):
    room_code = data['room_code']
    display_name = data['display_name']
    user_id = session.get('user_id')  # Optional, for logged in users
    
    # Get the room
    room = LiveQuizRoom.query.filter_by(room_code=room_code, is_active=True).first()
    
    if not room:
        emit('join_response', {'success': False, 'error': 'Room not found or inactive'})
        return
    
    # Check if the quiz is already in progress
    if room.current_question_index >= 0:
        emit('join_response', {'success': False, 'error': 'Quiz already in progress'})
        return
    
    # Check if display name is already taken in this room
    existing_participant = LiveQuizParticipant.query.filter_by(
        room_id=room.id, 
        display_name=display_name
    ).first()
    
    if existing_participant:
        emit('join_response', {'success': False, 'error': 'Name already taken'})
        return
    
    # Create participant
    participant = LiveQuizParticipant(
        room_id=room.id,
        user_id=user_id,
        display_name=display_name
    )
    
    db.session.add(participant)
    db.session.commit()
    
    # Store participant ID in session
    session['participant_id'] = participant.id
    session['room_code'] = room_code
    
    # Join the room
    join_room(room_code)
    
    # Notify host about new participant
    emit('new_participant', {
        'participant_id': participant.id,
        'display_name': display_name,
        'user_id': user_id
    }, room=room_code)
    
    print(f"Participant {display_name} joined room: {room_code}")
    
    # Send success response with redirect info
    emit('join_response', {
        'success': True, 
        'participant_id': participant.id,
        'room_code': room_code
    })

@socketio.on('leave_room')
def handle_leave_room(data):
    room_code = data.get('room_code')
    participant_id = session.get('participant_id')
    
    if room_code and participant_id:
        # Get the participant
        participant = LiveQuizParticipant.query.get(participant_id)
        
        if participant:
            room = LiveQuizRoom.query.get(participant.room_id)
            
            # Delete the participant
            display_name = participant.display_name
            db.session.delete(participant)
            db.session.commit()
            
            # Notify host about participant leaving
            if room and room.room_code == room_code:
                emit('participant_left', {
                    'participant_id': participant_id,
                    'display_name': display_name
                }, room=room_code)
            
            # Leave the Socket.IO room
            leave_room(room_code)
            
            # Remove participant ID from session
            session.pop('participant_id', None)
            session.pop('room_code', None)
            
            print(f"Participant {display_name} left room: {room_code}")
            
            return {'success': True}
    
    return {'success': False, 'error': 'Room or participant not found'}

@socketio.on('start_quiz')
@authenticated_only
def handle_start_quiz(data):
    room_code = data['room_code']
    
    # Get the room
    room = LiveQuizRoom.query.filter_by(room_code=room_code, is_active=True).first()
    
    if not room or room.host_id != session['user_id']:
        return {'success': False, 'error': 'Room not found or you are not the host'}
    
    # Set current question index to 0 (first question)
    room.current_question_index = 0
    db.session.commit()
    
    # Notify all participants that the quiz has started
    emit('quiz_started', {}, room=room_code)
    
    print(f"Quiz started in room: {room_code}")
    
    return {'success': True}

@socketio.on('submit_answer')
def handle_submit_answer(data):
    participant_id = session.get('participant_id')
    question_id = data.get('question_id')
    option_id = data.get('option_id')
    time_taken = data.get('time_taken')
    
    if not participant_id:
        return {'success': False, 'error': 'Not authenticated as a participant'}
    
    participant = LiveQuizParticipant.query.get(participant_id)
    if not participant:
        return {'success': False, 'error': 'Participant not found'}
    
    # Check if answer already submitted for this question
    existing_answer = LiveQuizAnswer.query.filter_by(
        participant_id=participant_id,
        question_id=question_id
    ).first()
    
    if existing_answer:
        return {'success': False, 'error': 'Answer already submitted'}
    
    # Create answer record
    from models.quizModel import Option
    option = Option.query.get(option_id)
    
    is_correct = option.is_correct if option else False
    
    # Calculate points - more points for faster answers
    max_points = 1000
    min_points = 500
    time_factor = 1.0
    
    if time_taken:
        # Adjust time factor based on how quickly they answered
        # Faster answers get more points
        time_factor = max(0.5, 1.0 - (time_taken / 30))
    
    points = int(max_points * time_factor) if is_correct else 0
    
    answer = LiveQuizAnswer(
        participant_id=participant_id,
        question_id=question_id,
        option_id=option_id,
        is_correct=is_correct,
        time_taken=time_taken,
        points_earned=points
    )
    
    db.session.add(answer)
    
    # Update participant score if answer is correct
    if is_correct:
        participant.current_score += points
        
        # Notify the host about the score update
        room = LiveQuizRoom.query.get(participant.room_id)
        emit('update_score', {
            'participant_id': participant_id,
            'display_name': participant.display_name,
            'score': participant.current_score
        }, room=room.room_code)
    
    db.session.commit()
    
    return {
        'success': True,
        'is_correct': is_correct,
        'points_earned': points
    }