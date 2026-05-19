"""
Unit tests for WiFi Capping NCUK - RADIUS Integration
Tests for authentication and accounting functionality
"""

import unittest
import time
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wifi_capping.utils.config import Config
from wifi_capping.utils.security import validate_credentials, hash_password, verify_password, generate_session_id
from wifi_capping.radius import RadiusClient
from wifi_capping.capping import UserSession, BandwidthMonitor


class TestConfig(unittest.TestCase):
    """Test configuration management"""
    
    def test_default_config(self):
        """Test loading default configuration"""
        config = Config()
        
        self.assertEqual(config.radius_host, "127.0.0.1")
        self.assertEqual(config.radius_auth_port, 1812)
        self.assertEqual(config.radius_acct_port, 1813)
        self.assertEqual(config.default_bandwidth_limit_mb, 1000)
        self.assertEqual(config.monitoring_interval_seconds, 60)

    def test_config_validation(self):
        """Test configuration validation"""
        # Test with environment variables
        with patch.dict(os.environ, {
            'RADIUS_AUTH_PORT': '999999',  # Invalid port
        }):
            with self.assertRaises(ValueError):
                Config()


class TestSecurity(unittest.TestCase):
    """Test security utilities"""
    
    def test_validate_credentials(self):
        """Test credential validation"""
        # Valid credentials
        self.assertTrue(validate_credentials("testuser", "testpass123"))
        
        # Invalid credentials
        self.assertFalse(validate_credentials("", "testpass"))  # Empty username
        self.assertFalse(validate_credentials("user", ""))      # Empty password
        self.assertFalse(validate_credentials("ab", "testpass"))  # Username too short
        self.assertFalse(validate_credentials("user", "123"))   # Password too short
        self.assertFalse(validate_credentials("user@#$", "testpass"))  # Invalid characters

    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "test_password_123"
        
        # Hash password
        hashed, salt = hash_password(password)
        
        # Verify correct password
        self.assertTrue(verify_password(password, hashed, salt))
        
        # Verify incorrect password
        self.assertFalse(verify_password("wrong_password", hashed, salt))

    def test_session_id_generation(self):
        """Test session ID generation"""
        session_id1 = generate_session_id()
        session_id2 = generate_session_id()
        
        # Session IDs should be different
        self.assertNotEqual(session_id1, session_id2)
        
        # Session IDs should be 32 characters (16 bytes hex)
        self.assertEqual(len(session_id1), 32)
        self.assertEqual(len(session_id2), 32)


class TestRadiusClient(unittest.TestCase):
    """Test RADIUS client functionality"""
    
    def setUp(self):
        """Set up test configuration"""
        self.config = Config()
        
    @patch('wifi_capping.radius.client.Client')
    @patch('wifi_capping.radius.dictionary.Dictionary')
    def test_radius_client_init(self, mock_dict, mock_client):
        """Test RADIUS client initialization"""
        mock_dict.return_value = Mock()
        mock_client.return_value = Mock()
        
        radius_client = RadiusClient(self.config)
        
        # Verify client was created with correct parameters
        mock_client.assert_called_once()
        mock_dict.assert_called_once_with("dictionary")

    @patch('wifi_capping.radius.client.Client')
    @patch('wifi_capping.radius.dictionary.Dictionary')
    def test_authenticate_user_success(self, mock_dict, mock_client):
        """Test successful user authentication"""
        # Mock RADIUS client
        mock_dict.return_value = Mock()
        mock_auth_client = Mock()
        mock_client.return_value = mock_auth_client
        
        # Mock request packet
        mock_request = Mock()
        mock_request.PwCrypt = Mock(return_value="encrypted_password")
        mock_auth_client.CreateAuthPacket.return_value = mock_request
        
        # Mock successful authentication response
        mock_packet = Mock()
        mock_packet.code = 2  # Access-Accept
        mock_packet.keys.return_value = ['Session-Timeout']
        mock_packet.__getitem__ = Mock(return_value=[3600])
        
        mock_auth_client.SendPacket.return_value = mock_packet
        
        radius_client = RadiusClient(self.config)
        
        # Test authentication
        success, attributes = radius_client.authenticate_user("testuser", "testpass")
        
        self.assertTrue(success)
        self.assertIn('Session-Timeout', attributes)

    @patch('socket.socket')
    def test_connection_test(self, mock_socket):
        """Test RADIUS server connection test"""
        # Mock successful connection
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        
        with patch('wifi_capping.radius.client.Client'), \
             patch('wifi_capping.radius.dictionary.Dictionary'):
            
            radius_client = RadiusClient(self.config)
            result = radius_client.test_connection()
            
            self.assertTrue(result)
            mock_sock.connect.assert_called_once()
            mock_sock.close.assert_called_once()


