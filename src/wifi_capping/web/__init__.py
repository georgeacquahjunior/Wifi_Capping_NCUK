"""
Web Interface for WiFi Capping System
Provides HTTP API and basic web UI for system management
"""

import logging
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

from ..capping import WifiCappingService
from ..utils.config import Config
from ..utils.security import sanitize_input, validate_ip_address


logger = logging.getLogger(__name__)


def create_app(config: Config) -> Flask:
    """Create and configure Flask application"""
    
    app = Flask(__name__)
    app.config.update(config.get_flask_config())
    
    # Initialize WiFi capping service
    wifi_service = WifiCappingService(config)
    wifi_service.start()
    
    # Store service reference in app context
    app.wifi_service = wifi_service
    
    # Web UI Template
    DASHBOARD_TEMPLATE = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>WiFi Capping NCUK - Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
            .stats { display: flex; gap: 20px; margin: 20px 0; }
            .stat-card { background: #ecf0f1; padding: 15px; border-radius: 5px; flex: 1; }
            .sessions { margin: 20px 0; }
            .session { background: white; border: 1px solid #bdc3c7; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .capped { border-left: 5px solid #e74c3c; }
            .active { border-left: 5px solid #27ae60; }
            .auth-form { background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .form-group { margin: 10px 0; }
            label { display: block; margin-bottom: 5px; }
            input { padding: 8px; width: 200px; border: 1px solid #bdc3c7; border-radius: 3px; }
            button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
            button:hover { background: #2980b9; }
            .error { color: #e74c3c; }
            .success { color: #27ae60; }
        </style>
        <script>
            function refreshPage() {
                location.reload();
            }
            
            function authenticateUser() {
                const formData = new FormData(document.getElementById('authForm'));
                const data = Object.fromEntries(formData);
                
                fetch('/api/authenticate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    const messageEl = document.getElementById('authMessage');
                    if (result.success) {
                        messageEl.innerHTML = '<span class="success">Authentication successful! Session ID: ' + result.session_id + '</span>';
                        setTimeout(refreshPage, 2000);
                    } else {
                        messageEl.innerHTML = '<span class="error">Authentication failed: ' + result.error + '</span>';
                    }
                })
                .catch(error => {
                    document.getElementById('authMessage').innerHTML = '<span class="error">Error: ' + error + '</span>';
                });
            }
            
            function endSession(sessionId) {
                fetch('/api/sessions/' + sessionId + '/end', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        refreshPage();
                    } else {
                        alert('Failed to end session');
                    }
                })
                .catch(error => alert('Error: ' + error));
            }
            
            setInterval(refreshPage, 30000); // Auto-refresh every 30 seconds
        </script>
    </head>
    <body>
        <div class="header">
            <h1>WiFi Capping NCUK Dashboard</h1>
            <p>Secure freeRADIUS Integration - Real-time Monitoring</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Service Status</h3>
                <p><strong>Running:</strong> {{ status.service_running }}</p>
                <p><strong>RADIUS Connected:</strong> {{ status.radius_connected }}</p>
                <p><strong>Active Sessions:</strong> {{ status.active_sessions }}</p>
            </div>
            <div class="stat-card">
                <h3>Configuration</h3>
                <p><strong>Default Bandwidth Limit:</strong> {{ status.default_bandwidth_limit_mb }} MB</p>
                <p><strong>Monitoring Interval:</strong> {{ status.monitoring_interval }} seconds</p>
                <p><strong>Last Updated:</strong> {{ current_time }}</p>
            </div>
        </div>
        
        <div class="auth-form">
            <h3>User Authentication</h3>
            <form id="authForm" onsubmit="event.preventDefault(); authenticateUser();">
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" name="password" required>
                </div>
                <div class="form-group">
                    <label>User IP:</label>
                    <input type="text" name="user_ip" placeholder="192.168.1.100" required>
                </div>
                <div class="form-group">
                    <label>NAS IP:</label>
                    <input type="text" name="nas_ip" placeholder="192.168.1.1" required>
                </div>
                <div class="form-group">
                    <label>NAS Port:</label>
                    <input type="number" name="nas_port" value="0" required>
                </div>
                <div class="form-group">
                    <label>Bandwidth Limit (MB):</label>
                    <input type="number" name="bandwidth_limit_mb" placeholder="Optional">
                </div>
                <button type="submit">Authenticate & Start Session</button>
            </form>
            <div id="authMessage"></div>
        </div>
        
        <div class="sessions">
            <h3>Active Sessions</h3>
            {% if sessions %}
                {% for session_id, session in sessions.items() %}
                <div class="session {{ 'capped' if session.is_capped else 'active' }}">
                    <h4>{{ session.username }} ({{ session_id[:8] }}...)</h4>
                    <p><strong>User IP:</strong> {{ session.user_ip }}</p>
                    <p><strong>Duration:</strong> {{ session.duration_seconds }} seconds</p>
                    <p><strong>Usage:</strong> {{ "%.2f"|format(session.total_mb) }} / {{ session.bandwidth_limit_mb }} MB</p>
                    <p><strong>Remaining:</strong> {{ "%.2f"|format(session.remaining_mb) }} MB</p>
                    <p><strong>Status:</strong> {% if session.is_capped %}CAPPED{% else %}ACTIVE{% endif %}</p>
                    <button onclick="endSession('{{ session_id }}')">End Session</button>
                </div>
                {% endfor %}
            {% else %}
                <p>No active sessions</p>
            {% endif %}
        </div>
        
        <div style="margin-top: 40px; text-align: center; color: #7f8c8d;">
            <p>WiFi Capping NCUK v1.0.0 - Secure freeRADIUS Integration</p>
            <button onclick="refreshPage()">Refresh Dashboard</button>
        </div>
    </body>
    </html>
    '''
    
    @app.route('/')
    def dashboard():
        """Main dashboard page"""
        try:
            status = app.wifi_service.get_service_status()
            sessions = app.wifi_service.bandwidth_monitor.get_all_sessions()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return render_template_string(
                DASHBOARD_TEMPLATE,
                status=status,
                sessions=sessions,
                current_time=current_time
            )
        except Exception as e:
            logger.error(f"Dashboard error: {str(e)}")
            return f"Dashboard error: {str(e)}", 500

    @app.route('/api/status')
    def api_status():
        """Get service status"""
        try:
            status = app.wifi_service.get_service_status()
            return jsonify(status)
        except Exception as e:
            logger.error(f"Status API error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/sessions')
    def api_sessions():
        """Get all active sessions"""
        try:
            sessions = app.wifi_service.bandwidth_monitor.get_all_sessions()
            return jsonify(sessions)
        except Exception as e:
            logger.error(f"Sessions API error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/sessions/<session_id>')
    def api_session_details(session_id):
        """Get details for a specific session"""
        try:
            session_id = sanitize_input(session_id)
            session_info = app.wifi_service.bandwidth_monitor.get_session_info(session_id)
            
            if session_info is None:
                return jsonify({"error": "Session not found"}), 404
                
            return jsonify(session_info)
        except Exception as e:
            logger.error(f"Session details API error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/authenticate', methods=['POST'])
    def api_authenticate():
        """Authenticate user and start session"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['username', 'password', 'user_ip', 'nas_ip', 'nas_port']
            for field in required_fields:
                if field not in data:
                    return jsonify({"success": False, "error": f"Missing field: {field}"}), 400
            
            # Sanitize inputs
            username = sanitize_input(data['username'])
            password = data['password']  # Don't sanitize password
            user_ip = sanitize_input(data['user_ip'])
            nas_ip = sanitize_input(data['nas_ip'])
            nas_port = int(data['nas_port'])
            
            # Optional bandwidth limit
            bandwidth_limit_mb = None
            if 'bandwidth_limit_mb' in data and data['bandwidth_limit_mb']:
                bandwidth_limit_mb = int(data['bandwidth_limit_mb'])
            
            # Validate IP addresses
            if not validate_ip_address(user_ip):
                return jsonify({"success": False, "error": "Invalid user IP address"}), 400
                
            if not validate_ip_address(nas_ip):
                return jsonify({"success": False, "error": "Invalid NAS IP address"}), 400
            
            # Authenticate and start session
            success, session_id = app.wifi_service.authenticate_and_start_session(
                username, password, user_ip, nas_ip, nas_port, bandwidth_limit_mb
            )
            
            if success:
                logger.info(f"API authentication successful for user {username}")
                return jsonify({
                    "success": True,
                    "session_id": session_id,
                    "message": "Authentication successful"
                })
            else:
                logger.warning(f"API authentication failed for user {username}")
                return jsonify({
                    "success": False,
                    "error": "Authentication failed"
                }), 401
                
        except Exception as e:
            logger.error(f"Authentication API error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/sessions/<session_id>/end', methods=['POST'])
    def api_end_session(session_id):
        """End a specific session"""
        try:
            session_id = sanitize_input(session_id)
            success = app.wifi_service.bandwidth_monitor.end_session(session_id)
            
            if success:
                return jsonify({"success": True, "message": "Session ended"})
            else:
                return jsonify({"success": False, "error": "Failed to end session"}), 400
                
        except Exception as e:
            logger.error(f"End session API error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/test-radius')
    def api_test_radius():
        """Test RADIUS server connection"""
        try:
            connected = app.wifi_service.radius_client.test_connection()
            return jsonify({
                "connected": connected,
                "message": "RADIUS server is reachable" if connected else "RADIUS server not reachable"
            })
        except Exception as e:
            logger.error(f"RADIUS test API error: {str(e)}")
            return jsonify({"connected": False, "error": str(e)}), 500

    @app.teardown_appcontext
    def cleanup(error):
        """Cleanup when app context is destroyed"""
        if hasattr(app, 'wifi_service'):
            app.wifi_service.stop()

    return app


def run_web_server(config: Config):
    """Run the web server"""
    app = create_app(config)
    
    logger.info(f"Starting web server on {config.flask_host}:{config.flask_port}")
    
    try:
        app.run(
            host=config.flask_host,
            port=config.flask_port,
            debug=config.flask_debug
        )
    except KeyboardInterrupt:
        logger.info("Web server stopped by user")
    except Exception as e:
        logger.error(f"Web server error: {str(e)}")
        raise
    finally:
        if hasattr(app, 'wifi_service'):
            app.wifi_service.stop()