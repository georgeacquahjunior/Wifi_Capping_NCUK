# models/student.py

from app import db

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Student {self.id}>"
