"""
Simple test script for WiFi Capping System core functionality
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_encryption():
    """Test encryption functionality."""
    print("Testing encryption module...")
    
    from encryption import NetworkEncryption, EncryptionType, SecurityLevel
    
    encryption = NetworkEncryption()
    
    # Test PSK generation
    psk = encryption.generate_psk("TestNetwork", 16)
    assert len(psk) == 16, f"Expected PSK length 16, got {len(psk)}"
    print("✓ PSK generation working")
    
    # Test policy creation
    policy = encryption.create_encryption_policy(
        network_id="TestNetwork",
        encryption_type=EncryptionType.WPA3_PSK,
        security_level=SecurityLevel.HIGH
    )
    assert policy["network_id"] == "TestNetwork"
    assert policy["encryption_type"] == "wpa3-psk"
    print("✓ Encryption policy creation working")
    
    # Test hostapd config generation
    config = encryption.generate_hostapd_config("TestNetwork")
    assert config is not None
    assert "ssid=TestNetwork" in config
    print("✓ Hostapd config generation working")
    
    print("Encryption module tests passed!\n")


def test_access_control():
    """Test access control functionality."""
    print("Testing access control module...")
    
    from access_control import AccessControl, UserRole, AccessLevel
    
    access_control = AccessControl()
    
    # Test user creation
    user = access_control.create_user(
        username="testuser",
        email="test@ncuk.edu",
        role=UserRole.STUDENT,
        access_level=AccessLevel.BASIC,
        mac_addresses=["AA:BB:CC:DD:EE:FF"],
        password="testpassword123"
    )
    assert user.username == "testuser"
    assert user.role == UserRole.STUDENT
    print("✓ User creation working")
    
    # Test authentication
    authenticated_user = access_control.authenticate_user("testuser", "testpassword123")
    assert authenticated_user is not None
    assert authenticated_user.username == "testuser"
    print("✓ User authentication working")
    
    # Test MAC authorization
    authorized = access_control.authorize_mac_address("AA:BB:CC:DD:EE:FF", user.user_id)
    assert authorized == True
    print("✓ MAC address authorization working")
    
    # Test guest access creation
    guest_credentials = access_control.create_guest_access(duration_hours=12)
    assert "username" in guest_credentials
    assert "password" in guest_credentials
    print("✓ Guest access creation working")
    
    print("Access control module tests passed!\n")


def test_system_integration():
    """Test system integration."""
    print("Testing system integration...")
    
    from encryption import NetworkEncryption, EncryptionType, SecurityLevel
    from access_control import AccessControl, UserRole, AccessLevel
    
    # Initialize components
    encryption = NetworkEncryption()
    access_control = AccessControl()
    
    # Create network policy
    network_policy = encryption.create_encryption_policy(
        network_id="IntegrationTest",
        encryption_type=EncryptionType.WPA2_PSK,
        security_level=SecurityLevel.MEDIUM
    )
    
    # Create user
    user = access_control.create_user(
        username="integration.test",
        email="integration@ncuk.edu",
        role=UserRole.FACULTY,
        mac_addresses=["FF:FF:FF:FF:FF:FF"]
    )
    
    # Test authorization
    authorized = access_control.authorize_mac_address("FF:FF:FF:FF:FF:FF", user.user_id)
    
    assert network_policy is not None
    assert user is not None
    assert authorized == True
    
    print("✓ System integration working")
    print("System integration tests passed!\n")


def main():
    """Run all tests."""
    print("=" * 50)
    print("WiFi Capping System - Core Functionality Tests")
    print("=" * 50)
    print()
    
    try:
        test_encryption()
        test_access_control()
        test_system_integration()
        
        print("=" * 50)
        print("ALL TESTS PASSED! ✓")
        print("=" * 50)
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())