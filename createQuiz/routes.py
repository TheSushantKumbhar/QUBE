from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from models.quizModel import Quiz, Question, Option
from models.models import User
from extensions import db
import os
import uuid
import traceback
from werkzeug.utils import secure_filename
import json
import cloudinary
import cloudinary.uploader
import cloudinary.api
import base64

# Create blueprint
quiz_bp = Blueprint('quiz', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def upload_to_cloudinary(file_data):
    """Upload image to Cloudinary and return the URL"""
    if not file_data:
        return None
        
    try:
        # Handle base64 encoded images
        if isinstance(file_data, str) and file_data.startswith('data:image'):
            # Generate a unique filename
            filename = f"quiz_image_{uuid.uuid4()}"
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file_data,
                public_id=filename,
                folder="quiz_images"
            )
            
            # Return the secure URL
            return result['secure_url']
            
        # Handle file objects (if you're receiving actual file uploads)
        elif hasattr(file_data, 'filename'):
            filename = f"quiz_image_{uuid.uuid4()}"
            
            result = cloudinary.uploader.upload(
                file_data,
                public_id=filename,
                folder="quiz_images"
            )
            
            return result['secure_url']
            
    except Exception as e:
        print(f"Cloudinary upload error: {str(e)}")
        traceback.print_exc()
        
    return None

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


@quiz_bp.route('/quizCategories',methods=['GET','POST'])
@login_required
def quiz_categories():
    return render_template('CreateQuiz/quizCategories.html')


@quiz_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_quiz_page():
    """Render the create quiz page"""
    if request.method == 'POST':
        # Handle form submission
        try:
            user = get_current_user()
            data = request.json
            
            new_quiz = Quiz(
                title=data['title'],
                subject=data.get('subject', ''),
                user_id=user.id,  # Use the SQLAlchemy user id
                is_public=False,
                is_live=False
            )
            db.session.add(new_quiz)
            db.session.flush()
            
            for q_index, question_data in enumerate(data['questions']):
                question_image_url = upload_to_cloudinary(question_data.get('image'))
                new_question = Question(
                    quiz_id=new_quiz.id,
                    text=question_data['text'],
                    image_url=question_image_url,
                    question_type=question_data['type'],
                    position=q_index + 1
                )
                db.session.add(new_question)
                db.session.flush()
                
                for o_index, option_data in enumerate(question_data['options']):
                    option_image_url = upload_to_cloudinary(option_data.get('image'))
                    new_option = Option(
                        question_id=new_question.id,
                        text=option_data['text'],
                        image_url=option_image_url,
                        is_correct=option_data['isCorrect'],
                        position=o_index + 1
                    )
                    db.session.add(new_option)
            
            db.session.commit()
            flash("Quiz created successfully!", "success")
            return redirect(url_for('quiz.view_quiz', quiz_id=new_quiz.id))
            
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f"Error creating quiz: {str(e)}", "danger")
    
    return render_template('CreateQuiz/createQuiz.html')

@quiz_bp.route('/api/quizzes', methods=['POST'])
@login_required
def create_quiz_api():
    """API endpoint to create a new quiz"""
    try:
        user = get_current_user()
        data = request.json
        
        new_quiz = Quiz(
            title=data['title'],
            subject=data.get('subject', ''),
            user_id=user.id,  # Use the SQLAlchemy user id
            is_public=False,
            is_live=False
        )
        db.session.add(new_quiz)
        db.session.flush()
        
        for q_index, question_data in enumerate(data['questions']):
            question_image_url = upload_to_cloudinary(question_data.get('image'))
            new_question = Question(
                quiz_id=new_quiz.id,
                text=question_data['text'],
                image_url=question_image_url,
                question_type=question_data['type'],
                position=q_index + 1
            )
            db.session.add(new_question)
            db.session.flush()
            
            for o_index, option_data in enumerate(question_data['options']):
                option_image_url = upload_to_cloudinary(option_data.get('image'))
                new_option = Option(
                    question_id=new_question.id,
                    text=option_data['text'],
                    image_url=option_image_url,
                    is_correct=option_data['isCorrect'],
                    position=o_index + 1
                )
                db.session.add(new_option)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Quiz created successfully', 'quiz_id': new_quiz.id}), 201
        
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Failed to create quiz: {str(e)}'}), 500

