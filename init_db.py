# init_db.py

from app import create_app, db
from models.student import Student
from models.data_usage import UsageLog  
import bcrypt

app = create_app()
with app.app_context():
    db.create_all()

    # Add sample student (only if not exists)
    if not Student.query.get("stu001"):
        hashed = bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode('utf-8')
        student = Student(id="stu001", name="George", password=hashed)
        db.session.add(student)
        db.session.commit()

    print("Database initialized with student and usage_logs table.")
