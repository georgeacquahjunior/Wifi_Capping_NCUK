import os
from datetime import timedelta

# Configuration for Flask app and database
class Config:
    # Secret key for JWT encoding/decoding
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_change_in_production'
    # SQLite database URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///students.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_EXPIRATION_DELTA = timedelta(hours=1)  # Token expires in 1 hour