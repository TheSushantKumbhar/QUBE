from flask import Blueprint,render_template,url_for,session
from createQuiz.routes import login_required
from utils.auth_helpers import get_current_user
from extensions import db
from models.quizModel import Question,QuizAttempt,Quiz
from sqlalchemy import func, desc, case, or_

main_bp = Blueprint('main',__name__)
@main_bp.route('/')
@login_required
def index():
    # Get the current user
    current_user = get_current_user()
    user_id = current_user.id
    username = current_user.username
    
    # Fetch recent activities for the user
    recent_activities = get_user_recent_activities(user_id)
    
    return render_template('homepage/index.html', 
                          username=username,
                          recent_activities=recent_activities,profile_pic=session.get('profile_pic'))

def get_user_recent_activities(user_id, limit=3):
    """Fetch recent user activities including quiz completions and created quizzes"""
    
    # Get recent quiz attempts by the user
    recent_attempts = db.session.query(
        QuizAttempt.id,
        QuizAttempt.started_at,
        QuizAttempt.completed_at,
        QuizAttempt.score,
        Quiz.title.label('quiz_title'),
        Quiz.id.label('quiz_id')
    ).join(Quiz, QuizAttempt.quiz_id == Quiz.id)\
     .filter(QuizAttempt.user_id == user_id)\
     .filter(QuizAttempt.completed_at != None)\
     .order_by(db.desc(QuizAttempt.completed_at))\
     .limit(limit)\
     .all()
    
    # Get recently created quizzes by the user
    recent_creations = db.session.query(
        Quiz.id,
        Quiz.title,
        Quiz.created_at
    ).filter(Quiz.user_id == user_id)\
     .order_by(db.desc(Quiz.created_at))\
     .limit(limit)\
     .all()
    
    activities = []
    
    # Add completed quiz activities
    for attempt in recent_attempts:
        activities.append({
            'type': 'completed',
            'message': f"You completed '{attempt.quiz_title}' with a score of {attempt.score}%",
            'timestamp': attempt.completed_at.strftime('%b %d, %Y at %H:%M'),
            'raw_timestamp': attempt.completed_at,
            'url': url_for('quiz.quiz_results', attempt_id=attempt.id) 
            # Ensure this route exists or adjust accordingly
        })
    
    # Add created quiz activities
    for quiz in recent_creations:
        activities.append({
            'type': 'created',
            'message': f"You created a new quiz '{quiz.title}'",
            'timestamp': quiz.created_at.strftime('%b %d, %Y at %H:%M'),
            'raw_timestamp': quiz.created_at,
            'url': url_for('quiz.view_quiz', quiz_id=quiz.id)
            # Ensure this route exists or adjust accordingly
        })
    
    # Optional: Add recent improvements in scores (comparing attempts)
    # This requires more complex logic to find improved scores on the same quiz
    
    # Sort all activities by timestamp, newest first
    activities.sort(key=lambda x: x['raw_timestamp'], reverse=True)
    
    # Return limited number of activities
    return activities[:limit]