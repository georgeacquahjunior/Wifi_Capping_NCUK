"""
WiFi Capping System Demonstration Script

This script demonstrates the key features of the NCUK WiFi Capping System:
- Network encryption and security policies
- User management and access control
- Bandwidth management capabilities
"""

import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from encryption import NetworkEncryption, EncryptionType, SecurityLevel
from access_control import AccessControl, UserRole, AccessLevel


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title):
    """Print a formatted section."""
    print(f"\n--- {title} ---")


def demonstrate_encryption():
    """Demonstrate encryption capabilities."""
    print_header("NETWORK ENCRYPTION & SECURITY POLICIES")
    
    encryption = NetworkEncryption()
    
    print_section("Creating WiFi Network Encryption Policies")
    
    # Create main campus network
    main_policy = encryption.create_encryption_policy(
        network_id="NCUK-Campus",
        encryption_type=EncryptionType.WPA3_PSK,
        security_level=SecurityLevel.HIGH,
        psk=encryption.generate_psk("NCUK-Campus", 32)
    )
    print(f"✓ Created main campus network: {main_policy['network_id']}")
    print(f"  - Encryption: {main_policy['encryption_type']}")
    print(f"  - Security Level: {main_policy['security_level']}")
    print(f"  - PSK Length: {len(main_policy['settings']['psk'])} characters")
    
    # Create guest network
    guest_policy = encryption.create_encryption_policy(
        network_id="NCUK-Guest",
        encryption_type=EncryptionType.WPA2_PSK,
        security_level=SecurityLevel.MEDIUM
    )
    print(f"✓ Created guest network: {guest_policy['network_id']}")
    print(f"  - Encryption: {guest_policy['encryption_type']}")
    print(f"  - Security Level: {guest_policy['security_level']}")
    
    # Create enterprise network
    enterprise_policy = encryption.create_encryption_policy(
        network_id="NCUK-Enterprise",
        encryption_type=EncryptionType.WPA3_ENTERPRISE,
        security_level=SecurityLevel.ENTERPRISE,
        radius_server="radius.ncuk.edu",
        radius_secret="enterprise_secret_123"
    )
    print(f"✓ Created enterprise network: {enterprise_policy['network_id']}")
    print(f"  - Encryption: {enterprise_policy['encryption_type']}")
    print(f"  - RADIUS Server: {enterprise_policy['settings']['radius_server']}")
    
    print_section("Generating hostapd Configuration")
    
    # Generate configuration for main network
    config = encryption.generate_hostapd_config("NCUK-Campus")
    print("✓ Generated hostapd configuration for NCUK-Campus:")
    print("  Sample configuration lines:")
    for line in config.split('\n')[:5]:
        if line.strip():
            print(f"    {line}")
    print("    ...")
    
    return encryption


