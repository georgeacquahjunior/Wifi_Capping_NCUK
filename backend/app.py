# Simple Flask app with JWT authentication

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import bcrypt
import jwt
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_change_in_production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)
db = SQLAlchemy(app)

# JWT settings
JWT_EXPIRATION_DELTA = timedelta(hours=1)

# Token blacklist (in production, use Redis or database)
blacklisted_tokens = set()

# Define Student model
class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Student {self.id}>"

def generate_token(student_id):
    """Generate JWT token with expiration"""
    payload = {
        'student_id': student_id,
        'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify JWT token and check if it's blacklisted"""
    if token in blacklisted_tokens:
        return None
    
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    student_id = data.get('student_id')
    password = data.get('password')

    if not student_id or not password:
        return jsonify({'error': 'Student ID and password required'}), 400

    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    if bcrypt.checkpw(password.encode('utf-8'), student.password.encode('utf-8')):
        token = generate_token(student_id)
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'student_id': student_id,
            'expires_in': JWT_EXPIRATION_DELTA.total_seconds()
        }), 200
    else:
        return jsonify({'error': 'Incorrect password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout by blacklisting the token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    blacklisted_tokens.add(token)
    
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/verify', methods=['GET'])
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create a test user if it doesn't exist
        test_user = db.session.get(Student, 'admin')
        if not test_user:
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            test_student = Student(
                id='admin',
                name='Admin User',
                password=hashed_password.decode('utf-8')
            )
            db.session.add(test_student)
            db.session.commit()
            print("Test admin user created: admin/admin123")
    
    app.run(debug=True, port=5000)