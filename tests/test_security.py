"""
Basic security tests for the WiFi Capping system.
"""

import pytest
import tempfile
import os
from datetime import datetime

from wifi_capping.security import (
    EncryptionManager, PasswordManager, TokenManager, 
    SecurityValidator, CertificateManager
)
from wifi_capping.core.config import DevelopmentConfig, ProductionConfig


class TestEncryption:
    """Test encryption functionality."""
    
    def test_encryption_manager_basic(self):
        """Test basic encryption/decryption."""
        manager = EncryptionManager()
        test_data = "This is test data"
        
        encrypted = manager.encrypt(test_data)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == test_data
    
    def test_encryption_manager_dict(self):
        """Test dictionary encryption."""
        manager = EncryptionManager()
        test_dict = {'user': 'test', 'password': 'secret', 'role': 'admin'}
        
        encrypted = manager.encrypt_dict(test_dict)
        decrypted = manager.decrypt_dict(encrypted)
        
        assert decrypted == test_dict


class TestPasswordSecurity:
    """Test password security features."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "TestPassword123!"
        
        hashed = PasswordManager.hash_password(password)
        assert PasswordManager.verify_password(password, hashed)
        assert not PasswordManager.verify_password("wrong", hashed)
    
    def test_password_generation(self):
        """Test secure password generation."""
        password = PasswordManager.generate_secure_password(16)
        
        assert len(password) == 16
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)
    
    def test_password_strength_validation(self):
        """Test password strength validation."""
        # Strong password
        strong_result = SecurityValidator.validate_password_strength("StrongP@ssw0rd123")
        assert strong_result['valid']
        assert strong_result['strength'] == 'Strong'
        
        # Weak password
        weak_result = SecurityValidator.validate_password_strength("weak")
        assert not weak_result['valid']
        assert len(weak_result['issues']) > 0


class TestTokenSecurity:
    """Test JWT token functionality."""
    
    def test_token_generation_verification(self):
        """Test token generation and verification."""
        secret_key = "test_secret_key_12345"
        manager = TokenManager(secret_key)
        
        token = manager.generate_token("user123", ["admin", "user"])
        payload = manager.verify_token(token)
        
        assert payload is not None
        assert payload['user_id'] == "user123"
        assert "admin" in payload['roles']
    
    def test_token_expiration(self):
        """Test token expiration."""
        secret_key = "test_secret_key_12345"
        manager = TokenManager(secret_key)
        
        # Generate token with 1 second expiration
        token = manager.generate_token("user123", expires_in=1)
        
        import time
        time.sleep(2)
        
        payload = manager.verify_token(token)
        assert payload is None  # Should be expired


class TestCertificates:
    """Test SSL certificate functionality."""
    
    def test_self_signed_certificate_generation(self):
        """Test self-signed certificate generation."""
        cert_pem, key_pem = CertificateManager.generate_self_signed_cert("test.example.com")
        
        assert b'-----BEGIN CERTIFICATE-----' in cert_pem
        assert b'-----BEGIN PRIVATE KEY-----' in key_pem
    
    def test_certificate_file_operations(self):
        """Test certificate and key file operations."""
        cert_pem, key_pem = CertificateManager.generate_self_signed_cert("test.example.com")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cert_path = os.path.join(temp_dir, "test.crt")
            key_path = os.path.join(temp_dir, "test.key")
            
            CertificateManager.save_cert_and_key(cert_pem, key_pem, cert_path, key_path)
            
            assert os.path.exists(cert_path)
            assert os.path.exists(key_path)
            
            # Check key file permissions (owner read/write only)
            key_stat = os.stat(key_path)
            assert oct(key_stat.st_mode)[-3:] == '600'


class TestConfiguration:
    """Test configuration security validation."""
    
    def test_development_config_validation(self):
        """Test development configuration validation."""
        result = DevelopmentConfig.validate_security_config()
        
        # Development config should have warnings but be valid
        assert 'warnings' in result
    
    def test_production_config_validation(self):
        """Test production configuration validation."""
        result = ProductionConfig.validate_production_config()
        
        # Check that validation runs without errors
        assert 'valid' in result
        assert 'issues' in result
        assert 'warnings' in result
    
    def test_security_validator_report(self):
        """Test security report generation."""
        report = SecurityValidator.generate_security_report()
        
        assert 'timestamp' in report
        assert 'encryption_available' in report
        assert 'recommendations' in report
        assert len(report['recommendations']) > 0


if __name__ == '__main__':
    pytest.main([__file__])