from flask import Blueprint, render_template, current_app, g,session
from sqlalchemy import func, desc, case, or_
from datetime import datetime, timedelta
from models.quizModel import Quiz, Question, Option, QuizAttempt, UserAnswer
from models.models import User
from extensions import db

analytics = Blueprint('analytics', __name__)

@analytics.route('/')
def analytics_dashboard():
    current_user_id = g.user.id if hasattr(g, 'user') else None

    total_quizzes = db.session.query(func.count(Quiz.id)).scalar() or 0
    total_attempts = db.session.query(func.count(QuizAttempt.id)).scalar() or 0
    public_quizzes = db.session.query(func.count(Quiz.id)).filter(Quiz.is_public == True).scalar() or 0
    
    # Handle potential NULL values for avg_score
    avg_score_query = db.session.query(func.avg(QuizAttempt.score))\
                      .filter(QuizAttempt.completed_at != None)
    avg_score = round(avg_score_query.scalar() or 0)

    # Top quizzes - Modified to ensure we get results
    try:
        # try to get quizzes with attempts (original query)
        top_quizzes_data = db.session.query(
            Quiz.id,
            Quiz.title,
            Quiz.subject,
            func.count(QuizAttempt.id).label('attempts'),
            func.avg(QuizAttempt.score).label('avg_score'),
            (func.sum(case((QuizAttempt.completed_at != None, 1), else_=0)) * 100 / 
             func.greatest(func.count(QuizAttempt.id), 1)).label('completion_rate')  
        ).join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id)\
         .group_by(Quiz.id)\
         .order_by(desc('avg_score'))\
         .limit(5)\
         .all()

        # If we got no results, fall back to showing most recent quizzes
        if not top_quizzes_data:
            raise Exception("No quizzes with attempts found")
            
    except Exception as e:
        top_quizzes_data = db.session.query(
            Quiz
        ).order_by(desc(Quiz.id)).limit(5).all()
        
        # Format the data manually
        top_quizzes = []
        for quiz in top_quizzes_data:
            top_quizzes.append({
                'title': quiz.title,
                'subject': quiz.subject or 'General',
                'attempts': 0,
                'avg_score': 0,
                'completion_rate': 0
            })
    else:
        # Process results from the original query
        top_quizzes = [{
            'title': quiz.title,
            'subject': quiz.subject or 'General',
            'attempts': quiz.attempts,
            'avg_score': round(quiz.avg_score or 0),
            'completion_rate': round(quiz.completion_rate or 0)
        } for quiz in top_quizzes_data]

    # Recent activity
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

    # Top users
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

    # --- User Performance Over Time ---
    user_performance_dates = []
    user_scores = []
    avg_scores = []

    if current_user_id:
        # Get user's completed quiz attempts in chronological order
        user_attempts = db.session.query(
            QuizAttempt.completed_at,
            QuizAttempt.score,
            QuizAttempt.quiz_id
        ).filter(QuizAttempt.user_id == current_user_id,
                 QuizAttempt.completed_at != None)\
         .order_by(QuizAttempt.completed_at)\
         .limit(7).all()

        for attempt in user_attempts:
            user_performance_dates.append(attempt.completed_at.strftime('%b %d'))
            user_scores.append(round(attempt.score or 0))
            
            avg_quiz_score = db.session.query(func.avg(QuizAttempt.score))\
                .filter(QuizAttempt.quiz_id == attempt.quiz_id,
                        QuizAttempt.completed_at != None)\
                .scalar() or 0
            avg_scores.append(round(avg_quiz_score))

    # Provide placeholder data if no attempts found
    if not user_performance_dates:
        user_performance_dates = ["No Data"]
        user_scores = [0]
        avg_scores = [0]

    user_performance_data = {
        'labels': user_performance_dates,
        'user_scores': user_scores,
        'avg_scores': avg_scores
    }

    # --- Subject Performance Breakdown ---
    subject_labels = []
    subject_scores = []

    if current_user_id:
        # Get user's average score by subject
        subject_performance = db.session.query(
            Quiz.subject,
            func.avg(QuizAttempt.score).label('avg_score')
        ).join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id)\
         .filter(QuizAttempt.user_id == current_user_id,
                 QuizAttempt.completed_at != None)\
         .group_by(Quiz.subject).all()

        for subject in subject_performance:
            subject_name = subject.subject or 'General'
            subject_labels.append(subject_name)
            subject_scores.append(round(subject.avg_score or 0))

    # Provide placeholder data if no subjects found
    if not subject_labels:
        subject_labels = ["No Data"]
        subject_scores = [0]

    subject_performance_data = {
        'labels': subject_labels,
        'scores': subject_scores
    }

    return render_template('Analytics/analytics.html',
                           total_quizzes=total_quizzes,
                           total_attempts=total_attempts,
                           public_quizzes=public_quizzes,
                           avg_score=avg_score,
                           top_quizzes=top_quizzes,
                           recent_activity=recent_activity,
                           top_users=top_users,
                           user_performance_data=user_performance_data,
                           subject_performance_data=subject_performance_data,username=session.get('username'),profile_pic=session.get('profile_pic'))