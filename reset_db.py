from extensions import db
from app import app # Import your Flask app and database instance

with app.app_context():
    db.drop_all()  # Drop all tables
    db.create_all()  # Recreate all tables
    print("Database reset successfully!")
