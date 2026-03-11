#!/usr/bin/env python3
"""
WiFi Capping NCUK - Main application entry point
A secure WiFi bandwidth management system for NCUK institutions.
"""

import os
import sys
import logging
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from wifi_capping.core.app import create_app
from wifi_capping.core.config import get_config


def main():
    """Main application entry point."""
    print("WiFi Capping NCUK - Secure Bandwidth Management System")
    print("=" * 60)
    
    # Get configuration
    config_name = os.environ.get('FLASK_ENV', 'development')
    config = get_config(config_name)
    
    print(f"Environment: {config_name}")
    print(f"SSL Required: {config.SSL_REQUIRED}")
    print(f"AUP Enabled: {config.AUP_ENABLED}")
    print(f"Database Encryption: {config.DATABASE_ENCRYPTION}")
    
    # Validate security configuration
    validation = config.validate_security_config()
    
    if not validation['valid']:
        print("\n❌ Security Configuration Issues:")
        for issue in validation['issues']:
            print(f"  - {issue}")
        print("\nPlease fix these issues before starting the application.")
        return 1
    
    if validation['warnings']:
        print("\n⚠️  Security Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    # Production-specific validation
    if config_name == 'production':
        from wifi_capping.core.config import ProductionConfig
        prod_validation = ProductionConfig.validate_production_config()
        
        if not prod_validation['valid']:
            print("\n❌ Production Configuration Issues:")
            for issue in prod_validation['issues']:
                print(f"  - {issue}")
            return 1
    
    print("\n✅ Security configuration validated successfully!")
    
    # Create application
    try:
        app = create_app(config_name)
        print(f"✅ Application created successfully")
        
        # Display security report
        from wifi_capping.security import SecurityValidator
        security_report = SecurityValidator.generate_security_report()
        
        print(f"\n📊 Security Report:")
        print(f"  - Encryption: Available")
        print(f"  - SSL Support: Available")
        print(f"  - Password Hashing: {security_report['password_hashing']}")
        print(f"  - Token Algorithm: {security_report['token_algorithm']}")
        
        # Display policy summary
        policy_summary = app.policy_engine.get_policy_summary()
        print(f"\n📋 Policy Summary:")
        print(f"  - Total Policies: {policy_summary['total_policies']}")
        print(f"  - Enabled Policies: {policy_summary['enabled_policies']}")
        print(f"  - User Groups: {policy_summary['user_groups']}")
        
        # Display AUP status
        aup_policy = app.aup_policy_manager.get_active_policy()
        if aup_policy:
            print(f"\n📜 AUP Policy Active: {aup_policy.name} v{aup_policy.version}")
        
        print(f"\n🚀 Starting server on port {config.MONITORING_PORT}")
        
        # Start the application
        if config.SSL_REQUIRED and os.path.exists(config.SSL_CERT_PATH):
            app.run(
                host='0.0.0.0',
                port=config.MONITORING_PORT,
                ssl_context=(config.SSL_CERT_PATH, config.SSL_KEY_PATH),
                debug=(config_name == 'development')
            )
        else:
            app.run(
                host='0.0.0.0',
                port=config.MONITORING_PORT,
                debug=(config_name == 'development')
            )
            
    except Exception as e:
        print(f"\n❌ Failed to start application: {e}")
        logging.exception("Application startup failed")
        return 1
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)