"""
Monitoring blueprint for system metrics and real-time monitoring.
"""

import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from ..core.models import SystemMetrics, NetworkSession, SecurityEvent, db

logger = logging.getLogger(__name__)
monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route('/dashboard', methods=['GET'])
@login_required
def get_monitoring_dashboard():
    """Get real-time monitoring dashboard data."""
    # Current active sessions
    active_sessions = NetworkSession.query.filter_by(session_active=True).count()
    
    # Bandwidth usage in last hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_sessions = NetworkSession.query.filter(
        NetworkSession.start_time > one_hour_ago
    ).all()
    
    total_download = sum(session.bytes_downloaded for session in recent_sessions)
    total_upload = sum(session.bytes_uploaded for session in recent_sessions)
    
    # Security events in last 24 hours
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    security_events = SecurityEvent.query.filter(
        SecurityEvent.timestamp > twenty_four_hours_ago
    ).count()
    
    # Policy enforcement stats
    policy_summary = current_app.policy_engine.get_policy_summary()
    
    # AUP violations in last 7 days
    aup_summary = current_app.aup_monitor.get_violation_summary(days=7)
    
    return jsonify({
        'active_sessions': active_sessions,
        'bandwidth_usage': {
            'download_mb': total_download / (1024 * 1024),
            'upload_mb': total_upload / (1024 * 1024),
            'period_hours': 1
        },
        'security_events_24h': security_events,
        'policy_summary': policy_summary,
        'aup_summary': aup_summary,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@monitoring_bp.route('/sessions/active', methods=['GET'])
@login_required
def get_active_sessions():
    """Get currently active network sessions."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    sessions = NetworkSession.query.filter_by(session_active=True).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    session_data = []
    for session in sessions.items:
        data = session.to_dict()
        data['user'] = session.user.to_dict() if session.user else None
        data['duration_minutes'] = (datetime.utcnow() - session.start_time).total_seconds() / 60
        session_data.append(data)
    
    return jsonify({
        'sessions': session_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': sessions.total,
            'pages': sessions.pages
        }
    }), 200


@monitoring_bp.route('/bandwidth/top-users', methods=['GET'])
@login_required
def get_top_bandwidth_users():
    """Get top bandwidth consuming users."""
    days = request.args.get('days', 7, type=int)
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Query sessions and aggregate by user
    sessions = NetworkSession.query.filter(
        NetworkSession.start_time > cutoff_date
    ).all()
    
    user_usage = {}
    for session in sessions:
        user_id = session.user_id
        if user_id not in user_usage:
            user_usage[user_id] = {
                'user': session.user.to_dict() if session.user else {'id': user_id},
                'total_download': 0,
                'total_upload': 0,
                'session_count': 0
            }
        
        user_usage[user_id]['total_download'] += session.bytes_downloaded
        user_usage[user_id]['total_upload'] += session.bytes_uploaded
        user_usage[user_id]['session_count'] += 1
    
    # Sort by total usage
    top_users = sorted(
        user_usage.values(),
        key=lambda x: x['total_download'] + x['total_upload'],
        reverse=True
    )[:20]
    
    # Convert bytes to MB
    for user in top_users:
        user['total_download_mb'] = user['total_download'] / (1024 * 1024)
        user['total_upload_mb'] = user['total_upload'] / (1024 * 1024)
        user['total_mb'] = user['total_download_mb'] + user['total_upload_mb']
    
    return jsonify({
        'top_users': top_users,
        'period_days': days
    }), 200


@monitoring_bp.route('/security/events', methods=['GET'])
@login_required
def get_security_events():
    """Get security events."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    event_type = request.args.get('event_type')
    severity = request.args.get('severity')
    
    query = SecurityEvent.query
    
    if event_type:
        query = query.filter_by(event_type=event_type)
    if severity:
        query = query.filter_by(severity=severity)
    
    events = query.order_by(SecurityEvent.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'events': [event.to_dict() for event in events.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': events.total,
            'pages': events.pages
        }
    }), 200


@monitoring_bp.route('/metrics/system', methods=['GET'])
@login_required
def get_system_metrics():
    """Get system performance metrics."""
    from ..monitoring import SystemMonitor
    
    monitor = SystemMonitor()
    current_metrics = monitor.get_current_metrics()
    
    # Get historical metrics
    hours = request.args.get('hours', 24, type=int)
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    historical_metrics = SystemMetrics.query.filter(
        SystemMetrics.timestamp > cutoff_time
    ).order_by(SystemMetrics.timestamp.asc()).all()
    
    # Group by metric name
    metrics_by_name = {}
    for metric in historical_metrics:
        if metric.metric_name not in metrics_by_name:
            metrics_by_name[metric.metric_name] = []
        metrics_by_name[metric.metric_name].append(metric.to_dict())
    
    return jsonify({
        'current_metrics': current_metrics,
        'historical_metrics': metrics_by_name,
        'period_hours': hours
    }), 200


@monitoring_bp.route('/alerts', methods=['GET'])
@login_required
def get_alerts():
    """Get system alerts based on thresholds."""
    alerts = []
    
    # Check active sessions threshold
    active_sessions = NetworkSession.query.filter_by(session_active=True).count()
    if active_sessions > 100:  # Configurable threshold
        alerts.append({
            'type': 'high_session_count',
            'severity': 'warning',
            'message': f'High number of active sessions: {active_sessions}',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Check recent security events
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_high_severity_events = SecurityEvent.query.filter(
        SecurityEvent.timestamp > one_hour_ago,
        SecurityEvent.severity.in_(['HIGH', 'CRITICAL'])
    ).count()
    
    if recent_high_severity_events > 5:
        alerts.append({
            'type': 'security_events_spike',
            'severity': 'high',
            'message': f'High number of security events in last hour: {recent_high_severity_events}',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Check unresolved AUP violations
    unresolved_violations = len([
        v for v in current_app.aup_monitor.violations.values()
        if not v.resolved and v.severity.value in ['high', 'critical']
    ])
    
    if unresolved_violations > 10:
        alerts.append({
            'type': 'unresolved_violations',
            'severity': 'medium',
            'message': f'High number of unresolved AUP violations: {unresolved_violations}',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    return jsonify({
        'alerts': alerts,
        'alert_count': len(alerts)
    }), 200


@monitoring_bp.route('/reports/bandwidth', methods=['GET'])
@login_required
def generate_bandwidth_report():
    """Generate bandwidth usage report."""
    days = request.args.get('days', 30, type=int)
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    sessions = NetworkSession.query.filter(
        NetworkSession.start_time > cutoff_date
    ).all()
    
    # Daily usage aggregation
    daily_usage = {}
    user_group_usage = {}
    
    for session in sessions:
        day = session.start_time.strftime('%Y-%m-%d')
        user_group = session.user.user_group if session.user else 'unknown'
        
        if day not in daily_usage:
            daily_usage[day] = {'download': 0, 'upload': 0, 'sessions': 0}
        
        if user_group not in user_group_usage:
            user_group_usage[user_group] = {'download': 0, 'upload': 0, 'sessions': 0}
        
        daily_usage[day]['download'] += session.bytes_downloaded
        daily_usage[day]['upload'] += session.bytes_uploaded
        daily_usage[day]['sessions'] += 1
        
        user_group_usage[user_group]['download'] += session.bytes_downloaded
        user_group_usage[user_group]['upload'] += session.bytes_uploaded
        user_group_usage[user_group]['sessions'] += 1
    
    # Convert to MB
    for day_data in daily_usage.values():
        day_data['download_mb'] = day_data['download'] / (1024 * 1024)
        day_data['upload_mb'] = day_data['upload'] / (1024 * 1024)
    
    for group_data in user_group_usage.values():
        group_data['download_mb'] = group_data['download'] / (1024 * 1024)
        group_data['upload_mb'] = group_data['upload'] / (1024 * 1024)
    
    return jsonify({
        'daily_usage': daily_usage,
        'user_group_usage': user_group_usage,
        'period_days': days,
        'generated_at': datetime.utcnow().isoformat()
    }), 200


@monitoring_bp.route('/reports/aup-compliance', methods=['GET'])
@login_required
def generate_aup_compliance_report():
    """Generate AUP compliance report."""
    days = request.args.get('days', 30, type=int)
    
    report = current_app.aup_monitor.generate_aup_report(days=days)
    
    return jsonify(report), 200