# Handles login with JWT token generation and logout

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import bcrypt
import jwt
from models.student import Student
from config import Config

auth_bp = Blueprint('auth', __name__)

# Token blacklist (in production, use Redis or database)
blacklisted_tokens = set()

def generate_token(student_id):
    """Generate JWT token with expiration"""
    payload = {
        'student_id': student_id,
        'exp': datetime.utcnow() + Config.JWT_EXPIRATION_DELTA,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token and check if it's blacklisted"""
    if token in blacklisted_tokens:
        return None
    
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

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
        token = generate_token(student_id)
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'student_id': student_id,
            'expires_in': Config.JWT_EXPIRATION_DELTA.total_seconds()
        }), 200
    else:
        return jsonify({'error': 'Incorrect password'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout by blacklisting the token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    blacklisted_tokens.add(token)
    
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/verify', methods=['GET'])
def verify():
    """Verify if current token is valid"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if payload:
        return jsonify({
            'valid': True,
            'student_id': payload['student_id'],
            'expires_at': payload['exp']
        }), 200
    else:
        return jsonify({'valid': False, 'error': 'Token invalid or expired'}), 401