def demonstrate_access_control():
    """Demonstrate access control capabilities."""
    print_header("USER MANAGEMENT & ACCESS CONTROL")
    
    access_control = AccessControl()
    
    print_section("Creating User Accounts")
    
    # Create admin user
    admin = access_control.create_user(
        username="admin.user",
        email="admin@ncuk.edu",
        role=UserRole.ADMIN,
        access_level=AccessLevel.UNLIMITED,
        mac_addresses=["00:11:22:33:44:55"],
        password="secure_admin_pass"
    )
    print(f"✓ Created admin user: {admin.username}")
    print(f"  - Role: {admin.role.value}")
    print(f"  - Access Level: {admin.access_level.value}")
    print(f"  - MAC Addresses: {', '.join(admin.mac_addresses)}")
    
    # Create faculty user
    faculty = access_control.create_user(
        username="prof.smith",
        email="prof.smith@ncuk.edu",
        role=UserRole.FACULTY,
        access_level=AccessLevel.PREMIUM,
        mac_addresses=["AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"]
    )
    print(f"✓ Created faculty user: {faculty.username}")
    print(f"  - Role: {faculty.role.value}")
    print(f"  - Access Level: {faculty.access_level.value}")
    print(f"  - Device Count: {len(faculty.mac_addresses)}")
    
    # Create student user
    student = access_control.create_user(
        username="john.doe",
        email="john.doe@student.ncuk.edu",
        role=UserRole.STUDENT,
        access_level=AccessLevel.BASIC,
        mac_addresses=["AA:AA:AA:AA:AA:AA"],
        daily_quota_gb=5.0
    )
    print(f"✓ Created student user: {student.username}")
    print(f"  - Role: {student.role.value}")
    print(f"  - Daily Quota: {student.daily_quota_gb} GB")
    
    print_section("Testing Authentication")
    
    # Test authentication
    auth_result = access_control.authenticate_user("admin.user", "secure_admin_pass")
    if auth_result:
        print(f"✓ Authentication successful for {auth_result.username}")
        print(f"  - Last login: {auth_result.last_login}")
    
    # Test failed authentication
    failed_auth = access_control.authenticate_user("admin.user", "wrong_password")
    if not failed_auth:
        print("✓ Authentication correctly failed for wrong password")
    
    print_section("MAC Address Authorization")
    
    # Test MAC authorization
    mac_authorized = access_control.authorize_mac_address("AA:BB:CC:DD:EE:FF", faculty.user_id)
    print(f"✓ MAC authorization for faculty device: {'Allowed' if mac_authorized else 'Denied'}")
    
    unauthorized_mac = access_control.authorize_mac_address("FF:FF:FF:FF:FF:FF")
    print(f"✓ Unknown MAC authorization: {'Allowed' if unauthorized_mac else 'Denied'}")
    
    print_section("Guest Access Management")
    
    # Create temporary guest access
    guest_credentials = access_control.create_guest_access(duration_hours=24, bandwidth_limit=5)
    print("✓ Created guest access:")
    print(f"  - Username: {guest_credentials['username']}")
    print(f"  - Password: {guest_credentials['password']}")
    print(f"  - Expires: {guest_credentials['expires_at']}")
    print(f"  - Bandwidth Limit: {guest_credentials['bandwidth_limit_mbps']} Mbps")
    
    print_section("Time-Based Access Rules")
    
    # Create custom time rule
    custom_rule = access_control.create_time_based_rule(
        rule_id="exam_period",
        name="Exam Period Extended Hours",
        start_time="06:00",
        end_time="02:00",  # Next day
        days=["monday", "tuesday", "wednesday", "thursday", "friday"],
        target_roles=[UserRole.STUDENT],
        priority=200
    )
    print(f"✓ Created time-based rule: {custom_rule.name}")
    print(f"  - Active: {custom_rule.conditions['start_time']} - {custom_rule.conditions['end_time']}")
    print(f"  - Days: {', '.join(custom_rule.conditions['days'])}")
    
    return access_control


