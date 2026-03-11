"""
Core application factory and initialization.
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from ..security import EncryptionManager, TokenManager, CertificateManager
from ..policy import PolicyEngine, DefaultPolicyTemplates
from ..aup import AUPMonitor, AUPPolicyManager
from .config import get_config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name=None):
    """Create Flask application with security and policy enforcement."""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Validate security configuration
    security_validation = config.validate_security_config()
    if not security_validation['valid']:
        logging.error("Security configuration validation failed:")
        for issue in security_validation['issues']:
            logging.error(f"  - {issue}")
        raise ValueError("Invalid security configuration")
    
    # Log warnings
    for warning in security_validation['warnings']:
        logging.warning(f"Security warning: {warning}")
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Initialize security components
    app.encryption_manager = EncryptionManager(app.config['ENCRYPTION_KEY'])
    app.token_manager = TokenManager(app.config['JWT_SECRET_KEY'])
    
    # Initialize policy engine
    app.policy_engine = PolicyEngine()
    
    # Add default policies
    default_policies = [
        DefaultPolicyTemplates.create_student_bandwidth_policy(),
        DefaultPolicyTemplates.create_staff_bandwidth_policy(),
        DefaultPolicyTemplates.create_night_time_policy()
    ]
    
    for policy in default_policies:
        app.policy_engine.add_policy(policy)
    
    # Add default user groups
    default_groups = DefaultPolicyTemplates.create_default_user_groups()
    for group in default_groups:
        app.policy_engine.add_user_group(group)
    
    # Initialize AUP monitoring
    app.aup_monitor = AUPMonitor()
    app.aup_policy_manager = AUPPolicyManager()
    
    # Set default AUP policy
    default_aup_policy = app.aup_policy_manager.create_default_policy()
    app.aup_policy_manager.policies[default_aup_policy.id] = default_aup_policy
    app.aup_policy_manager.set_active_policy(default_aup_policy.id)
    
    # Configure logging
    configure_logging(app)
    
    # Generate SSL certificates if needed
    if app.config['SSL_REQUIRED'] and not os.path.exists(app.config['SSL_CERT_PATH']):
        logging.info("Generating self-signed SSL certificate...")
        cert_pem, key_pem = CertificateManager.generate_self_signed_cert("wifi-capping.ncuk.ac.uk")
        CertificateManager.save_cert_and_key(
            cert_pem, key_pem,
            app.config['SSL_CERT_PATH'],
            app.config['SSL_KEY_PATH']
        )
        logging.info("SSL certificate generated successfully")
    
    # Register blueprints
    register_blueprints(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


def configure_logging(app):
    """Configure application logging."""
    log_level = getattr(logging, app.config['LOG_LEVEL'])
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(app.config['LOG_FILE']),
            logging.StreamHandler()
        ]
    )
    
    # Configure audit logger
    audit_logger = logging.getLogger('audit')
    audit_handler = logging.FileHandler(app.config['AUDIT_LOG_FILE'])
    audit_handler.setFormatter(logging.Formatter('%(asctime)s AUDIT: %(message)s'))
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)


def register_blueprints(app):
    """Register application blueprints."""
    from ..web.auth import auth_bp
    from ..web.admin import admin_bp
    from ..web.api import api_bp
    from ..web.monitoring import monitoring_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(monitoring_bp, url_prefix='/monitoring')


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    from ..web.models import User
    return User.query.get(int(user_id))