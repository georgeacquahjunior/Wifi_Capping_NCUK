# backend/config.py

# class Config:
#     SQLALCHEMY_DATABASE_URI = "postgresql://postgres:brainstorm@localhost:5432/wifi_capping"
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     SECRET_KEY = "your-secret-key"

import os

class Config:
    # Get DATABASE_URL from environment (Render sets this), fallback to hosted DB
    uri = os.getenv(
        "DATABASE_URL", 
        "postgresql://wifi_capping_mff3_user:zuuglnMg2vnO5a7rMjfPQL73C6tjgzaV@dpg-d2c8g4vdiees73fd9rv0-a.oregon-postgres.render.com/wifi_capping_mff3"
    )

    # Fix for old-style URLs (postgres:// instead of postgresql://)
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

