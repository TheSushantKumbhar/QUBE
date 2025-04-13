from flask import Blueprint, render_template, current_app, g
from sqlalchemy import func, desc, case
from datetime import datetime, timedelta
from models.quizModel import Quiz, Question, Option, QuizAttempt, UserAnswer
from models.models import User
from extensions import db



analytics = Blueprint('analytics', __name__)

@analytics.route('/')
def analytics_dashboard():
    # Get current user
    current_user_id = g.user.id if hasattr(g, 'user') else None
    
    # Calculate summary statistics
    total_quizzes = db.session.query(func.count(Quiz.id)).scalar()
    total_attempts = db.session.query(func.count(QuizAttempt.id)).scalar()
    public_quizzes = db.session.query(func.count(Quiz.id)).filter(Quiz.is_public == True).scalar()
    
    # Calculate average score
    avg_score_query = db.session.query(func.avg(QuizAttempt.score)).filter(QuizAttempt.completed_at != None)
    avg_score = round(avg_score_query.scalar() or 0)
    
    # Get top performing quizzes (by average score and completion rate)
    # Fixed case() syntax: pass conditions as positional arguments, not a list
    top_quizzes_data = db.session.query(
        Quiz.id,
        Quiz.title,
        Quiz.subject,
        func.count(QuizAttempt.id).label('attempts'),
        func.avg(QuizAttempt.score).label('avg_score'),
        (func.sum(case((QuizAttempt.completed_at != None, 1), else_=0)) * 100 / 
         func.count(QuizAttempt.id)).label('completion_rate')
    ).join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id)\
     .group_by(Quiz.id)\
     .having(func.count(QuizAttempt.id) > 0)\
     .order_by(desc('avg_score'))\
     .limit(5)\
     .all()
    
    top_quizzes = [{
        'title': quiz.title,
        'subject': quiz.subject or 'General',
        'attempts': quiz.attempts,
        'avg_score': round(quiz.avg_score or 0),
        'completion_rate': round(quiz.completion_rate or 0)
    } for quiz in top_quizzes_data]
    
    # Get recent activity
    recent_attempts = db.session.query(
        QuizAttempt.id,
        QuizAttempt.started_at,
        QuizAttempt.completed_at,
        QuizAttempt.score,
        Quiz.title.label('quiz_title'),
        User.username
    ).join(Quiz, QuizAttempt.quiz_id == Quiz.id)\
     .join(User, QuizAttempt.user_id == User.id)\
     .order_by(desc(QuizAttempt.started_at))\
     .limit(10)\
     .all()
    
    recent_activity = [{
        'username': attempt.username,
        'quiz_title': attempt.quiz_title,
        'date': attempt.started_at.strftime('%b %d, %Y at %H:%M'),
        'completed': attempt.completed_at is not None,
        'score': round(attempt.score) if attempt.score is not None else None
    } for attempt in recent_attempts]
    
    # Get top performing users
    top_users_data = db.session.query(
        User.id,
        User.username,
        User.profile_pic.label('profile_pic'),
        func.count(QuizAttempt.id).label('quizzes_taken'),
        func.avg(QuizAttempt.score).label('avg_score')
    ).join(QuizAttempt, User.id == QuizAttempt.user_id)\
     .filter(QuizAttempt.completed_at != None)\
     .group_by(User.id)\
     .order_by(desc('avg_score'))\
     .limit(5)\
     .all()
    
    top_users = [{
        'username': user.username,
        'profile_pic': user.profile_pic,
        'quizzes_taken': user.quizzes_taken,
        'avg_score': round(user.avg_score or 0)
    } for user in top_users_data]
    
    # Generate data for completion rate over time chart (last 7 days)
    today = datetime.utcnow().date()
    dates = [(today - timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
    
    completion_rates = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        next_date = today - timedelta(days=i-1) if i > 0 else today + timedelta(days=1)
        
        # Count total attempts for the day
        total = db.session.query(func.count(QuizAttempt.id))\
                .filter(QuizAttempt.started_at >= date, 
                        QuizAttempt.started_at < next_date)\
                .scalar() or 0
        
        # Count completed attempts
        completed = db.session.query(func.count(QuizAttempt.id))\
                   .filter(QuizAttempt.started_at >= date,
                           QuizAttempt.started_at < next_date,
                           QuizAttempt.completed_at != None)\
                   .scalar() or 0
        
        # Calculate completion rate
        rate = round((completed / total) * 100) if total > 0 else 0
        completion_rates.append(rate)
    
    completion_data = {
        'labels': dates,
        'values': completion_rates
    }
    
    # Generate score distribution data
    score_ranges = ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%']
    score_distribution_counts = [
        db.session.query(func.count(QuizAttempt.id))\
        .filter(QuizAttempt.score >= low, QuizAttempt.score <= high)\
        .scalar() or 0
        for low, high in [(0, 20), (21, 40), (41, 60), (61, 80), (81, 100)]
    ]
    
    score_distribution = {
        'labels': score_ranges,
        'values': score_distribution_counts
    }
    
    return render_template('Analytics/analytics.html',
                          total_quizzes=total_quizzes,
                          total_attempts=total_attempts,
                          public_quizzes=public_quizzes,
                          avg_score=avg_score,
                          top_quizzes=top_quizzes,
                          recent_activity=recent_activity,
                          top_users=top_users,
                          completion_data=completion_data,
                          score_distribution=score_distribution)