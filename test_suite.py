#!/usr/bin/env python3
"""
Test suite for WiFi Monitoring and Security System
"""

import unittest
import tempfile
import os
import json
import yaml
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wifi_monitor import WiFiSecurityMonitor
from security_manager import SecurityUpdateManager, SecurityUpdate, Vulnerability

class TestWiFiSecurityMonitor(unittest.TestCase):
    """Test cases for WiFi Security Monitor"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.yml')
        
        # Create test configuration
        test_config = {
            'monitoring': {
                'max_devices_per_hour': 10,
                'max_bandwidth_mbps': 100,
                'suspicious_ports': [22, 23],
                'scan_interval_seconds': 5,
                'unusual_traffic_threshold': 80,
                'connection_timeout_threshold': 30
            },
            'security': {
                'auto_update': False,
                'update_check_interval_hours': 1,
                'alert_email': 'test@example.com',
                'alert_threshold': 'medium'
            },
            'logging': {
                'level': 'DEBUG',
                'file': os.path.join(self.temp_dir, 'test.log')
            },
            'network': {
                'interface': 'eth0',
                'ssid': 'TEST_WIFI',
                'trusted_mac_patterns': ['00:11:22:*']
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(test_config, f)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_monitor_initialization(self):
        """Test monitor initialization"""
        monitor = WiFiSecurityMonitor(self.config_file)
        
        self.assertIsNotNone(monitor.config)
        self.assertIsNotNone(monitor.logger)
        self.assertEqual(monitor.config['monitoring']['max_devices_per_hour'], 10)
        self.assertFalse(monitor.monitoring_active)
    
    def test_config_loading(self):
        """Test configuration loading"""
        monitor = WiFiSecurityMonitor(self.config_file)
        
        self.assertEqual(monitor.config['network']['interface'], 'eth0')
        self.assertEqual(monitor.config['network']['ssid'], 'TEST_WIFI')
    
    def test_default_config(self):
        """Test default configuration when file doesn't exist"""
        monitor = WiFiSecurityMonitor('nonexistent.yml')
        
        self.assertIsNotNone(monitor.config)
        self.assertIn('monitoring', monitor.config)
        self.assertIn('security', monitor.config)
    
    @patch('wifi_monitor.psutil.net_io_counters')
    def test_traffic_analysis(self, mock_net_stats):
        """Test traffic pattern analysis"""
        # Mock network statistics
        mock_stats = Mock()
        mock_stats.bytes_sent = 1000000
        mock_stats.bytes_recv = 2000000
        mock_stats.packets_sent = 1000
        mock_stats.packets_recv = 2000
        mock_net_stats.return_value = mock_stats
        
        monitor = WiFiSecurityMonitor(self.config_file)
        
        # Test traffic analysis
        monitor._analyze_traffic_patterns()
        
        self.assertTrue(len(monitor.traffic_history) > 0)
        self.assertIn('timestamp', monitor.traffic_history[0])
        self.assertIn('bytes_sent', monitor.traffic_history[0])
    
    def test_suspicious_device_detection(self):
        """Test suspicious device detection"""
        monitor = WiFiSecurityMonitor(self.config_file)
        
        # Add a trusted device
        monitor.connected_devices['00:11:22:33:44:55'] = {
            'last_seen': datetime.now(),
            'ip': '192.168.1.100'
        }
        
        # Add an untrusted device
        monitor.connected_devices['AA:BB:CC:DD:EE:FF'] = {
            'last_seen': datetime.now(),
            'ip': '192.168.1.101'
        }
        
        initial_events = len(monitor.suspicious_events)
        monitor._check_suspicious_devices()
        
        # Should have detected the untrusted device
        self.assertGreater(len(monitor.suspicious_events), initial_events)
    
    def test_device_count_threshold(self):
        """Test device count threshold detection"""
        monitor = WiFiSecurityMonitor(self.config_file)
        
        # Add devices exceeding threshold
        for i in range(15):  # More than the configured threshold of 10
            monitor.connected_devices[f'00:11:22:33:44:{i:02x}'] = {
                'last_seen': datetime.now(),
                'ip': f'192.168.1.{100+i}'
            }
        
        initial_events = len(monitor.suspicious_events)
        monitor._detect_suspicious_activity()
        
        # Should have detected too many devices
        self.assertGreater(len(monitor.suspicious_events), initial_events)
    
    def test_status_report(self):
        """Test status report generation"""
        monitor = WiFiSecurityMonitor(self.config_file)
        
        status = monitor.get_status_report()
        
        self.assertIn('monitoring_active', status)
        self.assertIn('connected_devices', status)
        self.assertIn('suspicious_events_last_24h', status)
        self.assertIn('system_status', status)
        self.assertEqual(status['system_status'], 'operational')
    
    def test_event_export(self):
        """Test event export functionality"""
        monitor = WiFiSecurityMonitor(self.config_file)
        
        # Add some test events
        monitor._log_suspicious_event('test_event', 'Test description', 'medium')
        
        export_file = os.path.join(self.temp_dir, 'test_events.json')
        filename = monitor.export_events(export_file)
        
        self.assertTrue(os.path.exists(filename))
        
        with open(filename, 'r') as f:
            events = json.load(f)
        
        self.assertGreater(len(events), 0)
        self.assertIn('type', events[0])
        self.assertIn('timestamp', events[0])


