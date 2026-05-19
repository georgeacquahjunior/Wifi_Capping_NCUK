"""
Authentication blueprint for secure user management.
"""

import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from ..core.models import User, SecurityEvent, db
from ..security import SecurityValidator

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Secure user authentication with rate limiting."""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # Rate limiting check
    recent_attempts = SecurityEvent.query.filter(
        SecurityEvent.event_type == 'login_attempt',
        SecurityEvent.ip_address == ip_address,
        SecurityEvent.timestamp > datetime.utcnow() - timedelta(minutes=15)
    ).count()
    
    if recent_attempts > 5:
        log_security_event('rate_limit_exceeded', 'HIGH', None, ip_address, user_agent,
                          f"Rate limit exceeded: {recent_attempts} attempts")
        return jsonify({'error': 'Too many login attempts. Please try again later.'}), 429
    
    # Find user
    user = User.query.filter_by(username=username).first()
    
    # Log login attempt
    log_security_event('login_attempt', 'INFO', user.id if user else None, ip_address, user_agent,
                      f"Login attempt for username: {username}")
    
    if not user or not user.check_password(password):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                log_security_event('account_locked', 'HIGH', user.id, ip_address, user_agent,
                                  f"Account locked due to failed attempts: {username}")
            db.session.commit()
        
        log_security_event('login_failed', 'MEDIUM', user.id if user else None, ip_address, user_agent,
                          f"Failed login for username: {username}")
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        log_security_event('locked_account_attempt', 'HIGH', user.id, ip_address, user_agent,
                          f"Attempt to access locked account: {username}")
        return jsonify({'error': 'Account is temporarily locked'}), 423
    
    # Check if account is active
    if not user.is_active:
        log_security_event('inactive_account_attempt', 'MEDIUM', user.id, ip_address, user_agent,
                          f"Attempt to access inactive account: {username}")
        return jsonify({'error': 'Account is disabled'}), 403
    
    # Successful login
    login_user(user)
    user.last_login = datetime.utcnow()
    user.failed_login_attempts = 0
    user.locked_until = None
    db.session.commit()
    
    # Generate JWT token
    token = current_app.token_manager.generate_token(str(user.id), [user.role])
    
    log_security_event('login_success', 'INFO', user.id, ip_address, user_agent,
                      f"Successful login: {username}")
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Secure user logout."""
    user_id = current_user.id
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    logout_user()
    session.clear()
    
    log_security_event('logout', 'INFO', user_id, ip_address, user_agent, "User logout")
    
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user profile."""
    return jsonify(current_user.to_dict()), 200


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password with security validation."""
    data = request.get_json()
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current password and new password required'}), 400
    
    current_password = data['current_password']
    new_password = data['new_password']
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # Verify current password
    if not current_user.check_password(current_password):
        log_security_event('password_change_failed', 'MEDIUM', current_user.id, ip_address, user_agent,
                          "Failed password change - incorrect current password")
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Validate new password strength
    validation = SecurityValidator.validate_password_strength(new_password)
    if not validation['valid']:
        return jsonify({
            'error': 'Password does not meet security requirements',
            'issues': validation['issues']
        }), 400
    
    # Update password
    current_user.set_password(new_password)
    db.session.commit()
    
    log_security_event('password_changed', 'INFO', current_user.id, ip_address, user_agent,
                      "Password changed successfully")
    
    return jsonify({'message': 'Password changed successfully'}), 200


@auth_bp.route('/validate-token', methods=['POST'])
def validate_token():
    """Validate JWT token."""
    data = request.get_json()
    token = data.get('token') if data else None
    
    if not token:
        return jsonify({'valid': False, 'error': 'Token required'}), 400
    
    payload = current_app.token_manager.verify_token(token)
    
    if payload:
        user = User.query.get(int(payload['user_id']))
        if user and user.is_active:
            return jsonify({
                'valid': True,
                'user_id': payload['user_id'],
                'roles': payload['roles']
            }), 200
    
    return jsonify({'valid': False, 'error': 'Invalid or expired token'}), 401


def log_security_event(event_type: str, severity: str, user_id: int, ip_address: str, 
                      user_agent: str, description: str):
    """Log security event to database and audit log."""
    # Log to database
    event = SecurityEvent(
        event_type=event_type,
        severity=severity,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        description=description
    )
    db.session.add(event)
    db.session.commit()
    
    # Log to audit logger
    audit_logger = logging.getLogger('audit')
    audit_logger.info(f"{event_type}|{severity}|{user_id}|{ip_address}|{description}")