# backend/routes/auth.py

from flask import Blueprint, request, jsonify
from models.student import Student, db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    student_id = data.get('student_id')
    password = data.get('password')

    student = Student.query.filter_by(student_id=student_id).first()

    if student and student.check_password(password):
        return jsonify({"message": "Login successful", "student_id": student_id}), 200
    else:
        return jsonify({"message": "Invalid ID or password"}), 401
