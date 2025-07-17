# # Handles logging + checking usage

# from flask import Blueprint, request, jsonify
# from models.data_usage import UsageLog

# usage_bp = Blueprint('usage', __name__)

# @usage_bp.route('/log_usage', methods=['POST'])
# def log_usage():
#     data = request.get_json()
#     student_id = data.get('student_id')
#     used_mb = data.get('used_mb')

    
# @usage_bp.route('/get_usage', methods=['GET'])
# def get_usage_logs():
#     logs = UsageLog.query.all()
#     result = []

#     for log in logs:
#         result.append({
#             "id": log.id,
#             "student_id": log.student_id,
#             "used_mb": log.used_mb,
#             "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
#         })

#     return jsonify(result), 200

