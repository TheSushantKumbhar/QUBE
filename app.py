from flask import Flask, render_template,request, redirect,url_for,session,flash
import pyrebase


app = Flask(__name__)
app.secret_key = "secret_key"

firebase_Config = {
  "apiKey": "AIzaSyDS2sOsrDSVps2erWnDRoDUwQZiMwvdP8M",
  "authDomain": "cube-88533.firebaseapp.com",
  "databaseURL" : "https://cube-88533-default-rtdb.firebaseio.com/",
  "projectId" : "cube-88533",
  "storageBucket": "cube-88533.firebasestorage.app",
  "messagingSenderId": "763418038891",
  "appId": "1:763418038891:web:3130cbed23ff118e67572e",
  "measurementId": "G-Y3NDYPSJ74"
  
};

firebase = pyrebase.initialize_app(firebase_Config)
auth = firebase.auth()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup',methods = ['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password: 
            flash('Passwords do not match. Try again.', 'danger')
            return redirect(url_for('signup'))

        try:
            user = auth.create_user_with_email_and_password(email,password)
            flash('Account created you can now log in !!!')
            return redirect(url_for('login'))
        except Exception as e: 
            flash('Error : ' +str(e),'danger')

    return render_template('signup.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try: 
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            flash('login successful')
            return redirect(url_for('dashboard'))
        
        except Exception as e : 
            error_msg = str(e)
            flash('Invalid credentials try again ERROR : ' +error_msg,'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('please login first!!!','warning')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html',username= session['user'])

@app.route('/logout')
def logout():
    session.pop('user',None)
    flash('logged out successfully','info')
    return redirect(url_for('login'))

@app.route('/resetPassword', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']

        try:
            auth.send_password_reset_email(email)
            flash('Password reset email sent! Check your inbox.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error: ' + str(e), 'danger')

    return render_template('resetPassword.html')



if __name__ == '__main__':
    app.run(debug=True)

