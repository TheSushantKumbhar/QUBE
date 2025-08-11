from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
import google.generativeai as genai

load_dotenv()

firebase_Config = {
    "apiKey": os.getenv('FIREBASE_API_KEY'),
    "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
    "databaseURL": os.getenv('FIREBASE_DATABASE_URL'),      
    "projectId": os.getenv('FIREBASE_PROJECT_ID'),
    "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
    "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
    "appId": os.getenv('FIREBASE_APP_ID'),
    "measurementId": os.getenv('FIREBASE_MEASUREMENT_ID')
}


SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
if not SQLALCHEMY_DATABASE_URI:
    raise ValueError("SQLALCHEMY_DATABASE_URI is not set. Check your .env file.")

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "").split(',')) if os.getenv("ALLOWED_EXTENSIONS") else set()
SECRET_KEY = os.getenv("SECRET_KEY")
SQLALCHEMY_TRACK_MODIFICATIONS = False

db = SQLAlchemy()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def configure_genai():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return genai