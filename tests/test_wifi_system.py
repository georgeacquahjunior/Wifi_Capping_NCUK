"""
Test Suite for NCUK WiFi Capping System

This module contains comprehensive tests for the encryption and access control functionality.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from encryption import NetworkEncryption, EncryptionType, SecurityLevel
from access_control import AccessControl, UserRole, AccessLevel, User
from bandwidth import BandwidthManager, TrafficClass, BandwidthLimit


class TestNetworkEncryption(unittest.TestCase):
    """Test cases for NetworkEncryption class."""
    
    def setUp(self):
        self.encryption = NetworkEncryption()
    
    def test_generate_psk(self):
        """Test PSK generation."""
        psk = self.encryption.generate_psk("TestNetwork", 16)
        self.assertEqual(len(psk), 16)
        
        # Test minimum length
        psk_min = self.encryption.generate_psk("TestNetwork", 8)
        self.assertEqual(len(psk_min), 8)
        
        # Test maximum length
        psk_max = self.encryption.generate_psk("TestNetwork", 63)
        self.assertEqual(len(psk_max), 63)
        
        # Test invalid length
        with self.assertRaises(ValueError):
            self.encryption.generate_psk("TestNetwork", 7)
        
        with self.assertRaises(ValueError):
            self.encryption.generate_psk("TestNetwork", 64)
    
    def test_create_encryption_policy(self):
        """Test encryption policy creation."""
        policy = self.encryption.create_encryption_policy(
            network_id="TestNetwork",
            encryption_type=EncryptionType.WPA3_PSK,
            security_level=SecurityLevel.HIGH
        )
        
        self.assertEqual(policy["network_id"], "TestNetwork")
        self.assertEqual(policy["encryption_type"], "wpa3-psk")
        self.assertEqual(policy["security_level"], "high")
        self.assertTrue(policy["enabled"])
        self.assertIn("psk", policy["settings"])
        self.assertIn("key_mgmt", policy["settings"])
    
    def test_validate_encryption_policy(self):
        """Test encryption policy validation."""
        # Valid policy
        valid_policy = {
            "network_id": "TestNetwork",
            "encryption_type": "wpa2-psk",
            "security_level": "medium",
            "settings": {"psk": "validpassword123"}
        }
        self.assertTrue(self.encryption.validate_encryption_policy(valid_policy))
        
        # Invalid policy - missing required field
        invalid_policy = {
            "network_id": "TestNetwork",
            "encryption_type": "wpa2-psk"
            # Missing security_level
        }
        self.assertFalse(self.encryption.validate_encryption_policy(invalid_policy))
        
        # Invalid policy - PSK too short
        invalid_psk_policy = {
            "network_id": "TestNetwork",
            "encryption_type": "wpa2-psk",
            "security_level": "medium",
            "settings": {"psk": "short"}
        }
        self.assertFalse(self.encryption.validate_encryption_policy(invalid_psk_policy))
    
    def test_encrypt_decrypt_sensitive_data(self):
        """Test data encryption and decryption."""
        original_data = "sensitive_password_123"
        encrypted = self.encryption.encrypt_sensitive_data(original_data)
        decrypted = self.encryption.decrypt_sensitive_data(encrypted)
        
        self.assertEqual(original_data, decrypted)
        self.assertNotEqual(original_data, encrypted)
    
    def test_hostapd_config_generation(self):
        """Test hostapd configuration generation."""
        # Create a WPA3 policy
        self.encryption.create_encryption_policy(
            network_id="TestWPA3",
            encryption_type=EncryptionType.WPA3_PSK,
            security_level=SecurityLevel.HIGH,
            psk="testpassword123"
        )
        
        config = self.encryption.generate_hostapd_config("TestWPA3")
        self.assertIsNotNone(config)
        self.assertIn("ssid=TestWPA3", config)
        self.assertIn("wpa=2", config)
        self.assertIn("ieee80211w=2", config)  # PMF required for WPA3
        
        # Test non-existent network
        config_none = self.encryption.generate_hostapd_config("NonExistent")
        self.assertIsNone(config_none)


class TestAccessControl(unittest.TestCase):
    """Test cases for AccessControl class."""
    
    def setUp(self):
        self.access_control = AccessControl()
    
    def test_create_user(self):
        """Test user creation."""
        user = self.access_control.create_user(
            username="testuser",
            email="test@ncuk.edu",
            role=UserRole.STUDENT,
            access_level=AccessLevel.BASIC,
            mac_addresses=["AA:BB:CC:DD:EE:FF"],
            password="testpassword123"
        )
        
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@ncuk.edu")
        self.assertEqual(user.role, UserRole.STUDENT)
        self.assertEqual(user.access_level, AccessLevel.BASIC)
        self.assertIn("AA:BB:CC:DD:EE:FF", user.mac_addresses)
        self.assertIsNotNone(user.password_hash)
        self.assertTrue(user.is_active)
    
    def test_authenticate_user(self):
        """Test user authentication."""
        # Create user
        self.access_control.create_user(
            username="authtest",
            email="auth@ncuk.edu",
            role=UserRole.STAFF,
            password="correctpassword"
        )
        
        # Test correct authentication
        user = self.access_control.authenticate_user("authtest", "correctpassword")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "authtest")
        
        # Test incorrect password
        user_wrong = self.access_control.authenticate_user("authtest", "wrongpassword")
        self.assertIsNone(user_wrong)
        
        # Test non-existent user
        user_none = self.access_control.authenticate_user("nonexistent", "password")
        self.assertIsNone(user_none)
    
    def test_mac_address_authorization(self):
        """Test MAC address authorization."""
        # Create user with MAC address
        user = self.access_control.create_user(
            username="mactest",
            email="mac@ncuk.edu",
            role=UserRole.STUDENT,
            mac_addresses=["11:22:33:44:55:66"]
        )
        
        # Test authorization for user's MAC
        authorized = self.access_control.authorize_mac_address("11:22:33:44:55:66", user.user_id)
        self.assertTrue(authorized)
        
        # Test authorization for unknown MAC
        unauthorized = self.access_control.authorize_mac_address("AA:AA:AA:AA:AA:AA")
        self.assertFalse(unauthorized)
    
    def test_mac_blacklist_whitelist(self):
        """Test MAC address blacklist and whitelist functionality."""
        test_mac = "BB:BB:BB:BB:BB:BB"
        
        # Add to whitelist
        self.assertTrue(self.access_control.add_mac_to_whitelist(test_mac))
        self.assertIn("BB:BB:BB:BB:BB:BB", self.access_control.mac_whitelist)
        
        # Add to blacklist (should remove from whitelist)
        self.assertTrue(self.access_control.add_mac_to_blacklist(test_mac))
        self.assertIn("BB:BB:BB:BB:BB:BB", self.access_control.mac_blacklist)
        self.assertNotIn("BB:BB:BB:BB:BB:BB", self.access_control.mac_whitelist)
        
        # Remove from blacklist
        self.assertTrue(self.access_control.remove_mac_from_blacklist(test_mac))
        self.assertNotIn("BB:BB:BB:BB:BB:BB", self.access_control.mac_blacklist)
    
    def test_guest_access_creation(self):
        """Test guest access creation."""
        guest_credentials = self.access_control.create_guest_access(duration_hours=12, bandwidth_limit=10)
        
        self.assertIn("username", guest_credentials)
        self.assertIn("password", guest_credentials)
        self.assertIn("expires_at", guest_credentials)
        self.assertEqual(guest_credentials["bandwidth_limit_mbps"], 10)
        
        # Verify guest user was created
        guest_username = guest_credentials["username"]
        guest_user = None
        for user in self.access_control.users.values():
            if user.username == guest_username:
                guest_user = user
                break
        
        self.assertIsNotNone(guest_user)
        self.assertEqual(guest_user.role, UserRole.GUEST)
    
    def test_time_based_access_rule(self):
        """Test time-based access rule creation."""
        rule = self.access_control.create_time_based_rule(
            rule_id="test_rule",
            name="Test Time Rule",
            start_time="09:00",
            end_time="17:00",
            days=["monday", "tuesday", "wednesday", "thursday", "friday"],
            target_roles=[UserRole.STUDENT],
            action="allow"
        )
        
        self.assertEqual(rule.rule_id, "test_rule")
        self.assertEqual(rule.name, "Test Time Rule")
        self.assertEqual(rule.rule_type, "time")
        self.assertTrue(rule.enabled)
        self.assertIn("start_time", rule.conditions)
        self.assertIn("end_time", rule.conditions)
        self.assertIn("days", rule.conditions)
    
    def test_user_deactivation_reactivation(self):
        """Test user deactivation and reactivation."""
        user = self.access_control.create_user(
            username="deactivatetest",
            email="deactivate@ncuk.edu",
            role=UserRole.STUDENT
        )
        
        user_id = user.user_id
        
        # Test deactivation
        self.assertTrue(self.access_control.deactivate_user(user_id))
        self.assertFalse(self.access_control.users[user_id].is_active)
        
        # Test reactivation
        self.assertTrue(self.access_control.reactivate_user(user_id))
        self.assertTrue(self.access_control.users[user_id].is_active)


class TestBandwidthManager(unittest.TestCase):
    """Test cases for BandwidthManager class."""
    
    def setUp(self):
        # Mock subprocess calls since we're testing
        self.patcher = patch('subprocess.run')
        self.mock_subprocess = self.patcher.start()
        self.mock_subprocess.return_value.returncode = 0
        
        self.bandwidth_manager = BandwidthManager(interface="test0")
    
    def tearDown(self):
        self.patcher.stop()
    
    def test_set_user_bandwidth_limit(self):
        """Test setting user bandwidth limits."""
        result = self.bandwidth_manager.set_user_bandwidth_limit(
            user_id="test_user",
            download_mbps=25.0,
            upload_mbps=10.0,
            priority=70
        )
        
        self.assertTrue(result)
        self.assertIn("test_user", self.bandwidth_manager.user_limits)
        
        limit = self.bandwidth_manager.get_user_bandwidth_limit("test_user")
        self.assertEqual(limit.download_mbps, 25.0)
        self.assertEqual(limit.upload_mbps, 10.0)
        self.assertEqual(limit.priority, 70)
    
    def test_remove_user_bandwidth_limit(self):
        """Test removing user bandwidth limits."""
        # First set a limit
        self.bandwidth_manager.set_user_bandwidth_limit("test_user", 10.0, 5.0)
        
        # Then remove it
        result = self.bandwidth_manager.remove_user_bandwidth_limit("test_user")
        self.assertTrue(result)
        self.assertNotIn("test_user", self.bandwidth_manager.user_limits)
    
    def test_qos_rule_creation(self):
        """Test QoS rule creation."""
        from bandwidth import Protocol
        
        bandwidth_limit = BandwidthLimit(download_mbps=50, upload_mbps=25, priority=80)
        
        result = self.bandwidth_manager.add_qos_rule(
            rule_id="test_qos",
            name="Test QoS Rule",
            protocol=Protocol.TCP,
            dst_port=80,
            traffic_class=TrafficClass.HIGH,
            bandwidth_limit=bandwidth_limit
        )
        
        self.assertTrue(result)
        self.assertIn("test_qos", self.bandwidth_manager.qos_rules)
        
        rule = self.bandwidth_manager.qos_rules["test_qos"]
        self.assertEqual(rule.name, "Test QoS Rule")
        self.assertEqual(rule.protocol, Protocol.TCP)
        self.assertEqual(rule.dst_port, 80)
        self.assertEqual(rule.traffic_class, TrafficClass.HIGH)
    
    @patch('psutil.net_io_counters')
    def test_usage_stats_collection(self, mock_net_io):
        """Test usage statistics collection."""
        # Mock network interface stats
        mock_stats = MagicMock()
        mock_stats.bytes_sent = 1000000
        mock_stats.bytes_recv = 2000000
        mock_stats.packets_sent = 1000
        mock_stats.packets_recv = 2000
        mock_stats.errin = 0
        mock_stats.errout = 0
        mock_stats.dropin = 0
        mock_stats.dropout = 0
        
        mock_net_io.return_value = {"test0": mock_stats}
        
        # Add a user limit to trigger stats collection
        self.bandwidth_manager.set_user_bandwidth_limit("test_user", 10.0, 5.0)
        
        # Collect stats
        self.bandwidth_manager._collect_usage_stats()
        
        # Check that stats were created
        stats = self.bandwidth_manager.get_usage_stats("test_user")
        self.assertIsNotNone(stats)
        self.assertEqual(stats.user_id, "test_user")
    
    def test_configuration_export(self):
        """Test configuration export."""
        # Set up some test data
        self.bandwidth_manager.set_user_bandwidth_limit("user1", 25.0, 10.0, 60)
        self.bandwidth_manager.set_user_bandwidth_limit("user2", 50.0, 20.0, 80)
        
        config = self.bandwidth_manager.export_configuration()
        
        self.assertEqual(config["interface"], "test0")
        self.assertIn("user_limits", config)
        self.assertIn("qos_rules", config)
        self.assertEqual(len(config["user_limits"]), 2)
        self.assertIn("user1", config["user_limits"])
        self.assertIn("user2", config["user_limits"])


class TestSystemIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        self.encryption = NetworkEncryption()
        self.access_control = AccessControl()
        
        # Mock subprocess for bandwidth manager
        self.patcher = patch('subprocess.run')
        self.mock_subprocess = self.patcher.start()
        self.mock_subprocess.return_value.returncode = 0
        
        self.bandwidth_manager = BandwidthManager(interface="test0")
    
    def tearDown(self):
        self.patcher.stop()
    
    def test_complete_user_workflow(self):
        """Test complete workflow: create user, set policies, authorize access."""
        # Create encryption policy
        network_policy = self.encryption.create_encryption_policy(
            network_id="TestNetwork",
            encryption_type=EncryptionType.WPA3_PSK,
            security_level=SecurityLevel.HIGH
        )
        
        # Create user
        user = self.access_control.create_user(
            username="integrationtest",
            email="integration@ncuk.edu",
            role=UserRole.FACULTY,
            mac_addresses=["FF:FF:FF:FF:FF:FF"]
        )
        
        # Set bandwidth limit
        bandwidth_result = self.bandwidth_manager.set_user_bandwidth_limit(
            user.user_id, 100.0, 50.0, 85
        )
        
        # Authorize MAC address
        auth_result = self.access_control.authorize_mac_address("FF:FF:FF:FF:FF:FF", user.user_id)
        
        # Verify all operations succeeded
        self.assertIsNotNone(network_policy)
        self.assertIsNotNone(user)
        self.assertTrue(bandwidth_result)
        self.assertTrue(auth_result)
        
        # Verify configurations
        self.assertEqual(network_policy["encryption_type"], "wpa3-psk")
        self.assertEqual(user.role, UserRole.FACULTY)
        
        limit = self.bandwidth_manager.get_user_bandwidth_limit(user.user_id)
        self.assertEqual(limit.download_mbps, 100.0)
        self.assertEqual(limit.upload_mbps, 50.0)


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestNetworkEncryption))
    suite.addTests(loader.loadTestsFromTestCase(TestAccessControl))
    suite.addTests(loader.loadTestsFromTestCase(TestBandwidthManager))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)