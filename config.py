# backend/config.py

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:brainstorm@localhost:5432/wifi_capping"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your-secret-key"

# import os

# class Config:
#     # Use DATABASE_URL from environment (Render), fallback to local DB if not set
#     SQLALCHEMY_DATABASE_URI = os.getenv(
#         "DATABASE_URL", 
#         "postgresql://wifi_capping_mff3_user:zuuglnMg2vnO5a7rMjfPQL73C6tjgzaV@dpg-d2c8g4vdiees73fd9rv0-a.oregon-postgres.render.com/wifi_capping_mff3"
#     )
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

