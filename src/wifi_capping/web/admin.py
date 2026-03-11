"""
Administrative interface for policy and security management.
"""

import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from ..core.models import User, PolicyConfig, AUPViolationRecord, SecurityEvent, db
from ..policy import Policy, PolicyType, PolicyAction, BandwidthLimit
from ..aup import ViolationType, ViolationSeverity

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin role."""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard', methods=['GET'])
@login_required
@admin_required
def get_dashboard():
    """Get administrative dashboard data."""
    # System overview
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_policies = PolicyConfig.query.count()
    active_policies = PolicyConfig.query.filter_by(enabled=True).count()
    
    # Recent violations
    recent_violations = AUPViolationRecord.query.filter(
        AUPViolationRecord.timestamp > datetime.utcnow() - timedelta(days=7)
    ).count()
    
    # Security events
    security_events_today = SecurityEvent.query.filter(
        SecurityEvent.timestamp > datetime.utcnow().date()
    ).count()
    
    # Policy engine stats
    policy_summary = current_app.policy_engine.get_policy_summary()
    
    # AUP violations summary
    aup_summary = current_app.aup_monitor.get_violation_summary(days=30)
    
    return jsonify({
        'overview': {
            'total_users': total_users,
            'active_users': active_users,
            'total_policies': total_policies,
            'active_policies': active_policies,
            'recent_violations': recent_violations,
            'security_events_today': security_events_today
        },
        'policy_summary': policy_summary,
        'aup_summary': aup_summary
    }), 200


@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def list_users():
    """List all users."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    users = User.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': users.total,
            'pages': users.pages
        }
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def get_user(user_id):
    """Get user details."""
    user = User.query.get_or_404(user_id)
    
    # Get user violations
    violations = current_app.aup_monitor.get_user_violations(user.username)
    
    # Get user security events
    security_events = SecurityEvent.query.filter_by(user_id=user_id).order_by(
        SecurityEvent.timestamp.desc()
    ).limit(10).all()
    
    return jsonify({
        'user': user.to_dict(),
        'violations': [
            {
                'id': v.id,
                'type': v.violation_type.value,
                'severity': v.severity.value,
                'description': v.description,
                'timestamp': v.timestamp.isoformat(),
                'resolved': v.resolved
            } for v in violations
        ],
        'security_events': [event.to_dict() for event in security_events]
    }), 200


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Enable/disable user account."""
    user = User.query.get_or_404(user_id)
    
    user.is_active = not user.is_active
    db.session.commit()
    
    # Log security event
    from .auth import log_security_event
    log_security_event(
        'user_status_changed',
        'INFO',
        current_user.id,
        request.remote_addr,
        request.headers.get('User-Agent', ''),
        f"User {user.username} {'enabled' if user.is_active else 'disabled'}"
    )
    
    return jsonify({
        'message': f"User {'enabled' if user.is_active else 'disabled'} successfully",
        'user': user.to_dict()
    }), 200


@admin_bp.route('/policies', methods=['GET'])
@login_required
@admin_required
def list_policies():
    """List all policies."""
    policies = PolicyConfig.query.all()
    
    return jsonify({
        'policies': [policy.to_dict() for policy in policies]
    }), 200


@admin_bp.route('/policies', methods=['POST'])
@login_required
@admin_required
def create_policy():
    """Create new policy."""
    data = request.get_json()
    
    required_fields = ['policy_id', 'name', 'policy_type', 'configuration']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if policy ID already exists
    existing = PolicyConfig.query.filter_by(policy_id=data['policy_id']).first()
    if existing:
        return jsonify({'error': 'Policy ID already exists'}), 409
    
    try:
        # Validate configuration
        config = json.loads(data['configuration']) if isinstance(data['configuration'], str) else data['configuration']
        
        # Create policy configuration
        policy_config = PolicyConfig(
            policy_id=data['policy_id'],
            name=data['name'],
            policy_type=data['policy_type'],
            configuration=json.dumps(config),
            enabled=data.get('enabled', True),
            priority=data.get('priority', 5)
        )
        
        db.session.add(policy_config)
        db.session.commit()
        
        # Add to policy engine
        policy = Policy(
            id=data['policy_id'],
            name=data['name'],
            description=config.get('description', ''),
            policy_type=PolicyType(data['policy_type']),
            enabled=data.get('enabled', True),
            priority=data.get('priority', 5),
            conditions=config.get('conditions', {}),
            actions=[PolicyAction(action) for action in config.get('actions', [])],
            parameters=config.get('parameters', {}),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        current_app.policy_engine.add_policy(policy)
        
        return jsonify({
            'message': 'Policy created successfully',
            'policy': policy_config.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create policy: {e}")
        return jsonify({'error': 'Failed to create policy'}), 500


@admin_bp.route('/policies/<policy_id>', methods=['PUT'])
@login_required
@admin_required
def update_policy(policy_id):
    """Update existing policy."""
    policy_config = PolicyConfig.query.filter_by(policy_id=policy_id).first_or_404()
    data = request.get_json()
    
    try:
        # Update policy configuration
        if 'name' in data:
            policy_config.name = data['name']
        if 'configuration' in data:
            config = json.loads(data['configuration']) if isinstance(data['configuration'], str) else data['configuration']
            policy_config.configuration = json.dumps(config)
        if 'enabled' in data:
            policy_config.enabled = data['enabled']
        if 'priority' in data:
            policy_config.priority = data['priority']
        
        policy_config.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Update policy engine
        config = json.loads(policy_config.configuration)
        policy = Policy(
            id=policy_id,
            name=policy_config.name,
            description=config.get('description', ''),
            policy_type=PolicyType(policy_config.policy_type),
            enabled=policy_config.enabled,
            priority=policy_config.priority,
            conditions=config.get('conditions', {}),
            actions=[PolicyAction(action) for action in config.get('actions', [])],
            parameters=config.get('parameters', {}),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        current_app.policy_engine.add_policy(policy)
        
        return jsonify({
            'message': 'Policy updated successfully',
            'policy': policy_config.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update policy: {e}")
        return jsonify({'error': 'Failed to update policy'}), 500


@admin_bp.route('/policies/<policy_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_policy(policy_id):
    """Delete policy."""
    policy_config = PolicyConfig.query.filter_by(policy_id=policy_id).first_or_404()
    
    try:
        db.session.delete(policy_config)
        db.session.commit()
        
        # Remove from policy engine
        current_app.policy_engine.remove_policy(policy_id)
        
        return jsonify({'message': 'Policy deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete policy: {e}")
        return jsonify({'error': 'Failed to delete policy'}), 500


@admin_bp.route('/violations', methods=['GET'])
@login_required
@admin_required
def list_violations():
    """List AUP violations."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    severity = request.args.get('severity')
    resolved = request.args.get('resolved')
    
    query = AUPViolationRecord.query
    
    if severity:
        query = query.filter_by(severity=severity)
    if resolved is not None:
        query = query.filter_by(resolved=resolved.lower() == 'true')
    
    violations = query.order_by(AUPViolationRecord.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'violations': [violation.to_dict() for violation in violations.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': violations.total,
            'pages': violations.pages
        }
    }), 200


