#!/usr/bin/env python3
"""
Test suite for FreeRADIUS-NAS-Backend flow validation
"""

import unittest
import requests
import json
import time
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin_tools.validation_tool import ValidationTool

class TestRadiusBackendFlow(unittest.TestCase):
    """Test cases for RADIUS backend flow validation"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.validator = ValidationTool()
        cls.backend_url = cls.validator.backend_url
        
    def test_01_database_connectivity(self):
        """Test database connection"""
        result = self.validator.test_database_connection()
        self.assertTrue(result, "Database connection should be successful")
    
    def test_02_backend_api_health(self):
        """Test backend API health check"""
        result = self.validator.test_backend_api()
        self.assertTrue(result, "Backend API should be healthy")
    
    def test_03_nas_device_validation(self):
        """Test NAS device configuration"""
        result = self.validator.validate_nas_devices()
        self.assertTrue(result, "NAS devices should be properly configured")
    
    def test_04_user_authentication_success(self):
        """Test successful user authentication"""
        result = self.validator.test_radius_auth("testuser1", "password123")
        self.assertTrue(result, "Valid user should authenticate successfully")
    
    def test_05_user_authentication_failure(self):
        """Test failed user authentication with wrong password"""
        result = self.validator.test_radius_auth("testuser1", "wrongpassword")
        self.assertFalse(result, "Invalid password should be rejected")
    
    def test_06_nonexistent_user_authentication(self):
        """Test authentication with non-existent user"""
        result = self.validator.test_radius_auth("nonexistentuser", "password")
        self.assertFalse(result, "Non-existent user should be rejected")
    
    def test_07_accounting_session_flow(self):
        """Test complete accounting session flow"""
        result = self.validator.test_accounting_flow("testuser1")
        self.assertTrue(result, "Accounting session flow should work correctly")
    
    def test_08_api_auth_endpoint(self):
        """Test API authentication endpoint directly"""
        auth_data = {
            "username": "testuser1",
            "password": "password123",
            "nas_ip": "192.168.1.1"
        }
        
        try:
            response = requests.post(f"{self.backend_url}/auth", json=auth_data, timeout=10)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data['status'], 'accept')
            self.assertIn('user_data', data)
            
        except Exception as e:
            self.fail(f"API authentication endpoint failed: {str(e)}")
    
    def test_09_api_accounting_start(self):
        """Test API accounting start endpoint"""
        session_id = f"test-{int(time.time())}"
        start_data = {
            "session_id": session_id,
            "username": "testuser1",
            "nas_ip": "192.168.1.1",
            "nas_port": 1
        }
        
        try:
            response = requests.post(f"{self.backend_url}/accounting/start", json=start_data, timeout=10)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data['status'], 'success')
            
        except Exception as e:
            self.fail(f"API accounting start failed: {str(e)}")
    
    def test_10_api_status_endpoint(self):
        """Test API status endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/status", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data['status'], 'healthy')
            self.assertIn('total_users', data)
            self.assertIn('timestamp', data)
            
        except Exception as e:
            self.fail(f"API status endpoint failed: {str(e)}")

class TestRadiusValidationTool(unittest.TestCase):
    """Test cases for the validation tool itself"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.validator = ValidationTool()
    
    def test_validation_tool_initialization(self):
        """Test validation tool initializes correctly"""
        self.assertIsNotNone(self.validator.engine)
        self.assertIsNotNone(self.validator.Session)
        self.assertIsNotNone(self.validator.backend_url)
    
    def test_database_configuration(self):
        """Test database configuration is loaded"""
        self.assertIn('host', self.validator.db_config)
        self.assertIn('port', self.validator.db_config)
        self.assertIn('user', self.validator.db_config)
        self.assertIn('password', self.validator.db_config)
        self.assertIn('database', self.validator.db_config)
    
    def test_radius_configuration(self):
        """Test RADIUS configuration is loaded"""
        self.assertIn('host', self.validator.radius_config)
        self.assertIn('secret', self.validator.radius_config)
        self.assertIn('auth_port', self.validator.radius_config)
        self.assertIn('acct_port', self.validator.radius_config)

def run_tests():
    """Run all test suites"""
    print("Running FreeRADIUS-NAS-Backend Flow Validation Tests")
    print("=" * 60)
    
    # Create test suites
    backend_suite = unittest.TestLoader().loadTestsFromTestCase(TestRadiusBackendFlow)
    tool_suite = unittest.TestLoader().loadTestsFromTestCase(TestRadiusValidationTool)
    
    # Combine test suites
    all_tests = unittest.TestSuite([backend_suite, tool_suite])
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(all_tests)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    if success:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {len(result.failures + result.errors)} test(s) failed")
    
    return success

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)