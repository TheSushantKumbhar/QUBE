from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from models.quizModel import Quiz, Question, Option,QuizAttempt,UserAnswer
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
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

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
    


# Add these routes to your existing createquiz/routes.py file

@quiz_bp.route('/view/<int:quiz_id>')
@login_required
def view_quiz(quiz_id):
    """View a quiz with management options"""
    quiz = Quiz.query.get_or_404(quiz_id)
    user = get_current_user()
    
    # Check if user has access to this quiz
    if quiz.user_id != user.id and not quiz.is_public:
        flash("You don't have permission to view this quiz.", "danger")
        return redirect(url_for('quiz.my_quizzes'))
    
    return render_template('CreateQuiz/viewQuiz.html', quiz=quiz, current_user=user)


@quiz_bp.route('/update_settings/<int:quiz_id>', methods=['POST'])
@login_required
def update_quiz_settings(quiz_id):
    """Update quiz settings (public/private, scheduled times)"""
    quiz = Quiz.query.get_or_404(quiz_id)
    user = get_current_user()
    
    # Check if user owns this quiz
    if quiz.user_id != user.id:
        return jsonify({'success': False, 'message': 'You do not have permission to modify this quiz'}), 403
    
    try:
        # Update quiz settings
        quiz.is_public = 'is_public' in request.form
        quiz.is_live = 'is_live' in request.form
        quiz.always_available = request.form.get('always_available') == 'true'
        
        # If not always available, update the time restrictions
        if not quiz.always_available:
            start_time_str = request.form.get('start_time')
            end_time_str = request.form.get('end_time')
            
            if start_time_str and end_time_str:
                # Convert time strings to datetime objects
                from datetime import datetime, time
                
                # Parse the time strings (format: HH:MM)
                hours, minutes = map(int, start_time_str.split(':'))
                start_time = time(hour=hours, minute=minutes)
                
                hours, minutes = map(int, end_time_str.split(':'))
                end_time = time(hour=hours, minute=minutes)
                
                quiz.start_time = start_time
                quiz.end_time = end_time
            else:
                return jsonify({'success': False, 'message': 'Start and end times are required'}), 400
        else:
            # Reset time restrictions if always available
            quiz.start_time = None
            quiz.end_time = None
        
        db.session.commit()
        return jsonify({'success': True}), 200
        
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@quiz_bp.route('/edit/<int:quiz_id>')
@login_required
def edit_quiz(quiz_id):
    """Edit an existing quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    user = get_current_user()
    
    # Check if user owns this quiz
    if quiz.user_id != user.id:
        flash("You don't have permission to edit this quiz.", "danger")
        return redirect(url_for('quiz.my_quizzes'))
    
    # Fetch quiz data to pre-populate the form
    questions = []
    for question in sorted(quiz.questions, key=lambda q: q.position):
        options = []
        for option in sorted(question.options, key=lambda o: o.position):
            options.append({
                'id': option.id,
                'text': option.text,
                'image_url': option.image_url,
                'isCorrect': option.is_correct
            })
        
        questions.append({
            'id': question.id,
            'text': question.text,
            'image_url': question.image_url,
            'type': question.question_type,
            'options': options
        })
    
    quiz_data = {
        'id': quiz.id,
        'title': quiz.title,
        'subject': quiz.subject,
        'questions': questions
    }
    
    return render_template('CreateQuiz/editQuiz.html', quiz=quiz, quiz_data=json.dumps(quiz_data))


@quiz_bp.route('/delete/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    """Delete a quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    user = get_current_user()
    
    # Check if user owns this quiz
    if quiz.user_id != user.id:
        flash("You don't have permission to delete this quiz.", "danger")
        return redirect(url_for('quiz.my_quizzes'))
    
    try:
        db.session.delete(quiz)
        db.session.commit()
        flash("Quiz deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        flash(f"Error deleting quiz: {str(e)}", "danger")
    
    return redirect(url_for('quiz.my_quizzes'))


# Add these to your quiz_bp Blueprint in createquiz/routes.py
@quiz_bp.route('/explore')
def explore_quizzes():
    """
    Explore page that shows all public quizzes
    Any user can view this page, even if not logged in
    """
    # Get all public quizzes that are live
    public_quizzes = Quiz.query.filter(
        Quiz.is_public == True,
        Quiz.is_live == True
    ).order_by(Quiz.created_at.desc()).all()
    
    # Get current user if logged in
    current_user = get_current_user()
    
    # Get current time for checking availability
    from datetime import datetime
    current_time = (datetime.utcnow() + timedelta(hours=5, minutes=30)).time()
    
    return render_template('explore.html', 
                          quizzes=public_quizzes,
                          current_user=current_user,
                          current_time=current_time)

@quiz_bp.route('/explore/details/<int:quiz_id>')
def explore_quiz_details(quiz_id):
    """View details of a public quiz from the explore page"""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if quiz is public
    if not quiz.is_public:
        flash("This quiz is not available for public viewing.", "danger")
        return redirect(url_for('quiz.explore_quizzes'))
    
    # Get quiz creator info
    creator = User.query.get(quiz.user_id)
    
    # Get current user if logged in
    current_user = get_current_user()
    
    # Check if there's a current quiz attempt by this user
    user_attempt = None
    if current_user:
        user_attempt = QuizAttempt.query.filter_by(
            quiz_id=quiz.id,
            user_id=current_user.id,
            completed_at=None
        ).first()
    
    return render_template('exploreQuizDetails.html', quiz=quiz,creator=creator, current_user=current_user,user_attempt=user_attempt)


@quiz_bp.route('/explore/start/<int:quiz_id>', methods=['POST'])
@login_required
def start_explore_quiz(quiz_id):
    """Start attempting a public quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    user = get_current_user()
    
    # Check if quiz is public and live
    if not quiz.is_public or not quiz.is_live:
        flash("This quiz is not available for public attempts.", "danger")
        return redirect(url_for('quiz.explore_quizzes'))
    
    # Check if quiz is available at the current time
    if not quiz.always_available:
        from datetime import datetime
        current_time = (datetime.utcnow() + timedelta(hours=5, minutes=30)).time()
        
        # Check if current time is within quiz availability window
        if not (quiz.start_time <= current_time <= quiz.end_time):
            flash("This quiz is not available at this time.", "warning")
            return redirect(url_for('quiz.explore_quiz_details', quiz_id=quiz.id))
    
    # Check if there's an existing incomplete attempt
    existing_attempt = QuizAttempt.query.filter_by(
        quiz_id=quiz.id,
        user_id=user.id,
        completed_at=None
    ).first()
    
    if existing_attempt:
        # Resume existing attempt
        return redirect(url_for('quiz.take_quiz', attempt_id=existing_attempt.id))
    
    # Create new attempt
    new_attempt = QuizAttempt(
        quiz_id=quiz.id,
        user_id=user.id
    )
    db.session.add(new_attempt)
    
    try:
        db.session.commit()
        return redirect(url_for('quiz.take_quiz', attempt_id=new_attempt.id))
    except Exception as e:
        db.session.rollback()
        flash(f"Error starting quiz: {str(e)}", "danger")
        return redirect(url_for('quiz.explore_quiz_details', quiz_id=quiz.id))
    
@quiz_bp.route('/quiz/take/<int:attempt_id>')
@login_required
def take_quiz(attempt_id):
    """Take a quiz based on an attempt ID"""
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    user = get_current_user()
    
    # Check if this attempt belongs to the current user
    if attempt.user_id != user.id:
        flash("You don't have permission to access this quiz attempt.", "danger")
        return redirect(url_for('quiz.explore_quizzes'))
    
    # Check if attempt is already completed
    if attempt.completed_at:
        flash("This quiz attempt has already been completed.", "info")
        return redirect(url_for('quiz.explore_quiz_details', quiz_id=attempt.quiz_id))
    
    # Get the quiz
    quiz = attempt.quiz
    
    # Check if quiz is still available (time restrictions)
    if not quiz.always_available:
        from datetime import datetime
        current_time = (datetime.utcnow() + timedelta(hours=5, minutes=30)).time()
        
        # Check if current time is within quiz availability window
        if not (quiz.start_time <= current_time <= quiz.end_time):
            flash("This quiz is not available at this time.", "warning")
            return redirect(url_for('quiz.explore_quiz_details', quiz_id=quiz.id))
    
    # Get current time for template
    from datetime import datetime
    current_time = (datetime.utcnow() + timedelta(hours=5, minutes=30)).time()
    
    return render_template('solveQuiz/takeQuiz.html', 
                          quiz=quiz, 
                          attempt=attempt,
                          current_time=current_time)

@quiz_bp.route('/quiz/submit/<int:attempt_id>', methods=['POST'])
@login_required
def submit_quiz(attempt_id):
    try:
        print(f"Received submission for attempt {attempt_id}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Request data: {request.get_json()}")

        if not request.is_json:
            return jsonify({'success': False, 'message': 'Invalid request. JSON payload required.'}), 400

        data = request.get_json()
        answers = data.get('answers', {})
        # completion_time = data.get('completionTime')

        if not answers or not isinstance(answers, dict):
            return jsonify({'success': False, 'message': 'Invalid or missing answers.'}), 400

        attempt = QuizAttempt.query.get_or_404(attempt_id)
        user = get_current_user()

        if attempt.user_id != user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        if attempt.completed_at:
            return jsonify({'success': False, 'message': 'This attempt has already been completed'}), 400

        # Clear previous answers
        UserAnswer.query.filter_by(attempt_id=attempt.id).delete()
        db.session.flush()  # Ensure deletion is processed before adding new answers

        total_questions = 0
        correct_answers = 0
        incorrect_answers = 0

        for question_id, option_ids in answers.items():
            try:
                question_id = int(question_id)
                question = Question.query.get(question_id)
                if not question or question.quiz_id != attempt.quiz_id:
                    print(f"Invalid question ID {question_id} for quiz {attempt.quiz_id}")
                    continue

                total_questions += 1
                correct_options = {o.id for o in question.options if o.is_correct}
                user_option_ids = set(int(o_id) for o_id in option_ids if str(o_id).isdigit())

                # Determine correctness
                if question.question_type == 'single':
                    is_correct = len(user_option_ids) == 1 and user_option_ids.issubset(correct_options)
                else:
                    is_correct = user_option_ids == correct_options

                if is_correct:
                    correct_answers += 1
                else:
                    incorrect_answers += 1

                # Save user answers
                for option_id in user_option_ids:
                    option = Option.query.get(option_id)
                    if option and option.question_id == question_id:  # Validate option exists and belongs to question
                        user_answer = UserAnswer(
                            attempt_id=attempt.id,
                            question_id=question.id,
                            option_id=option_id
                        )
                        db.session.add(user_answer)
                    else:
                        print(f"Invalid option ID {option_id} for question {question_id}")

            except ValueError as ve:
                print(f"ValueError processing question {question_id}: {ve}")
                continue

        # Update attempt details
        now = datetime.utcnow()  # Use UTC and handle timezone in app config if needed
        score_percentage = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        attempt.score = score_percentage
        attempt.completed_at = now

        # Commit all changes
        db.session.commit()
        print(f"Successfully saved attempt {attempt_id} with score {score_percentage}%")

        return jsonify({
            'success': True,
            'score': score_percentage,
            'correctAnswers': correct_answers,
            'totalQuestions': total_questions,
            'incorrectAnswers': incorrect_answers,
            'redirectUrl': url_for('quiz.quiz_results', attempt_id=attempt.id)
        }), 200

    except SQLAlchemyError as db_error:
        db.session.rollback()
        print(f"Database error: {str(db_error)}")
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        db.session.rollback()
        print(f"Unexpected error: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'An unexpected error occurred: {str(e)}'}), 500

@quiz_bp.route('/quiz/results/<int:attempt_id>')
@login_required
def quiz_results(attempt_id):
    """Display quiz results for a specific attempt"""
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    user = get_current_user()
    
    # Check if this attempt belongs to the current user
    if attempt.user_id != user.id:
        flash("You don't have permission to view these results.", "danger")
        return redirect(url_for('quiz.explore_quizzes'))
    
    # Check if attempt is completed
    if not attempt.completed_at:
        flash("This quiz attempt is not yet completed.", "warning")
        return redirect(url_for('quiz.explore_quizzes'))
    
    # Get detailed results
    questions = []
    for question in attempt.quiz.questions:
        user_answers = UserAnswer.query.filter_by(
            attempt_id=attempt.id, 
            question_id=question.id
        ).all()
        
        user_answer_ids = {ua.option_id for ua in user_answers}
        correct_option_ids = {o.id for o in question.options if o.is_correct}
        
        is_correct = user_answer_ids == correct_option_ids
        
        question_details = {
            'text': question.text,
            'image_url': question.image_url,
            'type': question.question_type,
            'user_answers': [
                {
                    'text': option.text, 
                    'image_url': option.image_url,
                    'is_correct': option.is_correct
                } for option in question.options if option.id in user_answer_ids
            ],
            'correct_answers': [
                {
                    'text': option.text, 
                    'image_url': option.image_url
                } for option in question.options if option.is_correct
            ],
            'is_correct': is_correct
        }
        
        questions.append(question_details)
    
    return render_template(
        'solveQuiz/results.html', 
        attempt=attempt, 
        quiz=attempt.quiz, 
        questions=questions
    )