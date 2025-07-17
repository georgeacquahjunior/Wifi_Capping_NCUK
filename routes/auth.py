# routes/auth.py

from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models.student import Student

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth', methods=['POST'])
def login():
    data = request.get_json()
    student_id = data.get('student_id')
    name = data.get('name')
    password = data.get('password')

    # Validate inputs
    if not student_id or not name or not password:
        return jsonify({"error": "student_id, name, and password are required"}), 400

    # Lookup student
    student = Student.query.get(student_id)

    # Validate login
    if student and student.name == name and check_password_hash(student.password, password):
        return jsonify({"message": "Login successful"}), 200

    return jsonify({"error": "Incorrect student ID, name, or password"}), 401
