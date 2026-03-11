"""
API endpoints for network policy enforcement and monitoring.
"""

import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from ..core.models import NetworkSession, User, db

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)


@api_bp.route('/network/evaluate', methods=['POST'])
@login_required
def evaluate_network_request():
    """Evaluate network request against policies."""
    data = request.get_json()
    
    required_fields = ['user_id', 'device_mac', 'destination']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user_id = data['user_id']
    device_mac = data['device_mac']
    request_data = {
        'source_ip': data.get('source_ip'),
        'destination': data['destination'],
        'protocol': data.get('protocol', 'TCP'),
        'port': data.get('port')
    }
    
    # Evaluate policies
    policy_result = current_app.policy_engine.evaluate_policies(user_id, device_mac, request_data)
    
    # Check AUP compliance for URL requests
    if 'http' in data['destination'].lower():
        aup_result = current_app.aup_monitor.check_content_compliance(
            data['destination'], user_id, device_mac
        )
        
        # Merge AUP results
        if not aup_result['allowed']:
            policy_result['allowed'] = False
            policy_result['reasons'].extend([f"AUP violation: {reason}" for reason in aup_result.get('violations', [])])
    
    return jsonify(policy_result), 200


@api_bp.route('/network/session/start', methods=['POST'])
@login_required
def start_network_session():
    """Start a new network session."""
    data = request.get_json()
    
    required_fields = ['user_id', 'device_mac', 'ip_address']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Create new session
    session = NetworkSession(
        user_id=data['user_id'],
        device_mac=data['device_mac'],
        ip_address=data['ip_address']
    )
    
    db.session.add(session)
    db.session.commit()
    
    logger.info(f"Network session started for user {data['user_id']}, device {data['device_mac']}")
    
    return jsonify({
        'message': 'Session started successfully',
        'session_id': session.id,
        'session': session.to_dict()
    }), 201


@api_bp.route('/network/session/<int:session_id>/update', methods=['POST'])
@login_required
def update_network_session(session_id):
    """Update network session with usage data."""
    session = NetworkSession.query.get_or_404(session_id)
    data = request.get_json()
    
    if 'bytes_downloaded' in data:
        session.bytes_downloaded = data['bytes_downloaded']
    if 'bytes_uploaded' in data:
        session.bytes_uploaded = data['bytes_uploaded']
    
    db.session.commit()
    
    # Check bandwidth compliance
    usage_data = {
        'download_mb': session.bytes_downloaded / (1024 * 1024),
        'upload_mb': session.bytes_uploaded / (1024 * 1024),
        'session_duration': (datetime.utcnow() - session.start_time).total_seconds()
    }
    
    bandwidth_result = current_app.aup_monitor.check_bandwidth_compliance(
        session.user.username, session.device_mac, usage_data
    )
    
    return jsonify({
        'message': 'Session updated successfully',
        'session': session.to_dict(),
        'bandwidth_compliance': bandwidth_result
    }), 200


@api_bp.route('/network/session/<int:session_id>/end', methods=['POST'])
@login_required
def end_network_session(session_id):
    """End a network session."""
    session = NetworkSession.query.get_or_404(session_id)
    
    session.end_time = datetime.utcnow()
    session.session_active = False
    
    db.session.commit()
    
    logger.info(f"Network session ended for user {session.user_id}, session {session_id}")
    
    return jsonify({
        'message': 'Session ended successfully',
        'session': session.to_dict()
    }), 200


@api_bp.route('/aup/check-content', methods=['POST'])
@login_required
def check_content_aup():
    """Check content against AUP policies."""
    data = request.get_json()
    
    required_fields = ['url', 'user_id', 'device_mac']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    result = current_app.aup_monitor.check_content_compliance(
        data['url'], data['user_id'], data['device_mac']
    )
    
    return jsonify(result), 200


@api_bp.route('/aup/report-activity', methods=['POST'])
@login_required
def report_suspicious_activity():
    """Report suspicious network activity."""
    data = request.get_json()
    
    required_fields = ['user_id', 'device_mac', 'activity_data']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    violations = current_app.aup_monitor.detect_suspicious_activity(
        data['user_id'], data['device_mac'], data['activity_data']
    )
    
    return jsonify({
        'violations_detected': len(violations),
        'violation_ids': [v.id for v in violations]
    }), 200


@api_bp.route('/policies/evaluate-user', methods=['POST'])
@login_required
def evaluate_user_policies():
    """Evaluate policies for a specific user."""
    data = request.get_json()
    
    if not data.get('user_id'):
        return jsonify({'error': 'User ID required'}), 400
    
    user_id = data['user_id']
    device_mac = data.get('device_mac', '00:00:00:00:00:00')
    
    # Get user group
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Evaluate policies
    result = current_app.policy_engine.evaluate_policies(
        user.username, device_mac, {'user_group': user.user_group}
    )
    
    return jsonify(result), 200


@api_bp.route('/security/validate-config', methods=['POST'])
@login_required
def validate_security_config():
    """Validate security configuration."""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    from ..security import SecurityValidator
    from ..core.config import get_config
    
    config = get_config()
    validation_result = config.validate_security_config()
    
    # Additional security checks
    security_report = SecurityValidator.generate_security_report()
    
    return jsonify({
        'validation': validation_result,
        'security_report': security_report
    }), 200


@api_bp.route('/monitoring/metrics', methods=['GET'])
@login_required
def get_monitoring_metrics():
    """Get system monitoring metrics."""
    from ..monitoring import SystemMonitor
    
    monitor = SystemMonitor()
    metrics = monitor.get_current_metrics()
    
    return jsonify(metrics), 200


@api_bp.route('/health', methods=['GET'])
def health_check():
    """System health check endpoint."""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check policy engine
        policy_count = len(current_app.policy_engine.policies)
        
        # Check AUP monitor
        aup_active = current_app.aup_monitor.monitoring_active
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'components': {
                'database': 'ok',
                'policy_engine': f'ok ({policy_count} policies)',
                'aup_monitor': 'ok' if aup_active else 'inactive'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503