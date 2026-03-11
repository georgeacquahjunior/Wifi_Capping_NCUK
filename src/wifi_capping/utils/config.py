"""
Configuration Management
Handles loading and validation of configuration settings
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class Config:
    """Configuration management for WiFi Capping system"""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration from environment variables
        
        Args:
            env_file: Path to .env file (optional)
        """
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file)
        else:
            load_dotenv()  # Load from default .env file if exists
            
        self._load_config()
        self._validate_config()

    def _load_config(self):
        """Load configuration from environment variables"""
        
        # freeRADIUS Configuration
        self.radius_host = os.getenv("RADIUS_HOST", "127.0.0.1")
        self.radius_auth_port = int(os.getenv("RADIUS_AUTH_PORT", "1812"))
        self.radius_acct_port = int(os.getenv("RADIUS_ACCT_PORT", "1813"))
        self.radius_secret = os.getenv("RADIUS_SECRET", "testing123")
        
        # WiFi Capping Configuration
        self.default_bandwidth_limit_mb = int(os.getenv("DEFAULT_BANDWIDTH_LIMIT_MB", "1000"))
        self.monitoring_interval_seconds = int(os.getenv("MONITORING_INTERVAL_SECONDS", "60"))
        self.max_session_time_hours = int(os.getenv("MAX_SESSION_TIME_HOURS", "24"))
        
        # Web Interface Configuration
        self.flask_secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
        self.flask_host = os.getenv("FLASK_HOST", "0.0.0.0")
        self.flask_port = int(os.getenv("FLASK_PORT", "5000"))
        self.flask_debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
        
        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_file = os.getenv("LOG_FILE", "wifi_capping.log")

    def _validate_config(self):
        """Validate configuration values"""
        
        # Validate RADIUS configuration
        if not self.radius_secret or self.radius_secret == "your_radius_secret_here":
            logger.warning("RADIUS secret not properly configured - using default")
            
        if not (1 <= self.radius_auth_port <= 65535):
            raise ValueError(f"Invalid RADIUS auth port: {self.radius_auth_port}")
            
        if not (1 <= self.radius_acct_port <= 65535):
            raise ValueError(f"Invalid RADIUS accounting port: {self.radius_acct_port}")
            
        # Validate bandwidth limits
        if self.default_bandwidth_limit_mb <= 0:
            raise ValueError("Default bandwidth limit must be positive")
            
        if self.monitoring_interval_seconds <= 0:
            raise ValueError("Monitoring interval must be positive")
            
        if self.max_session_time_hours <= 0:
            raise ValueError("Max session time must be positive")
            
        # Validate Flask configuration
        if self.flask_secret_key == "your_flask_secret_key_here":
            logger.warning("Flask secret key not properly configured - using default")
            
        logger.info("Configuration validation successful")

    def get_radius_config(self) -> dict:
        """Get RADIUS-specific configuration as dictionary"""
        return {
            "host": self.radius_host,
            "auth_port": self.radius_auth_port,
            "acct_port": self.radius_acct_port,
            "secret": self.radius_secret
        }

    def get_flask_config(self) -> dict:
        """Get Flask-specific configuration as dictionary"""
        return {
            "SECRET_KEY": self.flask_secret_key,
            "HOST": self.flask_host,
            "PORT": self.flask_port,
            "DEBUG": self.flask_debug
        }

    def __repr__(self):
        """String representation of configuration (without secrets)"""
        return (f"Config(radius_host={self.radius_host}, "
                f"radius_auth_port={self.radius_auth_port}, "
                f"radius_acct_port={self.radius_acct_port}, "
                f"bandwidth_limit={self.default_bandwidth_limit_mb}MB, "
                f"monitoring_interval={self.monitoring_interval_seconds}s)")


def setup_logging(config: Config):
    """
    Setup logging configuration
    
    Args:
        config: Configuration object
    """
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.log_file),
            logging.StreamHandler()
        ]
    )
    
    logger.info(f"Logging configured with level {config.log_level}")