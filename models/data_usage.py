# # models/usage_log.py

# from datetime import datetime
# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()  # Placeholder (real one is in app.py)


# class UsageLog(db.Model):
#     __tablename__ = 'usage_logs'

#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.String(50), db.ForeignKey('students.id'), nullable=False)
#     used_mb = db.Column(db.Integer, nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return f"<UsageLog {self.student_id} used {self.used_mb}MB>"
