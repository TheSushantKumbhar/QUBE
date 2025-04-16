from flask import Blueprint, request, jsonify, render_template
import google.generativeai as genai
import os
from config import configure_genai
from createQuiz.routes import login_required
from utils.auth_helpers import get_current_user
from extensions import db
from models.quizModel import Question,Quiz,Option
import json

AI = Blueprint("ai", __name__)
genai = configure_genai()
model = genai.GenerativeModel("gemini-1.5-pro-001") 

def format_prompt(topic, num_questions=5):
   
    return f"""
    Generate a quiz on the topic "{topic}" with {num_questions} questions.

    Each question should:
    - Have a clear and concise question text.
    - Include 4 options.
    - Have only one correct answer.
    - Be returned in this exact JSON format:
    [
        {{
            "question": "Question text here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": ["Correct option(s) exactly as in options"]
        }},
        ...
    ]

    IMPORTANT: Return ONLY valid JSON that can be parsed directly.
    """

def parse_quiz_response(response_text):
    """
    Parse the JSON response from the Gemini API
    """
    try:
        quiz_data = response_text.strip()
        return json.loads(quiz_data)  
    except Exception as e:
        return {"error": f"Failed to parse response: {str(e)}"}


@AI.route("/generate-ai-quiz", methods=["POST"])
def generate_ai_quiz():
    try:
        data = request.get_json()
        topic = data.get("topic", "")
        num_questions = data.get("num_questions", 5)

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        prompt = format_prompt(topic, num_questions)
        
        response = model.generate_content(prompt)
        quiz_data = parse_quiz_response(response.text)

        if "error" in quiz_data:
            return jsonify(quiz_data), 500
        
        return jsonify({"quiz": quiz_data})
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@AI.route("/create-quiz", methods=["GET"])
def create_quiz_page():
    return render_template("AIQuiz/promptPage.html")


@AI.route("/save-ai-quiz", methods=["POST"])
@login_required
def save_ai_quiz():
    current_user = get_current_user()
    try:
        data = request.get_json()
        title = data.get("title")
        subject = data.get("subject", "")
        questions = data.get("questions", [])

        if not title or not questions:
            return jsonify({"error": "Title and questions are required"}), 400

        # Create Quiz entry
        quiz = Quiz(
            title=title,
            subject=subject,
            user_id=current_user.id
        )
        db.session.add(quiz)
        db.session.flush() 

        for idx, q in enumerate(questions):
            question = Question(
                quiz_id=quiz.id,
                text=q["question"],
                question_type="single",
                position=idx
            )
            db.session.add(question)
            db.session.flush()

            for i, option_text in enumerate(q["options"]):
                is_correct = option_text in q["answer"]
                option = Option(
                    question_id=question.id,
                    text=option_text,
                    is_correct=is_correct,
                    position=i
                )
                db.session.add(option)

        db.session.commit()
        return jsonify({"message": "Quiz saved successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500