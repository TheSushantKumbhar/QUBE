from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, session, redirect, url_for, flash
from auth.routes import auth_bp
from extensions import db, migrate
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import SQLALCHEMY_DATABASE_URI
from models.models import User


app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"
app.register_blueprint(auth_bp, url_prefix='/auth')

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

db.init_app(app)
migrate.init_app(app, db) 
from models.models import User
if not SQLALCHEMY_DATABASE_URI:
    raise RuntimeError("DATABASE_URL is not set in .env or not being loaded.")

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html',username=session.get('user'))


if __name__ == '__main__':
    app.run(debug=True)

