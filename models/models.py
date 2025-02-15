from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<User {self.email}>"
