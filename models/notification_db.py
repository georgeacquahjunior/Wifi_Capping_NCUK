from .notification_db import db

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)