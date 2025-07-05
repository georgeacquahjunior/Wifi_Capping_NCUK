# Handles logging + checking usage

from flask import Blueprint, request, jsonify
from models.data_usage import UsageLog
from app import db

usage_bp = Blueprint('usage', __name__)

@usage_bp.route('/log_usage', methods=['POST'])
def log_usage():
    data = request.get_json()
    student_id = data.get('student_id')
    used_mb = data.get('used_mb')

    if not student_id or not used_mb:
        return jsonify({'error': 'student_id and used_mb required'}), 400

    log = UsageLog(student_id=student_id, used_mb=used_mb)
    db.session.add(log)
    db.session.commit()

    return jsonify({'message': 'Usage logged successfully'}), 201
