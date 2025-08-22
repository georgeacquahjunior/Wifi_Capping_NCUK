# backend/create_db.py

from app import app
from models.student_db import db, Student
from models.merged_usage_log_db import db, MergedUsageLogs
from models.admin_db import db, Admin

with app.app_context():
    db.create_all()



    print("Database and tables created.")
