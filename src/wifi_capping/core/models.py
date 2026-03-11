"""
Database models for the WiFi capping system.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='user')
    user_group = Column(String(50), nullable=False, default='students')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    
    def set_password(self, password):
        """Set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check user password."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'user_group': self.user_group,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }


class NetworkSession(db.Model):
    """Network session tracking."""
    __tablename__ = 'network_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    device_mac = Column(String(17), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime)
    bytes_downloaded = Column(Integer, default=0)
    bytes_uploaded = Column(Integer, default=0)
    session_active = Column(Boolean, default=True)
    
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))
    
    def to_dict(self):
        """Convert session to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_mac': self.device_mac,
            'ip_address': self.ip_address,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'bytes_downloaded': self.bytes_downloaded,
            'bytes_uploaded': self.bytes_uploaded,
            'session_active': self.session_active
        }


class PolicyConfig(db.Model):
    """Policy configuration storage."""
    __tablename__ = 'policy_configs'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    policy_type = Column(String(50), nullable=False)
    configuration = Column(Text, nullable=False)  # JSON configuration
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert policy to dictionary."""
        return {
            'id': self.id,
            'policy_id': self.policy_id,
            'name': self.name,
            'policy_type': self.policy_type,
            'enabled': self.enabled,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AUPViolationRecord(db.Model):
    """AUP violation storage."""
    __tablename__ = 'aup_violations'
    
    id = Column(Integer, primary_key=True)
    violation_id = Column(String(100), unique=True, nullable=False)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    device_mac = Column(String(17), nullable=False)
    violation_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text)  # JSON evidence
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text)
    penalty_applied = Column(String(200))
    
    user = db.relationship('User', backref=db.backref('violations', lazy=True))
    
    def to_dict(self):
        """Convert violation to dictionary."""
        return {
            'id': self.id,
            'violation_id': self.violation_id,
            'user_id': self.user_id,
            'device_mac': self.device_mac,
            'violation_type': self.violation_type,
            'severity': self.severity,
            'description': self.description,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'resolved': self.resolved,
            'resolution_notes': self.resolution_notes,
            'penalty_applied': self.penalty_applied
        }


class SecurityEvent(db.Model):
    """Security event logging."""
    __tablename__ = 'security_events'
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    user_id = Column(Integer, db.ForeignKey('users.id'))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    description = Column(Text, nullable=False)
    additional_data = Column(Text)  # JSON additional data
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship('User', backref=db.backref('security_events', lazy=True))
    
    def to_dict(self):
        """Convert security event to dictionary."""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'severity': self.severity,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'description': self.description,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class SystemMetrics(db.Model):
    """System performance and usage metrics."""
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50))
    category = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert metric to dictionary."""
        return {
            'id': self.id,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'metric_unit': self.metric_unit,
            'category': self.category,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }