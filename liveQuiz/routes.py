from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session as flask_session
live_quiz = Blueprint('live_quiz', __name__)