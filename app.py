from flask import Flask, render_template, session, redirect, url_for, flash
from auth.routes import auth_bp  

app = Flask(__name__)
app.secret_key = "secret_key"

app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def home():
    return render_template('index.html',username=session.get('user'))


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))

    return render_template('dashboard.html', username=session['user'])

if __name__ == '__main__':
    app.run(debug=True)
