from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
import pyrebase
from config import firebase_Config,UPLOAD_FOLDER,ALLOWED_EXTENSIONS
from models.models import User
from extensions import db
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

auth_bp = Blueprint('auth', __name__)
firebase = pyrebase.initialize_app(firebase_Config)
auth = firebase.auth()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form.get('username')
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        profile_pic = request.files.get('profile_pic')

        if password != confirm_password:
            flash("Passwords do not match. Try again.", "danger")
            return redirect(url_for('auth.signup'))

        try:
            # Firebase authentication
            auth.create_user_with_email_and_password(email, password)
            
            # Handle profile picture upload
            profile_pic_filename = None
            if profile_pic and allowed_file(profile_pic.filename):
                filename = secure_filename(profile_pic.filename)
                profile_pic_filename = os.path.join(UPLOAD_FOLDER, filename)
                profile_pic.save(profile_pic_filename)

            # Save user in PostgreSQL
            new_user = User(email=email, username=username, profile_pic=profile_pic_filename)
            db.session.add(new_user)
            db.session.commit()

            flash("Account created! You can now log in.", "success")
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Firebase authentication
            user = auth.sign_in_with_email_and_password(email, password)
            
            # Fetch user from PostgreSQL
            db_user = User.query.filter_by(email=email).first()
            if not db_user:
                flash("User not found in the database!", "danger")
                return redirect(url_for('auth.signup'))

            session['user'] = db_user.email
            session['username'] = db_user.username
            session['profile_pic'] = db_user.profile_pic or '/static/default-profile.png'

            flash("Login successful!", "success")
            return redirect(url_for('home'))

        except Exception as e:
            flash(f"Invalid credentials. Error: {str(e)}", "danger")

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('home'))


@auth_bp.route('/resetPassword', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            auth.send_password_reset_email(email)
            flash('Password reset email sent! Check your inbox.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    return render_template('resetPassword.html')


@auth_bp.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user' not in session:
        flash("You need to log in first!", "danger")
        return redirect(url_for('auth.login'))

    email = session['user']
    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form.get('username')
        profile_pic = request.files.get('profile_pic')

        # Update username if provided
        if username:
            user.username = username

        # Handle profile picture upload
        if profile_pic and allowed_file(profile_pic.filename):
            filename = secure_filename(profile_pic.filename)
            profile_pic_path = os.path.join(UPLOAD_FOLDER, filename)

            # **Delete the old profile picture if it exists**
            if user.profile_pic and os.path.exists(os.path.join("static", user.profile_pic)):
                os.remove(os.path.join("static", user.profile_pic))

            profile_pic.save(profile_pic_path)

            # Store relative path for profile picture
            user.profile_pic = f'profile_pics/{filename}'

        db.session.commit()
        flash("Profile updated successfully!", "success")

        # **Update session profile_pic so it appears in navbar immediately**
        session['profile_pic'] = user.profile_pic

        return redirect(url_for('auth.update_profile'))

    return render_template('profile.html', user=user)

