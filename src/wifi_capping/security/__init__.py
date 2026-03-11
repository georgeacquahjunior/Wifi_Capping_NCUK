"""
Security module for encryption, authentication, and secure communications.
"""

import hashlib
import secrets
import base64
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.x509.oid import NameOID
from cryptography import x509
import jwt
import bcrypt

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Manages encryption and decryption operations."""
    
    def __init__(self, encryption_key: str = None):
        """Initialize with encryption key."""
        if encryption_key:
            self.fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        else:
            self.fernet = Fernet(Fernet.generate_key())
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data."""
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data."""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """Encrypt dictionary data as JSON."""
        import json
        json_data = json.dumps(data)
        return self.encrypt(json_data)
    
    def decrypt_dict(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt dictionary data from JSON."""
        import json
        json_data = self.decrypt(encrypted_data)
        return json.loads(json_data)


class PasswordManager:
    """Manages password hashing and verification."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate a secure random password."""
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))


class TokenManager:
    """Manages JWT tokens for authentication."""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def generate_token(self, user_id: str, roles: list = None, expires_in: int = 3600) -> str:
        """Generate JWT token."""
        payload = {
            'user_id': user_id,
            'roles': roles or [],
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(16)  # JWT ID for revocation
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None


class CertificateManager:
    """Manages SSL/TLS certificates."""
    
    @staticmethod
    def generate_self_signed_cert(
        hostname: str,
        key_size: int = 2048,
        validity_days: int = 365
    ) -> Tuple[bytes, bytes]:
        """Generate self-signed certificate and private key."""
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "GB"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "England"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "London"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "NCUK"),
            x509.NameAttribute(NameOID.COMMON_NAME, hostname),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=validity_days)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(hostname),
                x509.DNSName(f"*.{hostname}"),
                x509.DNSName("localhost"),
                x509.IPAddress("127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Serialize certificate and key
        cert_pem = cert.public_bytes(serialization.Encoding.PEM)
        key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return cert_pem, key_pem
    
    @staticmethod
    def save_cert_and_key(cert_pem: bytes, key_pem: bytes, cert_path: str, key_path: str):
        """Save certificate and key to files."""
        import os
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(cert_path), exist_ok=True)
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        
        # Write certificate
        with open(cert_path, 'wb') as f:
            f.write(cert_pem)
        
        # Write private key with restricted permissions
        with open(key_path, 'wb') as f:
            f.write(key_pem)
        os.chmod(key_path, 0o600)  # Owner read/write only


class SecurityValidator:
    """Validates security configurations and settings."""
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength."""
        issues = []
        score = 0
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        elif len(password) >= 12:
            score += 2
        else:
            score += 1
        
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        else:
            score += 1
        
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        else:
            score += 1
        
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one digit")
        else:
            score += 1
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("Password must contain at least one special character")
        else:
            score += 1
        
        strength = "Weak"
        if score >= 5:
            strength = "Strong"
        elif score >= 3:
            strength = "Medium"
        
        return {
            'valid': len(issues) == 0,
            'strength': strength,
            'score': score,
            'issues': issues
        }
    
    @staticmethod
    def validate_encryption_key(key: str) -> bool:
        """Validate encryption key format."""
        try:
            # Try to create a Fernet instance with the key
            Fernet(key.encode() if isinstance(key, str) else key)
            return True
        except Exception:
            return False
    
    @staticmethod
    def generate_security_report() -> Dict[str, Any]:
        """Generate comprehensive security report."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'encryption_available': True,
            'ssl_support': True,
            'password_hashing': 'bcrypt',
            'token_algorithm': 'HS256',
            'recommendations': [
                'Use strong passwords (12+ characters with mixed case, numbers, symbols)',
                'Enable SSL/TLS for all communications',
                'Regularly rotate encryption keys',
                'Monitor authentication logs for suspicious activity',
                'Implement rate limiting for login attempts'
            ]
        }