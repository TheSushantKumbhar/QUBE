from flask import Blueprint, request, jsonify , render_template
from models.quizModel import db, Quiz, Question

quiz_bp = Blueprint('createQuiz', __name__)


@quiz_bp.route('/create_quiz', methods=['GET'])
def create_quiz_page():
    return render_template('createQuiz.html')

@quiz_bp.route('/create_quiz', methods=['POST'])
def create_quiz():
    data = request.json
    
    new_quiz = Quiz(title=data['title'], description=data['description'])
    db.session.add(new_quiz)
    db.session.commit()
    
    for q in data['questions']:
        new_question = Question(
            quiz_id=new_quiz.id,
            question_text=q['question_text'],
            option1=q['options'][0],
            option2=q['options'][1],
            option3=q['options'][2],
            option4=q['options'][3],
            correct_answer=q['correct_answer']
        )
        db.session.add(new_question)
    
    db.session.commit()
    return jsonify({"message": "Quiz created successfully!"})
