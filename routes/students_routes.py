from flask import Blueprint, request, jsonify
from models.student_db import Student, db


# Create a Blueprint for organizing student-related routes
student_bp = Blueprint('student_bp', __name__)

# ----------------------------
# CREATE - Add a new student
# Endpoint: POST /students
# ----------------------------
@student_bp.route('/students', methods=['POST'])
def add_student():
    try:
        # Get JSON data from the request body
        data = request.get_json()

        # Required fields for a student record
        required = ['student_id', 'first_name', 'last_name', 'password']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if student with same ID already exists
        if Student.query.filter_by(student_id=data['student_id']).first():
            return jsonify({'error': 'Student already exists'}), 409

        # Create a new student object
        new_student = Student(
            student_id=data['student_id'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )

        # Set hashed password using helper method
        new_student.set_password(data['password'])

        # Add to session and commit to database
        db.session.add(new_student)
        db.session.commit()

        return jsonify({'message': 'Student added successfully'}), 201

    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ----------------------------
# READ - Get all students
# Endpoint: GET /students
# ----------------------------
@student_bp.route('/students', methods=['GET'])
def get_students():
    # Fetch all student records
    students = Student.query.all()

    # Return list of students as JSON
    return jsonify([
        {
            'id': s.id,
            'student_id': s.student_id,
            'first_name': s.first_name,
            'last_name': s.last_name,
            'created_at': s.created_at
        } for s in students
    ]), 200

# ----------------------------
# READ - Get one student by database ID
# Endpoint: GET /students/<int:student_id>
# ----------------------------
@student_bp.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    # Find student by primary key ID
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Return student info as JSON
    return jsonify({
        'id': student.id,
        'student_id': student.student_id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'created_at': student.created_at
    }), 200

# ----------------------------
# UPDATE - Update student info
# Endpoint: PUT /students/<int:student_id>
# ----------------------------
@student_bp.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    # Get the student by ID
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Get update data from request body
    data = request.get_json()

    # Update the fields if provided
    student.first_name = data.get('first_name', student.first_name)
    student.last_name = data.get('last_name', student.last_name)

    # If password is provided, update and hash it
    if 'password' in data:
        student.set_password(data['password'])

    # Commit changes to the database
    db.session.commit()
    return jsonify({'message': 'Student updated successfully'}), 200

# ----------------------------
# DELETE - Delete a student
# Endpoint: DELETE /students/<int:student_id>
# ----------------------------
@student_bp.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    # Get the student by ID
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Delete the student from the database
    db.session.delete(student)
    db.session.commit()

    return jsonify({'message': 'Student deleted successfully'}), 200
