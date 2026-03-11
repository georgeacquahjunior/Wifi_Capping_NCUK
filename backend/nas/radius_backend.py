#!/usr/bin/env python3
"""
NAS Backend for FreeRADIUS Integration
Handles RADIUS authentication and accounting for WiFi capping system
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('ADMIN_SECRET_KEY', 'default_secret')

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'radius_user'),
    'password': os.getenv('DB_PASSWORD', 'radius_password'),
    'database': os.getenv('DB_NAME', 'wifi_capping')
}

# Create database engine
db_url = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RadiusBackend:
    """Backend handler for RADIUS operations"""
    
    def __init__(self):
        self.engine = engine
    
    def authenticate_user(self, username, password, nas_ip):
        """Authenticate user for RADIUS access request"""
        try:
            with Session() as session:
                # Check if user exists and is active
                result = session.execute(
                    text("SELECT username, password, data_limit_mb, data_used_mb, is_active FROM users WHERE username = :username"),
                    {"username": username}
                ).fetchone()
                
                if not result:
                    logger.warning(f"Authentication failed: User {username} not found")
                    return {"status": "reject", "reason": "User not found"}
                
                user_data = result._asdict()
                
                if not user_data['is_active']:
                    logger.warning(f"Authentication failed: User {username} is inactive")
                    return {"status": "reject", "reason": "User inactive"}
                
                if user_data['password'] != password:
                    logger.warning(f"Authentication failed: Invalid password for {username}")
                    return {"status": "reject", "reason": "Invalid password"}
                
                # Check data limit
                if user_data['data_used_mb'] >= user_data['data_limit_mb']:
                    logger.warning(f"Authentication failed: Data limit exceeded for {username}")
                    return {"status": "reject", "reason": "Data limit exceeded"}
                
                # Verify NAS device
                nas_result = session.execute(
                    text("SELECT nas_ip, is_active FROM nas_devices WHERE nas_ip = :nas_ip"),
                    {"nas_ip": nas_ip}
                ).fetchone()
                
                if not nas_result or not nas_result.is_active:
                    logger.warning(f"Authentication failed: Invalid or inactive NAS {nas_ip}")
                    return {"status": "reject", "reason": "Invalid NAS device"}
                
                logger.info(f"Authentication successful for user {username} from NAS {nas_ip}")
                return {
                    "status": "accept",
                    "user_data": {
                        "username": username,
                        "data_remaining_mb": user_data['data_limit_mb'] - user_data['data_used_mb']
                    }
                }
                
        except Exception as e:
            logger.error(f"Database error during authentication: {str(e)}")
            return {"status": "reject", "reason": "Database error"}
    
    def start_session(self, session_id, username, nas_ip, nas_port=None):
        """Start a new RADIUS accounting session"""
        try:
            with Session() as session:
                session.execute(
                    text("""INSERT INTO radius_sessions 
                         (session_id, username, nas_ip_address, nas_port, session_start, is_active)
                         VALUES (:session_id, :username, :nas_ip, :nas_port, NOW(), TRUE)"""),
                    {
                        "session_id": session_id,
                        "username": username,
                        "nas_ip": nas_ip,
                        "nas_port": nas_port
                    }
                )
                session.commit()
                logger.info(f"Session started: {session_id} for user {username}")
                return {"status": "success"}
                
        except Exception as e:
            logger.error(f"Error starting session: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def update_session(self, session_id, bytes_in=0, bytes_out=0):
        """Update session data usage"""
        try:
            with Session() as session:
                # Update session data
                session.execute(
                    text("""UPDATE radius_sessions 
                         SET bytes_in = :bytes_in, bytes_out = :bytes_out
                         WHERE session_id = :session_id AND is_active = TRUE"""),
                    {
                        "session_id": session_id,
                        "bytes_in": bytes_in,
                        "bytes_out": bytes_out
                    }
                )
                
                # Update user total data usage
                total_mb = (bytes_in + bytes_out) // (1024 * 1024)
                session.execute(
                    text("""UPDATE users u 
                         JOIN radius_sessions rs ON u.username = rs.username 
                         SET u.data_used_mb = (
                             SELECT SUM((rs2.bytes_in + rs2.bytes_out)) / (1024 * 1024)
                             FROM radius_sessions rs2 
                             WHERE rs2.username = u.username
                         )
                         WHERE rs.session_id = :session_id"""),
                    {"session_id": session_id}
                )
                
                session.commit()
                logger.info(f"Session updated: {session_id} - {total_mb}MB")
                return {"status": "success"}
                
        except Exception as e:
            logger.error(f"Error updating session: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def stop_session(self, session_id):
        """Stop a RADIUS accounting session"""
        try:
            with Session() as session:
                session.execute(
                    text("""UPDATE radius_sessions 
                         SET session_end = NOW(), is_active = FALSE
                         WHERE session_id = :session_id"""),
                    {"session_id": session_id}
                )
                session.commit()
                logger.info(f"Session stopped: {session_id}")
                return {"status": "success"}
                
        except Exception as e:
            logger.error(f"Error stopping session: {str(e)}")
            return {"status": "error", "message": str(e)}

# Initialize backend
radius_backend = RadiusBackend()

# API Endpoints
@app.route('/api/auth', methods=['POST'])
def authenticate():
    """RADIUS authentication endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    nas_ip = data.get('nas_ip')
    
    if not all([username, password, nas_ip]):
        return jsonify({"status": "reject", "reason": "Missing parameters"}), 400
    
    result = radius_backend.authenticate_user(username, password, nas_ip)
    return jsonify(result)

@app.route('/api/accounting/start', methods=['POST'])
def accounting_start():
    """RADIUS accounting start"""
    data = request.get_json()
    session_id = data.get('session_id')
    username = data.get('username')
    nas_ip = data.get('nas_ip')
    nas_port = data.get('nas_port')
    
    if not all([session_id, username, nas_ip]):
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
    
    result = radius_backend.start_session(session_id, username, nas_ip, nas_port)
    return jsonify(result)

@app.route('/api/accounting/update', methods=['POST'])
def accounting_update():
    """RADIUS accounting update"""
    data = request.get_json()
    session_id = data.get('session_id')
    bytes_in = data.get('bytes_in', 0)
    bytes_out = data.get('bytes_out', 0)
    
    if not session_id:
        return jsonify({"status": "error", "message": "Missing session_id"}), 400
    
    result = radius_backend.update_session(session_id, bytes_in, bytes_out)
    return jsonify(result)

@app.route('/api/accounting/stop', methods=['POST'])
def accounting_stop():
    """RADIUS accounting stop"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({"status": "error", "message": "Missing session_id"}), 400
    
    result = radius_backend.stop_session(session_id)
    return jsonify(result)

@app.route('/api/status', methods=['GET'])
def status():
    """Backend status check"""
    try:
        with Session() as session:
            result = session.execute(text("SELECT COUNT(*) as user_count FROM users")).fetchone()
            return jsonify({
                "status": "healthy",
                "total_users": result.user_count,
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('ADMIN_PORT', 5000)), debug=True)