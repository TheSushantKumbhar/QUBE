from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
import pyrebase
from config import firebase_Config, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from models.models import User
from extensions import db
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader
    
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

        # Check if email already exists in PostgreSQL
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in instead.", "danger")
            return redirect(url_for('auth.login'))

        try:
            # Firebase authentication first - only add to Postgres if this succeeds
            firebase_user = auth.create_user_with_email_and_password(email, password)
            
            # Upload profile picture to Cloudinary
            profile_pic_url = None
            if profile_pic:
                upload_result = cloudinary.uploader.upload(profile_pic, folder="profile_pics")
                profile_pic_url = upload_result["secure_url"]  # Get the uploaded image URL

            # Save user in PostgreSQL ONLY AFTER Firebase authentication succeeds
            new_user = User(email=email, username=username, profile_pic=profile_pic_url)
            db.session.add(new_user)
            db.session.commit()

            session['profile_pic'] = profile_pic_url

            flash("Account created! You can now log in.", "success")
            return redirect(url_for('auth.login'))

        except Exception as e:
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                flash("This email is already in use. Please log in instead.", "danger")
                return redirect(url_for('auth.login'))
            flash(f"Error: {error_message}", "danger")

    return render_template('authentication/signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Firebase authentication
            firebase_user = auth.sign_in_with_email_and_password(email, password)

            # Check if user exists in PostgreSQL
            db_user = User.query.filter_by(email=email).first()

            if not db_user:
                # Automatically create the user in PostgreSQL if missing
                db_user = User(email=email, username=None, profile_pic=None)
                db.session.add(db_user)
                db.session.commit()

            # Set session variables
            session['user'] = db_user.email
            session['username'] = db_user.username if db_user.username else "User"

            # If profile pic is stored in Cloudinary, use the direct URL
            session['profile_pic'] = db_user.profile_pic if db_user.profile_pic else "/static/profile_pics/default.jpg"

            flash("Login successful!", "success")
            return redirect(url_for('home'))

        except Exception as e:
            flash("Invalid email or password. Please try again.", "danger")
            print(f"Login error: {str(e)}")  # Log error for debugging

    return render_template('authentication/login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('username', None)
    session.pop('profile_pic', None)
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
            flash('Error sending password reset email. Please check if the email is registered.', 'danger')

    return render_template('authentication/resetPassword.html')


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
            session['username'] = username

        # Handle profile picture upload to Cloudinary
        if profile_pic and profile_pic.filename != '':
            try:
                # Upload new profile picture to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    profile_pic,
                    folder="profile_pics",
                    overwrite=True,
                    invalidate=True
                )
                
                # Get the new Cloudinary image URL
                new_profile_pic_url = upload_result['secure_url']
                
                # Store new Cloudinary URL in database
                user.profile_pic = new_profile_pic_url
                session['profile_pic'] = new_profile_pic_url  # Update session
                
            except Exception as e:
                flash(f"Error uploading image: {str(e)}", "danger")
                print(f"Cloudinary upload error: {str(e)}")

        db.session.commit()
        flash("Profile updated successfully!", "success")

        # Force a refresh to see the new image by redirecting
        return redirect(url_for('auth.update_profile'))

    return render_template('authentication/profile.html', user=user)