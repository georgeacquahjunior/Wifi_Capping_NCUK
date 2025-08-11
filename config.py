import os
from urllib.parse import urlparse

class DatabaseConfig:
    """Database configuration helper class"""
    
    @staticmethod
    def get_database_uri(environment='development'):
        """Get database URI based on environment"""
        # Check for explicit database URL first
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            return DatabaseConfig._validate_database_url(database_url)
        
        # Environment-specific database configuration
        if environment == 'production':
            return DatabaseConfig._get_production_database_uri()
        elif environment == 'testing':
            return 'sqlite:///:memory:'  # In-memory database for testing
        else:  # development
            return DatabaseConfig._get_development_database_uri()
    
    @staticmethod
    def _get_development_database_uri():
        """Get development database URI"""
        db_path = os.environ.get('DEV_DATABASE_PATH', 'students.db')
        # Create directory if path contains a directory component
        if os.path.dirname(db_path):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return f'sqlite:///{db_path}'
    
    @staticmethod
    def _get_production_database_uri():
        """Get production database URI with PostgreSQL support"""
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        db_name = os.environ.get('DB_NAME', 'wifi_capping')
        db_user = os.environ.get('DB_USER', 'postgres')
        db_password = os.environ.get('DB_PASSWORD', '')
        
        if db_password:
            return f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        else:
            # Fallback to SQLite if no PostgreSQL credentials provided
            db_path = os.environ.get('PROD_DATABASE_PATH', 'instance/students_prod.db')
            # Only create directories if we have write permission
            try:
                os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else 'instance', exist_ok=True)
            except PermissionError:
                # Use current directory if can't create the specified path
                db_path = 'students_prod.db'
            return f'sqlite:///{db_path}'
    
    @staticmethod
    def _validate_database_url(url):
        """Validate and normalize database URL"""
        try:
            parsed = urlparse(url)
            if parsed.scheme in ['sqlite', 'postgresql', 'mysql']:
                return url
            else:
                raise ValueError(f"Unsupported database scheme: {parsed.scheme}")
        except Exception as e:
            raise ValueError(f"Invalid database URL: {e}")

class Config:
    """Base configuration class"""
    # Secret key for JWT encoding/decoding
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    
    # Database configuration - will be set dynamically
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Add connection pool settings for production databases (PostgreSQL/MySQL)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 20,
        'pool_recycle': 300,  # Recycle connections every 5 minutes
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20
    }

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}