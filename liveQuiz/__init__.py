from flask import Blueprint

live_quiz = Blueprint('live_quiz', __name__)

from . import routes