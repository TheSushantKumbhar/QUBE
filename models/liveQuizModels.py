from extensions import db
from datetime import datetime

class LiveQuizRoom(db.Model):
    __tablename__ = "live_quiz_rooms"

    id = db.Column(db.Integer,primary_key=True)   
    room_code = db.Column(db.String(8), unique = True,nullable = False)
    quiz_id = db.Column(db.Integer,db.ForeignKey("quizzes.id",ondelete = "CASCADE"),nullable = False)
    host_id = db.Column(db.Integer,db.ForeignKey("users.id",ondelete="CASCADE"),nullable = False)
    created_at = db.Column(db.DateTime,default = datetime.utcnow)
    is_active = db.Column(db.Boolean,default = True)
    question_time = db.Column(db.Integer,default = 30)
    current_question_index = db.Column(db.Integer,default = -1)

    quiz = db.relationship("Quiz", backref=db.backref("live_rooms", cascade="all, delete-orphan"))
    host = db.relationship("User", backref=db.backref("hosted_rooms", cascade="all, delete-orphan"))
    participants = db.relationship("LiveQuizParticipant", backref="room", cascade="all, delete-orphan")

class LiveQuizParticipant(db.Model):
    __tablename__ = "live_quiz_participants"
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("live_quiz_rooms.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    display_name = db.Column(db.String(50), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    current_score = db.Column(db.Integer, default=0)
    
    user = db.relationship("User", backref=db.backref("participations", cascade="all, delete-orphan"))
    answers = db.relationship("LiveQuizAnswer", backref="participant", cascade="all, delete-orphan")


class LiveQuizAnswer(db.Model):
    __tablename__ = "live_quiz_answers"
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("live_quiz_participants.id", ondelete="CASCADE"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey("options.id", ondelete="CASCADE"), nullable=False)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_correct = db.Column(db.Boolean, default=False)
    time_taken = db.Column(db.Float)  # Time taken to answer in seconds
    points_earned = db.Column(db.Integer, default=0)
    
    # question = db.relationship("Question")
    # option = db.relationship("Option")
    question = db.relationship("Question", backref=db.backref("live_answers", cascade="all, delete-orphan"))
    option = db.relationship("Option", backref=db.backref("live_answers", cascade="all, delete-orphan"))