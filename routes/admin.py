# routes/admin.py

from flask import Blueprint, jsonify
from models.data_usage import UsageLog
from models.student import Student
from app import db
from sqlalchemy import extract
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# 1. View total monthly usage for a specific student
@admin_bp.route('/admin/usage/<student_id>', methods=['GET'])
def get_student_usage(student_id):
    now = datetime.utcnow()
    month = now.month
    year = now.year

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    total_usage = db.session.query(
        db.func.sum(UsageLog.used_mb)
    ).filter(
        UsageLog.student_id == student_id,
        extract('month', UsageLog.timestamp) == month,
        extract('year', UsageLog.timestamp) == year
    ).scalar() or 0

    return jsonify({
        "student_id": student_id,
        "name": student.name,
        "monthly_usage_mb": total_usage,
        "capped": total_usage >= 20480
    })

# 2. Reset a student's usage logs for the current month
@admin_bp.route('/admin/reset/<student_id>', methods=['POST'])
def reset_student_usage(student_id):
    now = datetime.utcnow()
    month = now.month
    year = now.year

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Delete usage logs for the current month
    db.session.query(UsageLog).filter(
        UsageLog.student_id == student_id,
        extract('month', UsageLog.timestamp) == month,
        extract('year', UsageLog.timestamp) == year
    ).delete()
    db.session.commit()

    return jsonify({
        "message": f"Usage logs for {student_id} reset successfully."
    }), 200
