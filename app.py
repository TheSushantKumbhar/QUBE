from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, session
from auth.routes import auth_bp
from createQuiz.routes import quiz_bp
from extensions import db, migrate
from config import SQLALCHEMY_DATABASE_URI
from models.db_init import create_database


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SECRET_KEY"] = "your_secret_key_here"

db.init_app(app)
migrate.init_app(app, db) 


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(quiz_bp) 

create_database(app)

@app.route('/')
def home():
    return render_template('index.html',username=session.get('user'))

if __name__ == '__main__':
    app.run(debug=True)

