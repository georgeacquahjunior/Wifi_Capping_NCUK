# Handles login

from flask import Blueprint, request, jsonify
import bcrypt
from models.student import Student

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    student_id = data.get('student_id')
    password = data.get('password')

    if not student_id or not password:
        return jsonify({'error': 'Student ID and password required'}), 400

    # Use SQLAlchemy model to query the student
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    if bcrypt.checkpw(password.encode('utf-8'), student.password.encode('utf-8')):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Incorrect password'}), 401
