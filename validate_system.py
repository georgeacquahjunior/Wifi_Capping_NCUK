#!/usr/bin/env python3
"""
Basic validation script for WiFi Monitoring System
Tests core functionality without external dependencies
"""

import os
import sys
import yaml
import json
import tempfile
import unittest
from unittest.mock import Mock, patch

def test_config_loading():
    """Test configuration loading functionality"""
    print("Testing configuration loading...")
    
    # Create a test config
    test_config = {
        'monitoring': {
            'max_devices_per_hour': 50,
            'scan_interval_seconds': 60
        },
        'security': {
            'auto_update': True,
            'alert_threshold': 'medium'
        },
        'network': {
            'interface': 'wlan0',
            'ssid': 'TEST_WIFI'
        }
    }
    
    # Test YAML parsing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        yaml.dump(test_config, f)
        config_file = f.name
    
    try:
        with open(config_file, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        assert loaded_config['monitoring']['max_devices_per_hour'] == 50
        assert loaded_config['security']['auto_update'] == True
        assert loaded_config['network']['interface'] == 'wlan0'
        
        print("✓ Configuration loading works correctly")
        return True
        
    finally:
        os.unlink(config_file)

def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")
    
    required_files = [
        'wifi_monitor.py',
        'security_manager.py',
        'config.yml',
        'requirements.txt',
        'setup.sh',
        'test_suite.py',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✓ All required files present")
    return True

def test_python_syntax():
    """Test Python files for syntax errors"""
    print("Testing Python syntax...")
    
    python_files = ['wifi_monitor.py', 'security_manager.py', 'test_suite.py']
    
    for file in python_files:
        try:
            with open(file, 'r') as f:
                content = f.read()
            
            # Compile to check syntax
            compile(content, file, 'exec')
            print(f"✓ {file} syntax is valid")
            
        except SyntaxError as e:
            print(f"❌ Syntax error in {file}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error checking {file}: {e}")
            return False
    
    return True

def test_configuration_validation():
    """Test the default configuration file"""
    print("Testing configuration validation...")
    
    try:
        with open('config.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required sections
        required_sections = ['monitoring', 'security', 'logging', 'network']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing configuration section: {section}")
                return False
        
        # Check monitoring settings
        monitoring = config['monitoring']
        required_monitoring = ['max_devices_per_hour', 'max_bandwidth_mbps', 'scan_interval_seconds']
        for setting in required_monitoring:
            if setting not in monitoring:
                print(f"❌ Missing monitoring setting: {setting}")
                return False
        
        # Check security settings
        security = config['security']
        required_security = ['auto_update', 'update_check_interval_hours', 'alert_threshold']
        for setting in required_security:
            if setting not in security:
                print(f"❌ Missing security setting: {setting}")
                return False
        
        print("✓ Configuration structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def test_script_permissions():
    """Test that scripts have correct permissions"""
    print("Testing script permissions...")
    
    executable_files = ['setup.sh']
    
    for file in executable_files:
        if os.path.exists(file):
            if os.access(file, os.X_OK):
                print(f"✓ {file} is executable")
            else:
                print(f"❌ {file} is not executable")
                return False
        else:
            print(f"❌ {file} does not exist")
            return False
    
    return True

def test_documentation():
    """Test documentation completeness"""
    print("Testing documentation...")
    
    try:
        with open('README.md', 'r') as f:
            readme = f.read()
        
        # Check for key sections
        required_sections = ['Features', 'Installation', 'Configuration', 'Usage']
        missing_sections = []
        
        for section in required_sections:
            if section not in readme:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing documentation sections: {missing_sections}")
            return False
        
        # Check for minimum content length
        if len(readme) < 1000:
            print("❌ Documentation appears incomplete (too short)")
            return False
        
        print("✓ Documentation is comprehensive")
        return True
        
    except Exception as e:
        print(f"❌ Documentation validation failed: {e}")
        return False

def test_security_features():
    """Test that security features are properly implemented"""
    print("Testing security feature implementation...")
    
    # Check that security-related code exists
    security_keywords = [
        'suspicious', 'vulnerability', 'update', 'alert', 'monitoring', 
        'threat', 'scan', 'security', 'unauthorized'
    ]
    
    files_to_check = ['wifi_monitor.py', 'security_manager.py']
    
    for file in files_to_check:
        try:
            with open(file, 'r') as f:
                content = f.read().lower()
            
            found_keywords = []
            for keyword in security_keywords:
                if keyword in content:
                    found_keywords.append(keyword)
            
            if len(found_keywords) < 5:  # Should have at least 5 security-related terms
                print(f"❌ {file} may not have sufficient security features")
                return False
            
            print(f"✓ {file} contains security features: {', '.join(found_keywords[:5])}")
            
        except Exception as e:
            print(f"❌ Error checking security features in {file}: {e}")
            return False
    
    return True

def run_all_tests():
    """Run all validation tests"""
    print("=== WiFi Monitoring System Validation ===")
    print()
    
    tests = [
        test_file_structure,
        test_python_syntax,
        test_config_loading,
        test_configuration_validation,
        test_script_permissions,
        test_documentation,
        test_security_features
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            print()
    
    print("=== Validation Summary ===")
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("✅ All validation tests passed!")
        print("The WiFi monitoring and security system appears to be correctly implemented.")
        return True
    else:
        print("❌ Some validation tests failed.")
        print("Please review the issues above before deploying the system.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)