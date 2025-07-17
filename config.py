# backend/config.py

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:brainstorm@localhost:5432/wifi_capping"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your-secret-key"
