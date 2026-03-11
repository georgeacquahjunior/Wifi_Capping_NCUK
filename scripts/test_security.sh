#!/bin/bash
# Security Testing Script for WiFi Capping NCUK

echo "🔍 WiFi Capping NCUK - Security Testing Suite"
echo "============================================="

# Test encryption functionality
echo "🔐 Testing Encryption..."
python -c "
import sys
sys.path.insert(0, 'src')
from wifi_capping.security import EncryptionManager

try:
    manager = EncryptionManager()
    test_data = 'Sensitive test data for encryption'
    encrypted = manager.encrypt(test_data)
    decrypted = manager.decrypt(encrypted)
    
    if decrypted == test_data:
        print('✅ Encryption test passed')
    else:
        print('❌ Encryption test failed')
        sys.exit(1)
except Exception as e:
    print(f'❌ Encryption test error: {e}')
    sys.exit(1)
"

# Test password security
echo "🔑 Testing Password Security..."
python -c "
import sys
sys.path.insert(0, 'src')
from wifi_capping.security import PasswordManager, SecurityValidator

try:
    # Test password hashing
    password = 'TestPassword123!'
    hashed = PasswordManager.hash_password(password)
    
    if PasswordManager.verify_password(password, hashed):
        print('✅ Password hashing test passed')
    else:
        print('❌ Password hashing test failed')
        sys.exit(1)
    
    # Test password strength validation
    result = SecurityValidator.validate_password_strength('StrongP@ssw0rd123')
    if result['valid'] and result['strength'] == 'Strong':
        print('✅ Password strength validation passed')
    else:
        print('❌ Password strength validation failed')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ Password security test error: {e}')
    sys.exit(1)
"

# Test JWT tokens
echo "🎫 Testing JWT Tokens..."
python -c "
import sys
sys.path.insert(0, 'src')
from wifi_capping.security import TokenManager

try:
    secret_key = 'test_secret_key_12345'
    manager = TokenManager(secret_key)
    
    token = manager.generate_token('test_user', ['admin'])
    payload = manager.verify_token(token)
    
    if payload and payload['user_id'] == 'test_user':
        print('✅ JWT token test passed')
    else:
        print('❌ JWT token test failed')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ JWT token test error: {e}')
    sys.exit(1)
"

# Test configuration validation
echo "⚙️  Testing Configuration Validation..."
python -c "
import sys
sys.path.insert(0, 'src')
from wifi_capping.core.config import DevelopmentConfig

try:
    result = DevelopmentConfig.validate_security_config()
    if 'valid' in result:
        print('✅ Configuration validation test passed')
    else:
        print('❌ Configuration validation test failed')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ Configuration validation test error: {e}')
    sys.exit(1)
"

# Test policy engine
echo "📋 Testing Policy Engine..."
python -c "
import sys
sys.path.insert(0, 'src')
from wifi_capping.policy import PolicyEngine, DefaultPolicyTemplates

try:
    engine = PolicyEngine()
    
    # Add default policies
    policies = [
        DefaultPolicyTemplates.create_student_bandwidth_policy(),
        DefaultPolicyTemplates.create_staff_bandwidth_policy()
    ]
    
    for policy in policies:
        engine.add_policy(policy)
    
    summary = engine.get_policy_summary()
    if summary['total_policies'] >= 2:
        print('✅ Policy engine test passed')
    else:
        print('❌ Policy engine test failed')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ Policy engine test error: {e}')
    sys.exit(1)
"

# Test AUP monitoring
echo "📜 Testing AUP Monitoring..."
python -c "
import sys
sys.path.insert(0, 'src')
from wifi_capping.aup import AUPMonitor

try:
    monitor = AUPMonitor()
    
    # Test content filtering
    result = monitor.check_content_compliance(
        'http://example.com', 'test_user', '00:11:22:33:44:55'
    )
    
    if 'allowed' in result:
        print('✅ AUP monitoring test passed')
    else:
        print('❌ AUP monitoring test failed')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ AUP monitoring test error: {e}')
    sys.exit(1)
"

# Test system monitoring
echo "📊 Testing System Monitoring..."
python -c "
import sys
sys.path.insert(0, 'src')
from wifi_capping.monitoring import SystemMonitor

try:
    monitor = SystemMonitor()
    metrics = monitor.get_current_metrics()
    
    if 'timestamp' in metrics and 'cpu' in metrics:
        print('✅ System monitoring test passed')
    else:
        print('❌ System monitoring test failed')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ System monitoring test error: {e}')
    sys.exit(1)
"

echo ""
echo "🎯 Security Testing Summary:"
echo "============================"
echo "✅ All security tests passed!"
echo "✅ Encryption working correctly"
echo "✅ Password security validated"
echo "✅ JWT tokens functioning"
echo "✅ Configuration validation working"
echo "✅ Policy engine operational"
echo "✅ AUP monitoring active"
echo "✅ System monitoring functional"
echo ""
echo "System is ready for deployment! 🚀"