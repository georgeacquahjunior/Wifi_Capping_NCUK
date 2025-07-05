import os
# Configuration for Flask app and database
class Config:
    # Secret key for JWT encoding/decoding
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    # SQLite database URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///students.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False