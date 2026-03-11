#!/usr/bin/env python3
"""
Security verification tool for WiFi Capping NCUK system.
This tool performs comprehensive security audits and validation.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from wifi_capping.core.config import get_config, ProductionConfig
from wifi_capping.security import SecurityValidator, EncryptionManager, CertificateManager
from wifi_capping.core.app import create_app


class SecurityAuditor:
    """Comprehensive security auditing tool."""
    
    def __init__(self):
        self.audit_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_score': 0,
            'checks': {},
            'recommendations': [],
            'critical_issues': [],
            'warnings': []
        }
    
    def run_audit(self, config_name: str = 'production') -> Dict[str, Any]:
        """Run comprehensive security audit."""
        print("🔍 Starting Security Audit...")
        print("=" * 50)
        
        # Configuration validation
        self._audit_configuration(config_name)
        
        # Encryption validation
        self._audit_encryption()
        
        # SSL/TLS validation
        self._audit_ssl_tls()
        
        # Policy validation
        self._audit_policies()
        
        # AUP validation
        self._audit_aup_compliance()
        
        # File permissions
        self._audit_file_permissions()
        
        # Calculate overall score
        self._calculate_score()
        
        return self.audit_results
    
    def _audit_configuration(self, config_name: str):
        """Audit configuration security."""
        print("📋 Auditing Configuration...")
        
        config = get_config(config_name)
        validation = config.validate_security_config()
        
        self.audit_results['checks']['configuration'] = {
            'valid': validation['valid'],
            'issues': validation['issues'],
            'warnings': validation['warnings']
        }
        
        if not validation['valid']:
            self.audit_results['critical_issues'].extend(validation['issues'])
        
        self.audit_results['warnings'].extend(validation['warnings'])
        
        # Production-specific checks
        if config_name == 'production':
            prod_validation = ProductionConfig.validate_production_config()
            if not prod_validation['valid']:
                self.audit_results['critical_issues'].extend(prod_validation['issues'])
        
        print(f"  ✅ Configuration audit complete")
    
    def _audit_encryption(self):
        """Audit encryption implementation."""
        print("🔐 Auditing Encryption...")
        
        try:
            # Test encryption manager
            encryption_manager = EncryptionManager()
            test_data = "Test encryption data"
            encrypted = encryption_manager.encrypt(test_data)
            decrypted = encryption_manager.decrypt(encrypted)
            
            encryption_working = (decrypted == test_data)
            
            self.audit_results['checks']['encryption'] = {
                'available': True,
                'working': encryption_working,
                'algorithm': 'Fernet (AES-128 CBC + HMAC SHA-256)'
            }
            
            if encryption_working:
                print("  ✅ Encryption working correctly")
            else:
                self.audit_results['critical_issues'].append("Encryption test failed")
                print("  ❌ Encryption test failed")
                
        except Exception as e:
            self.audit_results['checks']['encryption'] = {
                'available': False,
                'error': str(e)
            }
            self.audit_results['critical_issues'].append(f"Encryption unavailable: {e}")
            print(f"  ❌ Encryption error: {e}")
    
    def _audit_ssl_tls(self):
        """Audit SSL/TLS configuration."""
        print("🔒 Auditing SSL/TLS...")
        
        config = get_config()
        
        ssl_audit = {
            'required': config.SSL_REQUIRED,
            'cert_exists': os.path.exists(config.SSL_CERT_PATH),
            'key_exists': os.path.exists(config.SSL_KEY_PATH),
            'cert_path': config.SSL_CERT_PATH,
            'key_path': config.SSL_KEY_PATH
        }
        
        if config.SSL_REQUIRED:
            if not ssl_audit['cert_exists']:
                self.audit_results['critical_issues'].append(f"SSL certificate not found: {config.SSL_CERT_PATH}")
            if not ssl_audit['key_exists']:
                self.audit_results['critical_issues'].append(f"SSL key not found: {config.SSL_KEY_PATH}")
            
            # Check certificate validity (basic check)
            if ssl_audit['cert_exists']:
                try:
                    with open(config.SSL_CERT_PATH, 'rb') as f:
                        cert_data = f.read()
                    ssl_audit['cert_valid'] = b'-----BEGIN CERTIFICATE-----' in cert_data
                    if ssl_audit['cert_valid']:
                        print("  ✅ SSL certificate found and appears valid")
                    else:
                        self.audit_results['warnings'].append("SSL certificate format may be invalid")
                except Exception as e:
                    ssl_audit['cert_error'] = str(e)
                    self.audit_results['warnings'].append(f"Could not read SSL certificate: {e}")
        else:
            self.audit_results['warnings'].append("SSL/TLS is disabled - not recommended for production")
        
        self.audit_results['checks']['ssl_tls'] = ssl_audit
        print(f"  ✅ SSL/TLS audit complete")
    
    def _audit_policies(self):
        """Audit policy enforcement."""
        print("📊 Auditing Policy Enforcement...")
        
        try:
            app = create_app('testing')  # Use testing config for audit
            
            with app.app_context():
                policy_summary = app.policy_engine.get_policy_summary()
                
                policy_audit = {
                    'total_policies': policy_summary['total_policies'],
                    'enabled_policies': policy_summary['enabled_policies'],
                    'user_groups': policy_summary['user_groups'],
                    'policy_types': policy_summary['policy_types']
                }
                
                if policy_summary['enabled_policies'] == 0:
                    self.audit_results['warnings'].append("No enabled policies found")
                
                if policy_summary['user_groups'] == 0:
                    self.audit_results['warnings'].append("No user groups configured")
                
                self.audit_results['checks']['policies'] = policy_audit
                print(f"  ✅ Found {policy_summary['enabled_policies']} enabled policies")
                
        except Exception as e:
            self.audit_results['checks']['policies'] = {'error': str(e)}
            self.audit_results['warnings'].append(f"Policy audit failed: {e}")
            print(f"  ⚠️  Policy audit failed: {e}")
    
    def _audit_aup_compliance(self):
        """Audit AUP compliance features."""
        print("📜 Auditing AUP Compliance...")
        
        try:
            app = create_app('testing')
            
            with app.app_context():
                aup_policy = app.aup_policy_manager.get_active_policy()
                
                aup_audit = {
                    'active_policy': aup_policy.name if aup_policy else None,
                    'content_filters': len(app.aup_monitor.content_filters),
                    'monitoring_active': app.aup_monitor.monitoring_active
                }
                
                if not aup_policy:
                    self.audit_results['warnings'].append("No active AUP policy found")
                
                if not app.aup_monitor.monitoring_active:
                    self.audit_results['warnings'].append("AUP monitoring is not active")
                
                self.audit_results['checks']['aup'] = aup_audit
                print(f"  ✅ AUP audit complete - {aup_audit['content_filters']} content filters")
                
        except Exception as e:
            self.audit_results['checks']['aup'] = {'error': str(e)}
            self.audit_results['warnings'].append(f"AUP audit failed: {e}")
            print(f"  ⚠️  AUP audit failed: {e}")
    
    def _audit_file_permissions(self):
        """Audit file permissions for security-sensitive files."""
        print("📁 Auditing File Permissions...")
        
        config = get_config()
        sensitive_files = [
            config.SSL_CERT_PATH,
            config.SSL_KEY_PATH,
            '.env',
            'config.py'
        ]
        
        permission_audit = {}
        
        for file_path in sensitive_files:
            if os.path.exists(file_path):
                stat_info = os.stat(file_path)
                mode = oct(stat_info.st_mode)[-3:]  # Last 3 digits
                
                permission_audit[file_path] = {
                    'exists': True,
                    'permissions': mode,
                    'owner_readable': bool(int(mode[0]) & 4),
                    'group_readable': bool(int(mode[1]) & 4),
                    'other_readable': bool(int(mode[2]) & 4)
                }
                
                # Check for overly permissive permissions
                if file_path.endswith('.key') or file_path == '.env':
                    if int(mode[1]) > 0 or int(mode[2]) > 0:
                        self.audit_results['warnings'].append(
                            f"File {file_path} has overly permissive permissions: {mode}"
                        )
            else:
                permission_audit[file_path] = {'exists': False}
        
        self.audit_results['checks']['file_permissions'] = permission_audit
        print(f"  ✅ File permissions audit complete")
    
    def _calculate_score(self):
        """Calculate overall security score."""
        total_score = 100
        
        # Deduct points for critical issues
        total_score -= len(self.audit_results['critical_issues']) * 20
        
        # Deduct points for warnings
        total_score -= len(self.audit_results['warnings']) * 5
        
        # Ensure score doesn't go below 0
        self.audit_results['overall_score'] = max(0, total_score)
    
    def generate_report(self) -> str:
        """Generate human-readable audit report."""
        report = []
        report.append("WiFi Capping NCUK - Security Audit Report")
        report.append("=" * 50)
        report.append(f"Generated: {self.audit_results['timestamp']}")
        report.append(f"Overall Security Score: {self.audit_results['overall_score']}/100")
        report.append("")
        
        if self.audit_results['critical_issues']:
            report.append("🚨 CRITICAL ISSUES:")
            for issue in self.audit_results['critical_issues']:
                report.append(f"  - {issue}")
            report.append("")
        
        if self.audit_results['warnings']:
            report.append("⚠️  WARNINGS:")
            for warning in self.audit_results['warnings']:
                report.append(f"  - {warning}")
            report.append("")
        
        report.append("📊 AUDIT RESULTS:")
        for check_name, results in self.audit_results['checks'].items():
            report.append(f"  {check_name.title()}:")
            if isinstance(results, dict):
                for key, value in results.items():
                    report.append(f"    {key}: {value}")
            report.append("")
        
        # Security recommendations
        recommendations = [
            "Use strong passwords (12+ characters with mixed case, numbers, symbols)",
            "Enable SSL/TLS for all communications",
            "Regularly rotate encryption keys",
            "Monitor authentication logs for suspicious activity",
            "Implement rate limiting for login attempts",
            "Keep system and dependencies updated",
            "Regular security audits and penetration testing",
            "Backup encryption keys securely"
        ]
        
        report.append("📋 SECURITY RECOMMENDATIONS:")
        for rec in recommendations:
            report.append(f"  - {rec}")
        
        return "\n".join(report)


def main():
    """Main entry point for security verification tool."""
    import argparse
    
    parser = argparse.ArgumentParser(description='WiFi Capping NCUK Security Verification Tool')
    parser.add_argument('--config', default='production', 
                       choices=['development', 'testing', 'production'],
                       help='Configuration to audit (default: production)')
    parser.add_argument('--output', '-o', help='Output file for report')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    args = parser.parse_args()
    
    # Create auditor and run audit
    auditor = SecurityAuditor()
    results = auditor.run_audit(args.config)
    
    print("\n" + "=" * 50)
    print(f"🎯 Security Score: {results['overall_score']}/100")
    
    if results['critical_issues']:
        print(f"🚨 Critical Issues: {len(results['critical_issues'])}")
    if results['warnings']:
        print(f"⚠️  Warnings: {len(results['warnings'])}")
    
    # Generate output
    if args.json:
        output = json.dumps(results, indent=2)
    else:
        output = auditor.generate_report()
    
    # Save to file if specified
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"📄 Report saved to: {args.output}")
    else:
        print("\n" + output)
    
    # Return appropriate exit code
    if results['critical_issues']:
        return 1  # Critical issues found
    elif results['warnings']:
        return 2  # Warnings found
    else:
        return 0  # All good


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)