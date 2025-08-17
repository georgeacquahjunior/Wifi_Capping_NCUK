"""
Security utilities for WiFi Capping system
Handles credential validation, encryption, and secure communication
"""

import hashlib
import hmac
import secrets
import re
import logging
from typing import Optional
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2


logger = logging.getLogger(__name__)


def validate_credentials(username: str, password: str) -> bool:
    """
    Validate username and password format
    
    Args:
        username: Username to validate
        password: Password to validate
        
    Returns:
        bool: True if credentials meet security requirements
    """
    if not username or not password:
        return False
        
    # Username validation
    if len(username) < 3 or len(username) > 50:
        return False
        
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        return False
        
    # Password validation
    if len(password) < 6:
        return False
        
    return True


def hash_password(password: str, salt: Optional[bytes] = None) -> tuple:
    """
    Hash password using PBKDF2 with SHA-256
    
    Args:
        password: Plain text password
        salt: Optional salt (generated if not provided)
        
    Returns:
        tuple: (hashed_password, salt)
    """
    if salt is None:
        salt = get_random_bytes(32)
        
    # Use PBKDF2 with 100,000 iterations for strong security
    hashed = PBKDF2(password, salt, 32, count=100000)
    
    return hashed, salt


def verify_password(password: str, hashed_password: bytes, salt: bytes) -> bool:
    """
    Verify password against hash
    
    Args:
        password: Plain text password to verify
        hashed_password: Stored hash
        salt: Salt used for hashing
        
    Returns:
        bool: True if password matches
    """
    test_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(hashed_password, test_hash)


def encrypt_password(password: str) -> str:
    """
    Encrypt password for secure transmission
    Note: This is basic encryption - in production, use proper PKI
    
    Args:
        password: Plain text password
        
    Returns:
        str: Encrypted password (hex encoded)
    """
    # Generate a random key and IV for this encryption
    key = get_random_bytes(32)  # 256-bit key
    iv = get_random_bytes(16)   # 128-bit IV
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Pad password to multiple of 16 bytes
    padded_password = _pad_data(password.encode('utf-8'))
    
    # Encrypt password
    encrypted = cipher.encrypt(padded_password)
    
    # Return concatenated key + iv + encrypted data (hex encoded)
    return (key + iv + encrypted).hex()


def decrypt_password(encrypted_hex: str) -> str:
    """
    Decrypt password from hex string
    
    Args:
        encrypted_hex: Hex encoded encrypted password
        
    Returns:
        str: Decrypted password
    """
    try:
        encrypted_data = bytes.fromhex(encrypted_hex)
        
        # Extract key, IV, and encrypted data
        key = encrypted_data[:32]
        iv = encrypted_data[32:48]
        encrypted = encrypted_data[48:]
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted)
        
        # Remove padding
        unpadded = _unpad_data(decrypted)
        
        return unpadded.decode('utf-8')
        
    except Exception as e:
        logger.error(f"Password decryption failed: {str(e)}")
        raise ValueError("Invalid encrypted password")


def _pad_data(data: bytes) -> bytes:
    """Pad data to multiple of 16 bytes using PKCS7"""
    padding_length = 16 - (len(data) % 16)
    padding = bytes([padding_length]) * padding_length
    return data + padding


def _unpad_data(data: bytes) -> bytes:
    """Remove PKCS7 padding"""
    padding_length = data[-1]
    return data[:-padding_length]


def generate_session_id() -> str:
    """
    Generate a secure random session ID
    
    Returns:
        str: Cryptographically secure session ID
    """
    return secrets.token_hex(16)


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure secret key
    
    Args:
        length: Length of the key in bytes
        
    Returns:
        str: Hex encoded secret key
    """
    return secrets.token_hex(length)


def validate_ip_address(ip: str) -> bool:
    """
    Validate IPv4 address format
    
    Args:
        ip: IP address string
        
    Returns:
        bool: True if valid IPv4 address
    """
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
        
    # Check each octet is in valid range
    octets = ip.split('.')
    for octet in octets:
        if not (0 <= int(octet) <= 255):
            return False
            
    return True


def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        input_str: Input string to sanitize
        
    Returns:
        str: Sanitized string
    """
    if not input_str:
        return ""
        
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';\\&|`$]', '', input_str)
    
    # Limit length
    return sanitized[:100]


def create_message_signature(message: str, secret_key: str) -> str:
    """
    Create HMAC signature for message integrity
    
    Args:
        message: Message to sign
        secret_key: Secret key for signing
        
    Returns:
        str: Hex encoded HMAC signature
    """
    return hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def verify_message_signature(message: str, signature: str, secret_key: str) -> bool:
    """
    Verify HMAC signature
    
    Args:
        message: Original message
        signature: Signature to verify
        secret_key: Secret key used for signing
        
    Returns:
        bool: True if signature is valid
    """
    expected_signature = create_message_signature(message, secret_key)
    return hmac.compare_digest(signature, expected_signature)