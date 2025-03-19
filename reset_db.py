import sys
from extensions import db
from app import app  # Import Flask app

def reset_database():
    """Drops and recreates all database tables after user confirmation."""
    confirmation = input(" Are you sure you want to reset the database? (yes/no): ").strip().lower()
    
    if confirmation != "yes":
        print("Database reset aborted.")
        sys.exit(0)

    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✅ Database reset successfully!")

if __name__ == "__main__":
    reset_database()
