from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import pyrebase
from config import firebase_Config  

auth_bp = Blueprint('auth', __name__)

firebase = pyrebase.initialize_app(firebase_Config)
auth = firebase.auth()

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match. Try again.', 'danger')
            return redirect(url_for('auth.signup'))  

        try:
            auth.create_user_with_email_and_password(email, password)
            flash('Account created! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('home')) 
        
        except Exception as e:
            flash(f'Invalid credentials. Error: {str(e)}', 'danger')

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
