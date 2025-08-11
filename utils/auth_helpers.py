from flask import session
from models.models import User  

def get_current_user():
    """Returns the current logged-in user object based on Firebase email in session."""
    user_email = session.get('user')
    if user_email:
        return User.query.filter_by(email=user_email).first()
    return None
