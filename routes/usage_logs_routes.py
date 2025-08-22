from flask import Blueprint, jsonify
from models.merged_usage_log_db import db,MergedUsageLogs  # assumes you have this helper
from models.student_db import Student

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route("/usage_logs/dashboard", methods=["GET"])
def admin_dashboard():
    # Join Students and Usage using SQLAlchemy
    results = (
        db.session.query(
            Student.student_id,
            Student.first_name,
            Student.last_name,
            MergedUsageLogs.date_allocated,
            MergedUsageLogs.data_allocated,
            MergedUsageLogs.data_used,
            MergedUsageLogs.data_left,
            MergedUsageLogs.percentage_used,
            MergedUsageLogs.capped_status
        )
        .join(MergedUsageLogs, Student.student_id == MergedUsageLogs.student_id)
        .order_by(Student.student_id)
        .all()
    )

    students_data = []
    for row in results:
        students_data.append({
            "student_id": row.student_id,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "date_allocated": str(row.date_allocated),
            "data_allocated": float(row.data_allocated),
            "data_used": float(row.data_used),
            "data_left": float(row.data_left),
            "percentage_used": float(row.percentage_used),
            "capped_status": row.capped_status
        })

    return jsonify({"students": students_data})