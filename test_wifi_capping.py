#!/usr/bin/env python3
"""
Test script for Wi-Fi Usage Capping System

This script tests the basic functionality of the Wi-Fi capping system.
"""

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import subprocess

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wifi_capping import WiFiUsageCapper


class TestWiFiUsageCapper(unittest.TestCase):
    """Test cases for WiFiUsageCapper class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "test_config.json")
        self.data_path = os.path.join(self.test_dir, "test_usage.json")
        
        # Create test capper instance
        self.capper = WiFiUsageCapper(self.config_path)
        self.capper.data_file = self.data_path
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_config_creation(self):
        """Test that default config is created properly."""
        self.assertIsInstance(self.capper.config, dict)
        self.assertEqual(self.capper.config["data_limit_gb"], 20)
        self.assertEqual(self.capper.config["reset_period_days"], 30)
        self.assertTrue(os.path.exists(self.config_path))
    
    def test_usage_data_creation(self):
        """Test that usage data structure is created properly."""
        self.assertIsInstance(self.capper.usage_data, dict)
        self.assertEqual(self.capper.usage_data["total_bytes"], 0)
        self.assertFalse(self.capper.usage_data["is_disconnected"])
    
    @patch('wifi_capping.psutil.net_io_counters')
    def test_network_stats(self, mock_net_io):
        """Test network statistics collection."""
        # Mock network stats
        mock_stats = MagicMock()
        mock_stats.bytes_sent = 1000000
        mock_stats.bytes_recv = 2000000
        mock_net_io.return_value = mock_stats
        
        stats = self.capper.get_network_stats()
        self.assertEqual(stats, 3000000)
    
    @patch('wifi_capping.psutil.net_io_counters')
    def test_usage_update(self, mock_net_io):
        """Test usage data update."""
        # Mock network stats
        mock_stats = MagicMock()
        mock_stats.bytes_sent = 1000000
        mock_stats.bytes_recv = 2000000
        mock_net_io.return_value = mock_stats
        
        # First update (initialization)
        self.capper.update_usage()
        self.assertEqual(self.capper.usage_data["total_bytes"], 0)
        self.assertEqual(self.capper.usage_data["last_check"], 3000000)
        
        # Second update (with new data)
        mock_stats.bytes_sent = 1500000
        mock_stats.bytes_recv = 2500000
        self.capper.update_usage()
        self.assertEqual(self.capper.usage_data["total_bytes"], 1000000)
        self.assertEqual(self.capper.usage_data["last_check"], 4000000)
    
    def test_limit_checking(self):
        """Test data limit checking."""
        # Set usage below limit
        self.capper.usage_data["total_bytes"] = 10 * (1024 ** 3)  # 10GB
        self.assertFalse(self.capper.is_limit_exceeded())
        
        # Set usage above limit
        self.capper.usage_data["total_bytes"] = 25 * (1024 ** 3)  # 25GB
        self.assertTrue(self.capper.is_limit_exceeded())
    
    def test_usage_gb_calculation(self):
        """Test GB usage calculation."""
        self.capper.usage_data["total_bytes"] = 5 * (1024 ** 3)  # 5GB
        self.assertAlmostEqual(self.capper.get_usage_gb(), 5.0, places=1)
    
    def test_status_report(self):
        """Test status reporting."""
        self.capper.usage_data["total_bytes"] = 5 * (1024 ** 3)  # 5GB
        status = self.capper.get_status()
        
        self.assertEqual(status["usage_gb"], 5.0)
        self.assertEqual(status["limit_gb"], 20)
        self.assertEqual(status["percentage"], 25.0)
        self.assertFalse(status["is_disconnected"])
    
    def test_reset_usage(self):
        """Test usage data reset."""
        # Set some usage data
        self.capper.usage_data["total_bytes"] = 10 * (1024 ** 3)  # 10GB
        self.capper.usage_data["is_disconnected"] = True
        
        # Reset
        self.capper.reset_usage()
        
        self.assertEqual(self.capper.usage_data["total_bytes"], 0)
        self.assertFalse(self.capper.usage_data["is_disconnected"])


def run_integration_test():
    """Run a simple integration test."""
    print("Running integration test...")
    
    # Test basic functionality
    capper = WiFiUsageCapper("test_config.json")
    
    # Test status
    status = capper.get_status()
    print(f"Initial status: {status['usage_gb']:.2f}GB / {status['limit_gb']}GB")
    
    # Test config save/load
    capper.config["data_limit_gb"] = 15
    capper.save_config()
    
    # Create new instance to test loading
    capper2 = WiFiUsageCapper("test_config.json")
    assert capper2.config["data_limit_gb"] == 15, "Config not saved/loaded correctly"
    
    print("Integration test passed!")
    
    # Cleanup
    for file in ["test_config.json", "test_usage.json", "wifi_capping.log"]:
        if os.path.exists(file):
            os.remove(file)


def main():
    """Main test runner."""
    print("Wi-Fi Usage Capping System - Test Suite")
    print("=" * 50)
    
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "=" * 50)
    
    # Run integration test
    run_integration_test()
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    main()