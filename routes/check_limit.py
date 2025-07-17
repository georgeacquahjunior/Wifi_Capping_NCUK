# from flask import Blueprint, request, jsonify
# from models.data_usage import UsageLog
# from app import db
# from datetime import datetime
# from sqlalchemy import extract

# check_limit_bp = Blueprint('check_limit', __name__)
# @check_limit_bp.route('/check_limit', methods=['GET'])
# def check_limit():
#     student_id = request.args.get('student_id')
#     if not student_id:
#         return jsonify({'error': 'student_id is required'}), 400

#     # Get current month and year
#     now = datetime.utcnow()
#     current_month = now.month
#     current_year = now.year

#     # Query usage for the student in the current month
#     total_usage = db.session.query(
#         db.func.sum(UsageLog.used_mb)
#     ).filter(
#         UsageLog.student_id == student_id,
#         extract('month', UsageLog.timestamp) == current_month,
#         extract('year', UsageLog.timestamp) == current_year
#     ).scalar() or 0

#     is_capped = total_usage >= 20480

#     return jsonify({
#         "student_id": student_id,
#         "used_mb": total_usage,
#         "limit_reached": is_capped
#     }), 200