@admin_bp.route('/violations/<violation_id>/resolve', methods=['POST'])
@login_required
@admin_required
def resolve_violation(violation_id):
    """Resolve AUP violation."""
    data = request.get_json()
    penalty = data.get('penalty', '')
    notes = data.get('notes', '')
    
    # Apply penalty in AUP monitor
    success = current_app.aup_monitor.apply_penalty(violation_id, penalty, notes)
    
    if success:
        # Update database record
        violation_record = AUPViolationRecord.query.filter_by(violation_id=violation_id).first()
        if violation_record:
            violation_record.resolved = True
            violation_record.penalty_applied = penalty
            violation_record.resolution_notes = notes
            db.session.commit()
        
        return jsonify({'message': 'Violation resolved successfully'}), 200
    else:
        return jsonify({'error': 'Violation not found'}), 404


@admin_bp.route('/security/report', methods=['GET'])
@login_required
@admin_required
def get_security_report():
    """Generate comprehensive security report."""
    days = request.args.get('days', 30, type=int)
    
    # Generate reports
    aup_report = current_app.aup_monitor.generate_aup_report(days=days)
    
    # Security events summary
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    security_events = SecurityEvent.query.filter(
        SecurityEvent.timestamp > cutoff_date
    ).all()
    
    event_summary = {}
    for event in security_events:
        event_type = event.event_type
        event_summary[event_type] = event_summary.get(event_type, 0) + 1
    
    return jsonify({
        'aup_report': aup_report,
        'security_events': {
            'total': len(security_events),
            'by_type': event_summary
        },
        'report_period_days': days,
        'generated_at': datetime.utcnow().isoformat()
    }), 200