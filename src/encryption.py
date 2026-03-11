"""
Network Encryption Module for NCUK WiFi Capping System

This module handles all encryption-related functionality including:
- WPA2/WPA3 configuration
- Certificate management
- Encryption policy enforcement
- Security protocols
"""

import hashlib
import secrets
from enum import Enum
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

logger = logging.getLogger(__name__)


class EncryptionType(Enum):
    """Supported WiFi encryption types."""
    OPEN = "open"
    WEP = "wep"
    WPA_PSK = "wpa-psk"
    WPA2_PSK = "wpa2-psk"
    WPA3_PSK = "wpa3-psk"
    WPA_ENTERPRISE = "wpa-enterprise"
    WPA2_ENTERPRISE = "wpa2-enterprise"
    WPA3_ENTERPRISE = "wpa3-enterprise"


class SecurityLevel(Enum):
    """Security levels for network access."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ENTERPRISE = "enterprise"


class NetworkEncryption:
    """Manages network encryption policies and configurations."""
    
    def __init__(self):
        self.encryption_policies = {}
        self.certificates = {}
        self._master_key = None
        self._initialize_master_key()
    
    def _initialize_master_key(self):
        """Initialize the master encryption key."""
        # In production, this should be loaded from secure storage
        password = b"ncuk_wifi_system_master_key_2024"
        salt = b"ncuk_salt_12345678"  # Should be random in production
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self._master_key = Fernet(key)
        logger.info("Master encryption key initialized")
    
    def generate_psk(self, ssid: str, length: int = 32) -> str:
        """Generate a secure Pre-Shared Key for WPA/WPA2/WPA3."""
        if length < 8 or length > 63:
            raise ValueError("PSK length must be between 8 and 63 characters")
        
        # Generate cryptographically secure random key
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        psk = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        logger.info(f"Generated PSK for SSID: {ssid}")
        return psk
    
    def create_encryption_policy(self, 
                                network_id: str,
                                encryption_type: EncryptionType,
                                security_level: SecurityLevel,
                                **kwargs) -> Dict:
        """Create a new encryption policy for a network."""
        policy = {
            "network_id": network_id,
            "encryption_type": encryption_type.value,
            "security_level": security_level.value,
            "created_at": self._get_timestamp(),
            "enabled": True,
            "settings": {}
        }
        
        # Configure settings based on encryption type
        if encryption_type in [EncryptionType.WPA_PSK, EncryptionType.WPA2_PSK, EncryptionType.WPA3_PSK]:
            policy["settings"] = {
                "psk": kwargs.get("psk") or self.generate_psk(network_id),
                "group_cipher": kwargs.get("group_cipher", "CCMP"),
                "pairwise_cipher": kwargs.get("pairwise_cipher", "CCMP"),
                "key_mgmt": self._get_key_management(encryption_type),
                "pmf": kwargs.get("pmf", "optional" if encryption_type != EncryptionType.WPA3_PSK else "required")
            }
        elif encryption_type in [EncryptionType.WPA_ENTERPRISE, EncryptionType.WPA2_ENTERPRISE, EncryptionType.WPA3_ENTERPRISE]:
            policy["settings"] = {
                "radius_server": kwargs.get("radius_server"),
                "radius_port": kwargs.get("radius_port", 1812),
                "radius_secret": kwargs.get("radius_secret"),
                "key_mgmt": self._get_key_management(encryption_type),
                "eap_method": kwargs.get("eap_method", "PEAP"),
                "pmf": kwargs.get("pmf", "optional" if encryption_type != EncryptionType.WPA3_ENTERPRISE else "required")
            }
        
        # Add security level specific settings
        if security_level == SecurityLevel.HIGH or security_level == SecurityLevel.ENTERPRISE:
            policy["settings"]["group_rekey"] = kwargs.get("group_rekey", 600)  # 10 minutes
            policy["settings"]["strict_rekey"] = True
            policy["settings"]["disable_pmksa_caching"] = True
        
        self.encryption_policies[network_id] = policy
        logger.info(f"Created encryption policy for network: {network_id} with {encryption_type.value}")
        return policy
    
    def _get_key_management(self, encryption_type: EncryptionType) -> str:
        """Get the appropriate key management protocol."""
        key_mgmt_map = {
            EncryptionType.WPA_PSK: "WPA-PSK",
            EncryptionType.WPA2_PSK: "WPA-PSK",
            EncryptionType.WPA3_PSK: "SAE",
            EncryptionType.WPA_ENTERPRISE: "WPA-EAP",
            EncryptionType.WPA2_ENTERPRISE: "WPA-EAP",
            EncryptionType.WPA3_ENTERPRISE: "WPA-EAP-SUITE-B-192"
        }
        return key_mgmt_map.get(encryption_type, "NONE")
    
    def validate_encryption_policy(self, policy: Dict) -> bool:
        """Validate an encryption policy configuration."""
        required_fields = ["network_id", "encryption_type", "security_level"]
        
        for field in required_fields:
            if field not in policy:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate encryption type
        try:
            encryption_type = EncryptionType(policy["encryption_type"])
        except ValueError:
            logger.error(f"Invalid encryption type: {policy['encryption_type']}")
            return False
        
        # Validate PSK for PSK-based networks
        if encryption_type in [EncryptionType.WPA_PSK, EncryptionType.WPA2_PSK, EncryptionType.WPA3_PSK]:
            psk = policy.get("settings", {}).get("psk")
            if not psk or len(psk) < 8 or len(psk) > 63:
                logger.error("PSK must be between 8 and 63 characters")
                return False
        
        # Validate enterprise settings
        elif encryption_type in [EncryptionType.WPA_ENTERPRISE, EncryptionType.WPA2_ENTERPRISE, EncryptionType.WPA3_ENTERPRISE]:
            settings = policy.get("settings", {})
            if not settings.get("radius_server") or not settings.get("radius_secret"):
                logger.error("RADIUS server and secret required for enterprise networks")
                return False
        
        logger.info(f"Encryption policy validation passed for network: {policy['network_id']}")
        return True
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using the master key."""
        encrypted_data = self._master_key.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data using the master key."""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self._master_key.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    def get_policy(self, network_id: str) -> Optional[Dict]:
        """Retrieve an encryption policy by network ID."""
        return self.encryption_policies.get(network_id)
    
    def update_policy(self, network_id: str, updates: Dict) -> bool:
        """Update an existing encryption policy."""
        if network_id not in self.encryption_policies:
            logger.error(f"Network policy not found: {network_id}")
            return False
        
        policy = self.encryption_policies[network_id].copy()
        policy.update(updates)
        policy["updated_at"] = self._get_timestamp()
        
        if self.validate_encryption_policy(policy):
            self.encryption_policies[network_id] = policy
            logger.info(f"Updated encryption policy for network: {network_id}")
            return True
        
        return False
    
    def delete_policy(self, network_id: str) -> bool:
        """Delete an encryption policy."""
        if network_id in self.encryption_policies:
            del self.encryption_policies[network_id]
            logger.info(f"Deleted encryption policy for network: {network_id}")
            return True
        
        logger.warning(f"Attempted to delete non-existent policy: {network_id}")
        return False
    
    def list_policies(self) -> List[Dict]:
        """List all encryption policies."""
        return list(self.encryption_policies.values())
    
    def generate_hostapd_config(self, network_id: str) -> Optional[str]:
        """Generate hostapd configuration for a network."""
        policy = self.get_policy(network_id)
        if not policy:
            return None
        
        encryption_type = EncryptionType(policy["encryption_type"])
        settings = policy["settings"]
        
        config_lines = [
            f"# Configuration for network: {network_id}",
            f"interface=wlan0",
            f"ssid={network_id}",
            f"hw_mode=g",
            f"channel=6",
            f"macaddr_acl=0",
            f"auth_algs=1",
        ]
        
        if encryption_type == EncryptionType.OPEN:
            config_lines.append("# Open network - no encryption")
        
        elif encryption_type in [EncryptionType.WPA_PSK, EncryptionType.WPA2_PSK, EncryptionType.WPA3_PSK]:
            config_lines.extend([
                f"wpa=2",
                f"wpa_passphrase={settings['psk']}",
                f"wpa_key_mgmt={settings['key_mgmt']}",
                f"wpa_pairwise={settings['pairwise_cipher']}",
                f"rsn_pairwise={settings['pairwise_cipher']}",
            ])
            
            if encryption_type == EncryptionType.WPA3_PSK:
                config_lines.extend([
                    "ieee80211w=2",  # PMF required for WPA3
                    "sae_require_mfp=1"
                ])
        
        elif encryption_type in [EncryptionType.WPA_ENTERPRISE, EncryptionType.WPA2_ENTERPRISE, EncryptionType.WPA3_ENTERPRISE]:
            config_lines.extend([
                f"wpa=2",
                f"wpa_key_mgmt={settings['key_mgmt']}",
                f"auth_server_addr={settings['radius_server']}",
                f"auth_server_port={settings['radius_port']}",
                f"auth_server_shared_secret={settings['radius_secret']}",
            ])
        
        return "\n".join(config_lines)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().isoformat()


def get_recommended_encryption_type(security_level: SecurityLevel) -> EncryptionType:
    """Get recommended encryption type based on security level."""
    recommendations = {
        SecurityLevel.LOW: EncryptionType.WPA2_PSK,
        SecurityLevel.MEDIUM: EncryptionType.WPA3_PSK,
        SecurityLevel.HIGH: EncryptionType.WPA3_PSK,
        SecurityLevel.ENTERPRISE: EncryptionType.WPA3_ENTERPRISE
    }
    return recommendations.get(security_level, EncryptionType.WPA2_PSK)