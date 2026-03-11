"""
Core configuration management with security features.
"""

import os
import secrets
from typing import Dict, Any
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class with security defaults."""
    
    # Security Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or secrets.token_urlsafe(32)
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or Fernet.generate_key().decode()
    
    # Database Configuration with encryption
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///wifi_capping.db')
    DATABASE_ENCRYPTION = os.environ.get('DATABASE_ENCRYPTION', 'true').lower() == 'true'
    
    # SSL/TLS Configuration
    SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH', '/etc/ssl/certs/wifi-capping.crt')
    SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH', '/etc/ssl/private/wifi-capping.key')
    SSL_REQUIRED = os.environ.get('SSL_REQUIRED', 'true').lower() == 'true'
    
    # Network Configuration
    NETWORK_INTERFACE = os.environ.get('NETWORK_INTERFACE', 'wlan0')
    MANAGEMENT_INTERFACE = os.environ.get('MANAGEMENT_INTERFACE', 'eth0')
    MONITORING_PORT = int(os.environ.get('MONITORING_PORT', 8443))
    
    # Policy Configuration
    DEFAULT_BANDWIDTH_LIMIT = os.environ.get('DEFAULT_BANDWIDTH_LIMIT', '10MB')
    DEFAULT_SESSION_TIMEOUT = int(os.environ.get('DEFAULT_SESSION_TIMEOUT', 3600))
    POLICY_ENFORCEMENT = os.environ.get('POLICY_ENFORCEMENT', 'strict')
    
    # AUP Configuration
    AUP_ENABLED = os.environ.get('AUP_ENABLED', 'true').lower() == 'true'
    CONTENT_FILTERING = os.environ.get('CONTENT_FILTERING', 'true').lower() == 'true'
    AUDIT_LOGGING = os.environ.get('AUDIT_LOGGING', 'true').lower() == 'true'
    VIOLATION_NOTIFICATION = os.environ.get('VIOLATION_NOTIFICATION', 'true').lower() == 'true'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', '/var/log/wifi-capping/app.log')
    AUDIT_LOG_FILE = os.environ.get('AUDIT_LOG_FILE', '/var/log/wifi-capping/audit.log')
    
    @classmethod
    def validate_security_config(cls) -> Dict[str, Any]:
        """Validate security configuration and return issues."""
        issues = []
        warnings = []
        
        # Check for default/weak keys
        if cls.SECRET_KEY == 'your-secret-key-here-change-this':
            issues.append("SECRET_KEY is using default value - must be changed")
        
        if len(cls.SECRET_KEY) < 32:
            issues.append("SECRET_KEY must be at least 32 characters long")
        
        # Check SSL configuration
        if cls.SSL_REQUIRED:
            if not os.path.exists(cls.SSL_CERT_PATH):
                issues.append(f"SSL certificate not found at {cls.SSL_CERT_PATH}")
            if not os.path.exists(cls.SSL_KEY_PATH):
                issues.append(f"SSL key not found at {cls.SSL_KEY_PATH}")
        else:
            warnings.append("SSL is disabled - this is not recommended for production")
        
        # Check database encryption
        if not cls.DATABASE_ENCRYPTION:
            warnings.append("Database encryption is disabled")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }


class DevelopmentConfig(Config):
    """Development configuration with relaxed security for testing."""
    DEBUG = True
    SSL_REQUIRED = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'
    SSL_REQUIRED = False
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration with maximum security."""
    DEBUG = False
    TESTING = False
    SSL_REQUIRED = True
    
    @classmethod
    def validate_production_config(cls) -> Dict[str, Any]:
        """Additional validation for production environment."""
        result = cls.validate_security_config()
        
        # Additional production checks
        if cls.DEBUG:
            result['issues'].append("DEBUG mode must be disabled in production")
        
        if not cls.SSL_REQUIRED:
            result['issues'].append("SSL must be enabled in production")
        
        if cls.DATABASE_URL.startswith('sqlite:///'):
            result['warnings'].append("SQLite is not recommended for production - consider PostgreSQL")
        
        return result


config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Config:
    """Get configuration class based on environment."""
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    return config_map.get(config_name, DevelopmentConfig)