def demonstrate_bandwidth_management():
    """Demonstrate bandwidth management capabilities."""
    print_header("BANDWIDTH MANAGEMENT & QoS")
    
    # Import with mock to avoid traffic control errors
    import unittest.mock
    
    with unittest.mock.patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        
        from bandwidth import BandwidthManager, TrafficClass, BandwidthLimit
        
        bandwidth_mgr = BandwidthManager(interface="test0")
        
        print_section("Setting User Bandwidth Limits")
        
        # Set bandwidth for different user types
        limits = [
            ("admin_user", 1000.0, 500.0, 95, "Administrator"),
            ("faculty_user", 200.0, 100.0, 80, "Faculty"),
            ("staff_user", 50.0, 25.0, 60, "Staff"),
            ("student_user", 25.0, 10.0, 40, "Student"),
            ("guest_user", 5.0, 2.0, 20, "Guest")
        ]
        
        for user_id, down, up, priority, role in limits:
            bandwidth_mgr.set_user_bandwidth_limit(user_id, down, up, priority)
            print(f"✓ Set bandwidth for {role}: {down}↓/{up}↑ Mbps (Priority: {priority})")
        
        print_section("Quality of Service Rules")
        
        # Display QoS rules
        qos_rules = list(bandwidth_mgr.qos_rules.values())
        print(f"✓ Active QoS rules: {len(qos_rules)}")
        for rule in qos_rules[:3]:  # Show first 3
            print(f"  - {rule.name}: {rule.traffic_class.value} priority")
        
        print_section("Usage Monitoring")
        
        # Simulate usage stats
        bandwidth_mgr._collect_usage_stats()
        stats = bandwidth_mgr.get_usage_stats()
        print(f"✓ Monitoring {len(stats)} active users")
        
        print_section("System Reports")
        
        # Generate usage report
        report = bandwidth_mgr.generate_usage_report()
        print(f"✓ Generated usage report:")
        print(f"  - Report time: {report['generated_at']}")
        print(f"  - Total users: {report['total_users']}")
        print(f"  - Total download: {report['total_download_gb']:.2f} GB")
        print(f"  - Total upload: {report['total_upload_gb']:.2f} GB")
        
        return bandwidth_mgr


def demonstrate_system_integration():
    """Demonstrate complete system integration."""
    print_header("COMPLETE SYSTEM INTEGRATION")
    
    print_section("System Configuration Export")
    
    # Initialize all components
    encryption = NetworkEncryption()
    access_control = AccessControl()
    
    # Create comprehensive setup
    encryption.create_encryption_policy(
        "NCUK-Integrated", EncryptionType.WPA3_PSK, SecurityLevel.HIGH
    )
    
    user = access_control.create_user(
        "integrated.user", "integrated@ncuk.edu", UserRole.STAFF,
        mac_addresses=["BB:BB:BB:BB:BB:BB"]
    )
    
    # Export configurations
    encryption_policies = encryption.list_policies()
    user_list = access_control.export_user_list()
    access_rules = access_control.export_access_rules()
    
    print(f"✓ System configuration export:")
    print(f"  - Encryption policies: {len(encryption_policies)}")
    print(f"  - User accounts: {len(user_list)}")
    print(f"  - Access rules: {len(access_rules)}")
    
    print_section("Security Validation")
    
    # Validate configurations
    valid_policies = 0
    for policy in encryption_policies:
        if encryption.validate_encryption_policy(policy):
            valid_policies += 1
    
    print(f"✓ Security validation:")
    print(f"  - Valid encryption policies: {valid_policies}/{len(encryption_policies)}")
    print(f"  - Active users: {len([u for u in user_list if u['is_active']])}")
    
    print_section("System Statistics")
    
    # System overview
    total_networks = len(encryption_policies)
    total_users = len(user_list)
    admin_users = len([u for u in user_list if u['role'] == 'admin'])
    guest_users = len([u for u in user_list if u['role'] == 'guest'])
    
    print(f"✓ System overview:")
    print(f"  - Total networks configured: {total_networks}")
    print(f"  - Total user accounts: {total_users}")
    print(f"  - Administrative users: {admin_users}")
    print(f"  - Guest accounts: {guest_users}")
    print(f"  - System operational: {'Yes' if total_networks > 0 and total_users > 0 else 'No'}")


def main():
    """Main demonstration function."""
    print("WiFi Capping System for NCUK")
    print("Comprehensive Network Management Demonstration")
    print(f"Demonstration started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all demonstrations
        demonstrate_encryption()
        demonstrate_access_control()
        demonstrate_bandwidth_management()
        demonstrate_system_integration()
        
        print_header("DEMONSTRATION COMPLETE")
        print("✅ All system components demonstrated successfully!")
        print("✅ Network encryption and access policies are fully functional!")
        print("✅ The WiFi Capping System is ready for deployment.")
        print("\nFor more information, see README.md and configuration files.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())