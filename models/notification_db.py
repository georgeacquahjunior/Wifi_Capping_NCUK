from .notification_db import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = "notifications"

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(50), db.ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="unread")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)