@quiz_bp.route('/api/quizzes/<int:quiz_id>', methods=['GET'])
@login_required
def get_quiz(quiz_id):
    """Get quiz data by ID"""
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'success': False, 'message': 'Quiz not found'}), 404
        
        user = get_current_user()
        if not quiz.is_public and quiz.user_id != user.id:
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        quiz_data = {
            'id': quiz.id,
            'title': quiz.title,
            'subject': quiz.subject,
            'created_at': quiz.created_at.isoformat(),
            'is_public': quiz.is_public,
            'is_live': quiz.is_live,
            'questions': []
        }
        
        questions = sorted(quiz.questions, key=lambda q: q.position)
        for question in questions:
            options = sorted(question.options, key=lambda o: o.position)
            quiz_data['questions'].append({
                'id': question.id,
                'text': question.text,
                'image_url': question.image_url,
                'type': question.question_type,
                'options': [{'id': option.id, 'text': option.text, 'image_url': option.image_url, 'is_correct': option.is_correct} for option in options]
            })
            
        return jsonify({'success': True, 'quiz': quiz_data}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error retrieving quiz: {str(e)}'}), 500


@quiz_bp.route('/view/<int:quiz_id>')
@login_required
def view_quiz(quiz_id):
    """View a quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    user = get_current_user()
    
    # Check if user has access to this quiz
    if not quiz.is_public and quiz.user_id != user.id:
        flash("You don't have permission to view this quiz.", "danger")
        return redirect(url_for('home'))
    
    return render_template('CreateQuiz/viewQuiz.html', quiz=quiz)


@quiz_bp.route('/myquizzes')
@login_required
def my_quizzes():
    """View user's quizzes"""
    user = get_current_user()
    quizzes = Quiz.query.filter_by(user_id=user.id).all()
    return render_template('createQuiz/myQuizzes.html', quizzes=quizzes)


@quiz_bp.route('/preview')
@login_required
def preview_quiz():
    """Preview the quiz before creating it"""
    return render_template('CreateQuiz/previewQuiz.html')
    

@quiz_bp.route('/save_quiz', methods=['POST'])
@login_required
def save_quiz():
    """Save the quiz to the database"""
    try:
        user = get_current_user()
        data = request.form.get('quiz_data')

        if not data:
            flash("No quiz data received!", "danger")
            return redirect(url_for('quiz.create_quiz_page'))

        data = json.loads(data)

        new_quiz = Quiz(
            title=data['title'],
            subject=data.get('subject', ''),
            user_id=user.id,
            is_public=False,
            is_live=False
        )
        db.session.add(new_quiz)
        db.session.flush()

        for q_index, question_data in enumerate(data['questions']):
            question_image_url = upload_to_cloudinary(question_data.get('image'))
            new_question = Question(
                quiz_id=new_quiz.id,
                text=question_data['text'],
                image_url=question_image_url,
                question_type=question_data['type'],
                position=q_index + 1
            )
            db.session.add(new_question)
            db.session.flush()

            for o_index, option_data in enumerate(question_data['options']):
                option_image_url = upload_to_cloudinary(option_data.get('image'))
                new_option = Option(
                    question_id=new_question.id,
                    text=option_data['text'],
                    image_url=option_image_url,
                    is_correct=option_data['isCorrect'],
                    position=o_index + 1
                )
                db.session.add(new_option)

        db.session.commit()
        flash("Quiz saved successfully!", "success")
        return redirect(url_for('quiz.my_quizzes'))

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        flash(f"Error saving quiz: {str(e)}", "danger")
        return redirect(url_for('quiz.create_quiz_page'))