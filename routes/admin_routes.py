from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models.admin_db import Admin, db
from datetime import datetime

admin_bp = Blueprint('admin_bp', __name__)

# ---------------- CREATE ----------------
@admin_bp.route('/admins', methods=['POST'])
def create_admin():
    """Create a new admin account"""
    data = request.get_json()
    admin_id = data.get('admin_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    password = data.get('password')

    if not admin_id or not first_name or not last_name or not password:
        return jsonify({'error': 'All fields are required'}), 400

    password_hash = generate_password_hash(password)

    new_admin = Admin(
        admin_id=admin_id,
        first_name=first_name,
        last_name=last_name,
        password_hash=password_hash,
        created_at=datetime.utcnow()
    )
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({'message': 'Admin created successfully'}), 201

# ---------------- READ ALL ----------------
@admin_bp.route('/admins', methods=['GET'])
def get_all_admins():
    """Get all admins"""
    admins = Admin.query.all()
    result = [{
        'id': admin.id,
        'admin_id': admin.admin_id,
        'first_name': admin.first_name,
        'last_name': admin.last_name,
        'created_at': admin.created_at
    } for admin in admins]

    return jsonify(result), 200

# ---------------- READ ONE ----------------
@admin_bp.route('/admins/<int:id>', methods=['GET'])
def get_admin(id):
    """Get one admin by ID"""
    admin = Admin.query.get(id)
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404

    return jsonify({
        'id': admin.id,
        'admin_id': admin.admin_id,
        'first_name': admin.first_name,
        'last_name': admin.last_name,
        'created_at': admin.created_at
    }), 200

# ---------------- UPDATE ----------------
@admin_bp.route('/admins/<int:id>', methods=['PUT'])
def update_admin(id):
    """Update an admin account"""
    admin = Admin.query.get(id)
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404

    data = request.get_json()
    admin.admin_id = data.get('admin_id', admin.admin_id)
    admin.first_name = data.get('first_name', admin.first_name)
    admin.last_name = data.get('last_name', admin.last_name)
    password = data.get('password')

    if password:
        admin.password_hash = generate_password_hash(password)

    db.session.commit()

    return jsonify({'message': 'Admin updated successfully'}), 200

# ---------------- DELETE ----------------
@admin_bp.route('/admins/<int:id>', methods=['DELETE'])
def delete_admin(id):
    """Delete an admin"""
    admin = Admin.query.get(id)
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404

    db.session.delete(admin)
    db.session.commit()

    return jsonify({'message': 'Admin deleted successfully'}), 200