class TestSecurityUpdateManager(unittest.TestCase):
    """Test cases for Security Update Manager"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.yml')
        
        test_config = {
            'security': {
                'auto_update': True,
                'update_check_interval_hours': 1,
                'alert_threshold': 'medium'
            },
            'logging': {
                'level': 'DEBUG'
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(test_config, f)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_manager_initialization(self):
        """Test security manager initialization"""
        manager = SecurityUpdateManager(self.config_file)
        
        self.assertIsNotNone(manager.config)
        self.assertIsNotNone(manager.logger)
        self.assertTrue(manager.config['security']['auto_update'])
    
    def test_security_update_creation(self):
        """Test SecurityUpdate dataclass"""
        update = SecurityUpdate(
            package_name='test-package',
            current_version='1.0.0',
            new_version='1.1.0',
            severity='medium',
            description='Test update',
            cve_ids=['CVE-2023-1234']
        )
        
        self.assertEqual(update.package_name, 'test-package')
        self.assertEqual(update.severity, 'medium')
        self.assertIn('CVE-2023-1234', update.cve_ids)
    
    def test_vulnerability_creation(self):
        """Test Vulnerability dataclass"""
        vuln = Vulnerability(
            cve_id='CVE-2023-5678',
            severity='high',
            description='Test vulnerability',
            affected_packages=['package1', 'package2']
        )
        
        self.assertEqual(vuln.cve_id, 'CVE-2023-5678')
        self.assertEqual(vuln.severity, 'high')
        self.assertIn('package1', vuln.affected_packages)
    
    @patch('subprocess.run')
    def test_system_package_check(self, mock_subprocess):
        """Test system package update checking"""
        # Mock apt list output
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = """
        test-package/stable 1.1.0 amd64 [upgradable from: 1.0.0]
        another-package/stable 2.0.0 amd64 [upgradable from: 1.9.0]
        """
        
        manager = SecurityUpdateManager(self.config_file)
        
        with patch.object(manager, '_is_debian_based', return_value=True):
            with patch.object(manager, '_is_security_update', return_value=True):
                updates = manager._check_apt_updates()
        
        self.assertGreater(len(updates), 0)
    
    def test_severity_ordering(self):
        """Test vulnerability severity ordering"""
        manager = SecurityUpdateManager(self.config_file)
        
        vulnerabilities = [
            Vulnerability('CVE-1', 'low', 'Low severity', []),
            Vulnerability('CVE-2', 'critical', 'Critical severity', []),
            Vulnerability('CVE-3', 'medium', 'Medium severity', [])
        ]
        
        max_severity = manager._get_max_severity(vulnerabilities)
        self.assertEqual(max_severity, 'critical')
    
    def test_security_report_generation(self):
        """Test security report generation"""
        manager = SecurityUpdateManager(self.config_file)
        
        # Add test vulnerabilities
        manager.vulnerabilities = [
            Vulnerability('CVE-2023-1', 'medium', 'Test vuln 1', ['pkg1']),
            Vulnerability('CVE-2023-2', 'high', 'Test vuln 2', ['pkg2'])
        ]
        
        report = manager.generate_security_report()
        
        self.assertIn('timestamp', report)
        self.assertIn('vulnerabilities', report)
        self.assertIn('security_status', report)
        self.assertEqual(len(report['vulnerabilities']), 2)
    
    def test_security_status_assessment(self):
        """Test security status assessment"""
        manager = SecurityUpdateManager(self.config_file)
        
        # Test with no vulnerabilities
        manager.vulnerabilities = []
        self.assertEqual(manager._get_security_status(), 'secure')
        
        # Test with critical vulnerability
        manager.vulnerabilities = [
            Vulnerability('CVE-1', 'critical', 'Critical vuln', [])
        ]
        self.assertEqual(manager._get_security_status(), 'critical')
        
        # Test with high vulnerability
        manager.vulnerabilities = [
            Vulnerability('CVE-1', 'high', 'High vuln', [])
        ]
        self.assertEqual(manager._get_security_status(), 'high_risk')
    
    def test_config_security_check(self):
        """Test configuration security checking"""
        manager = SecurityUpdateManager(self.config_file)
        
        # Create a test config file with security issues
        test_config_file = os.path.join(self.temp_dir, 'insecure_config.txt')
        with open(test_config_file, 'w') as f:
            f.write('password=secret123\ndebug: true\n')
        
        vulnerabilities = manager._check_config_security(test_config_file)
        
        self.assertGreater(len(vulnerabilities), 0)
        # Should detect both password and debug issues
        descriptions = [v.description for v in vulnerabilities]
        self.assertTrue(any('password' in desc.lower() for desc in descriptions))
        self.assertTrue(any('debug' in desc.lower() for desc in descriptions))


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'integration_config.yml')
        
        # Create comprehensive test configuration
        test_config = {
            'monitoring': {
                'max_devices_per_hour': 5,
                'max_bandwidth_mbps': 50,
                'suspicious_ports': [22, 23, 3389],
                'scan_interval_seconds': 1,
                'unusual_traffic_threshold': 70,
                'connection_timeout_threshold': 20
            },
            'security': {
                'auto_update': False,  # Disable for testing
                'update_check_interval_hours': 1,
                'alert_email': 'security@test.com',
                'alert_threshold': 'low'
            },
            'logging': {
                'level': 'INFO',
                'file': os.path.join(self.temp_dir, 'integration.log')
            },
            'network': {
                'interface': 'lo',  # Use loopback for testing
                'ssid': 'TEST_NETWORK',
                'trusted_mac_patterns': ['00:11:22:*', 'AA:BB:CC:*']
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(test_config, f)
    
    def tearDown(self):
        """Clean up integration test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_full_system_initialization(self):
        """Test full system initialization and basic functionality"""
        # Initialize both components
        monitor = WiFiSecurityMonitor(self.config_file)
        security_manager = SecurityUpdateManager(self.config_file)
        
        # Test that both components are properly initialized
        self.assertIsNotNone(monitor.config)
        self.assertIsNotNone(security_manager.config)
        
        # Test configuration consistency
        self.assertEqual(
            monitor.config['security']['alert_threshold'],
            security_manager.config['security']['alert_threshold']
        )
    
    @patch('wifi_monitor.psutil.net_io_counters')
    @patch('wifi_monitor.netifaces.interfaces')
    def test_monitoring_and_security_workflow(self, mock_interfaces, mock_net_stats):
        """Test the complete monitoring and security workflow"""
        # Mock network data
        mock_interfaces.return_value = ['lo', 'eth0']
        mock_stats = Mock()
        mock_stats.bytes_sent = 500000
        mock_stats.bytes_recv = 1000000
        mock_stats.packets_sent = 500
        mock_stats.packets_recv = 1000
        mock_net_stats.return_value = mock_stats
        
        monitor = WiFiSecurityMonitor(self.config_file)
        security_manager = SecurityUpdateManager(self.config_file)
        
        # Add some test devices to trigger alerts
        for i in range(7):  # Exceed the threshold of 5
            monitor.connected_devices[f'FF:EE:DD:CC:BB:{i:02x}'] = {
                'last_seen': datetime.now(),
                'ip': f'192.168.1.{200+i}'
            }
        
        # Run monitoring checks
        monitor._scan_network_devices()
        monitor._analyze_traffic_patterns()
        monitor._detect_suspicious_activity()
        
        # Verify suspicious events were generated
        self.assertGreater(len(monitor.suspicious_events), 0)
        
        # Generate reports
        monitor_status = monitor.get_status_report()
        security_report = security_manager.generate_security_report()
        
        # Verify reports contain expected data
        self.assertIn('suspicious_events_last_24h', monitor_status)
        self.assertIn('security_status', security_report)
    
    def test_export_and_import_functionality(self):
        """Test data export and import functionality"""
        monitor = WiFiSecurityMonitor(self.config_file)
        security_manager = SecurityUpdateManager(self.config_file)
        
        # Generate some test data
        monitor._log_suspicious_event('test_event', 'Integration test event', 'low')
        security_manager.vulnerabilities = [
            Vulnerability('CVE-TEST-1', 'medium', 'Test vulnerability', ['test-package'])
        ]
        
        # Export data
        events_file = monitor.export_events(os.path.join(self.temp_dir, 'test_events.json'))
        report_file = security_manager.export_report(os.path.join(self.temp_dir, 'test_report.json'))
        
        # Verify files were created
        self.assertTrue(os.path.exists(events_file))
        self.assertTrue(os.path.exists(report_file))
        
        # Verify file contents
        with open(events_file, 'r') as f:
            events_data = json.load(f)
        
        with open(report_file, 'r') as f:
            report_data = json.load(f)
        
        self.assertGreater(len(events_data), 0)
        self.assertIn('vulnerabilities', report_data)
        self.assertGreater(len(report_data['vulnerabilities']), 0)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestWiFiSecurityMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityUpdateManager))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)