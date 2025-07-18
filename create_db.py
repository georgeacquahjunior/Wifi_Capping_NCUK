# backend/create_db.py

from app import app
from models.student_db import db, Student

with app.app_context():
    db.create_all()

    if not Student.query.filter_by(student_id="student001").first():
        student = Student(student_id="student001", name="George Acquah")
        student.set_password("test122")
        db.session.add(student)
        db.session.commit()

    print("Database and tables created.")
