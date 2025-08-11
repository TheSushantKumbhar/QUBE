from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, session

from extensions import db, migrate
from config import SQLALCHEMY_DATABASE_URI
from models.db_init import create_database
from models.models import User   
from liveQuiz.websockets import socketio  
from config import configure_genai

from apscheduler.schedulers.background import BackgroundScheduler 

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
socketio.init_app(app) 


app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SECRET_KEY"] = "your_secret_key_here"       
# app.config["GEMINI_API_KEY"] = GEMINI_API_KEY

from sqlalchemy.pool import NullPool

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "poolclass": NullPool
}
 
db.init_app(app)
migrate.init_app(app, db) 

from auth.routes import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from createQuiz.routes import quiz_bp
app.register_blueprint(quiz_bp, url_prefix='/quiz')

from liveQuiz.routes import live
app.register_blueprint(live, url_prefix="/live")

from AIQuiz.routes import AI
app.register_blueprint(AI,url_prefix="/AI")

from Analytics.routes import analytics
app.register_blueprint(analytics,url_prefix="/analytics")

from homepage.routes import main_bp
app.register_blueprint(main_bp)

# configure_genai()
create_database(app)

# @app.route('/')
# def home():
#     return render_template('Homepage/index.html',username=session.get('username'),profile_pic=session.get('profile_pic'))

@app.context_processor
def inject_current_user():
    from utils.auth_helpers import get_current_user
    return dict(current_user=get_current_user())


# def keep_db_alive():
#     with app.app_context():
#         try:
#             db.session.execute('SELECT 1')  # Lightweight dummy query
#             db.session.commit()
#             print("DB keep-alive successful.")
#         except Exception as e:
#             db.session.rollback()
#             print("DB keep-alive error:", str(e))

# # ---- SCHEDULER SETUP ----
# def start_scheduler():
#     scheduler = BackgroundScheduler(daemon=True)
#     scheduler.add_job(func=keep_db_alive, trigger="interval", minutes=4)
#     scheduler.start()
#     return scheduler

# scheduler = start_scheduler()

# # Shut down the scheduler when exiting the app
# import atexit
# atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    socketio.run(app, debug=True)