class TestUserSession(unittest.TestCase):
    """Test user session management"""
    
    def test_session_creation(self):
        """Test user session creation"""
        session = UserSession(
            username="testuser",
            user_ip="192.168.1.100",
            nas_ip="192.168.1.1",
            nas_port=0,
            bandwidth_limit_mb=500
        )
        
        self.assertEqual(session.username, "testuser")
        self.assertEqual(session.user_ip, "192.168.1.100")
        self.assertEqual(session.bandwidth_limit_mb, 500)
        self.assertTrue(session.is_active)
        self.assertFalse(session.is_capped)
        self.assertEqual(session.total_bytes, 0)

    def test_usage_update(self):
        """Test usage tracking"""
        session = UserSession(
            username="testuser",
            user_ip="192.168.1.100",
            nas_ip="192.168.1.1",
            nas_port=0,
            bandwidth_limit_mb=1  # 1 MB limit for testing
        )
        
        # Add some usage (under limit)
        session.update_usage(500000, 400000)  # ~0.9 MB total
        self.assertFalse(session.is_capped)
        
        # Add usage that exceeds limit
        session.update_usage(200000, 200000)  # Additional ~0.4 MB (total ~1.3 MB)
        self.assertTrue(session.is_capped)

    def test_remaining_bandwidth(self):
        """Test remaining bandwidth calculation"""
        session = UserSession(
            username="testuser",
            user_ip="192.168.1.100",
            nas_ip="192.168.1.1",
            nas_port=0,
            bandwidth_limit_mb=10
        )
        
        # Initially should have full bandwidth available
        self.assertEqual(session.get_remaining_bandwidth_mb(), 10.0)
        
        # Use some bandwidth
        session.update_usage(5 * 1024 * 1024, 0)  # 5 MB
        remaining = session.get_remaining_bandwidth_mb()
        self.assertAlmostEqual(remaining, 5.0, places=1)
        
        # Exceed limit
        session.update_usage(10 * 1024 * 1024, 0)  # Additional 10 MB
        remaining = session.get_remaining_bandwidth_mb()
        self.assertEqual(remaining, 0.0)


class TestBandwidthMonitor(unittest.TestCase):
    """Test bandwidth monitoring functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = Config()
        self.mock_radius_client = Mock()
        self.bandwidth_monitor = BandwidthMonitor(self.config, self.mock_radius_client)

    def test_session_creation(self):
        """Test session creation in bandwidth monitor"""
        self.mock_radius_client.send_accounting_start.return_value = True
        
        session_id = self.bandwidth_monitor.create_session(
            username="testuser",
            user_ip="192.168.1.100",
            nas_ip="192.168.1.1",
            nas_port=0
        )
        
        # Verify session was created
        self.assertIn(session_id, self.bandwidth_monitor.active_sessions)
        session = self.bandwidth_monitor.active_sessions[session_id]
        self.assertEqual(session.username, "testuser")
        
        # Verify accounting start was sent
        self.mock_radius_client.send_accounting_start.assert_called_once()

    def test_session_end(self):
        """Test session termination"""
        self.mock_radius_client.send_accounting_start.return_value = True
        self.mock_radius_client.send_accounting_stop.return_value = True
        
        # Create session
        session_id = self.bandwidth_monitor.create_session(
            username="testuser",
            user_ip="192.168.1.100",
            nas_ip="192.168.1.1",
            nas_port=0
        )
        
        # End session
        result = self.bandwidth_monitor.end_session(session_id)
        
        self.assertTrue(result)
        self.assertNotIn(session_id, self.bandwidth_monitor.active_sessions)
        
        # Verify accounting stop was sent
        self.mock_radius_client.send_accounting_stop.assert_called_once()

    def test_get_session_info(self):
        """Test session information retrieval"""
        self.mock_radius_client.send_accounting_start.return_value = True
        
        session_id = self.bandwidth_monitor.create_session(
            username="testuser",
            user_ip="192.168.1.100",
            nas_ip="192.168.1.1",
            nas_port=0,
            bandwidth_limit_mb=500
        )
        
        info = self.bandwidth_monitor.get_session_info(session_id)
        
        self.assertIsNotNone(info)
        self.assertEqual(info['username'], "testuser")
        self.assertEqual(info['user_ip'], "192.168.1.100")
        self.assertEqual(info['bandwidth_limit_mb'], 500)
        self.assertTrue(info['is_active'])
        self.assertFalse(info['is_capped'])


if __name__ == '__main__':
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    unittest.main()