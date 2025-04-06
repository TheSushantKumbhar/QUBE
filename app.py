from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, session
from auth.routes import auth_bp
from createQuiz.routes import quiz_bp
from extensions import db, migrate
from config import SQLALCHEMY_DATABASE_URI
from models.db_init import create_database
from models.models import User   

from apscheduler.schedulers.background import BackgroundScheduler 

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SECRET_KEY"] = "your_secret_key_here"       

db.init_app(app)
migrate.init_app(app, db) 


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(quiz_bp, url_prefix='/quiz')
from liveQuiz.routes import live
app.register_blueprint(live, url_prefix="/live")



create_database(app)

@app.route('/')
def home():
    return render_template('Homepage/index.html',username=session.get('user'))

def keep_db_alive():
    try:
        with app.app_context():
            db.session.execute("SELECT 1")
            db.session.commit()
            print("DB keep-alive successful")
    except Exception as e:
        db.session.rollback()
        print(f"DB keep-alive failed: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(func=keep_db_alive, trigger="interval", minutes=4)
scheduler.start()


if __name__ == '__main__':
    app.run(debug=True)

