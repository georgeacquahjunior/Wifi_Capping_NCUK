#!/usr/bin/env python3
"""
WiFi Monitoring System Demonstration
Shows core functionality without requiring full dependencies
"""

import yaml
import json
from datetime import datetime, timedelta
from typing import Dict, List

class MockWiFiMonitor:
    """Mock WiFi monitor for demonstration purposes"""
    
    def __init__(self):
        self.config = self._load_config()
        self.suspicious_events = []
        self.connected_devices = {}
        print("✓ Mock WiFi Monitor initialized")
    
    def _load_config(self):
        """Load configuration"""
        try:
            with open('config.yml', 'r') as f:
                return yaml.safe_load(f)
        except:
            return {'monitoring': {'max_devices_per_hour': 50}}
    
    def simulate_monitoring(self):
        """Simulate monitoring activities"""
        print("\n=== Simulating Network Monitoring ===")
        
        # Simulate device detection
        test_devices = [
            "00:11:22:33:44:55",  # Trusted device
            "AA:BB:CC:DD:EE:FF",  # Untrusted device
            "FF:EE:DD:CC:BB:AA"   # Another untrusted device
        ]
        
        for mac in test_devices:
            self.connected_devices[mac] = {
                'last_seen': datetime.now(),
                'ip': f'192.168.1.{len(self.connected_devices)+100}'
            }
            print(f"✓ Detected device: {mac}")
        
        # Simulate suspicious activity detection
        self._detect_suspicious_activity()
        
        return len(self.suspicious_events)
    
    def _detect_suspicious_activity(self):
        """Detect suspicious activity"""
        # Check for untrusted devices
        trusted_patterns = self.config.get('network', {}).get('trusted_mac_patterns', ['00:11:22:*'])
        
        for mac in self.connected_devices:
            is_trusted = any(mac.startswith(pattern.replace('*', '')) for pattern in trusted_patterns)
            
            if not is_trusted:
                event = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'untrusted_device',
                    'description': f'Untrusted device detected: {mac}',
                    'severity': 'medium'
                }
                self.suspicious_events.append(event)
                print(f"⚠ ALERT: {event['description']}")
        
        # Check device count
        device_count = len(self.connected_devices)
        max_devices = self.config['monitoring']['max_devices_per_hour']
        
        if device_count > max_devices:
            event = {
                'timestamp': datetime.now().isoformat(),
                'type': 'too_many_devices',
                'description': f'Too many devices: {device_count} (limit: {max_devices})',
                'severity': 'high'
            }
            self.suspicious_events.append(event)
            print(f"🚨 CRITICAL: {event['description']}")
    
    def get_status_report(self):
        """Generate status report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'connected_devices': len(self.connected_devices),
            'suspicious_events': len(self.suspicious_events),
            'last_24h_events': len([e for e in self.suspicious_events 
                                  if datetime.fromisoformat(e['timestamp']) > datetime.now() - timedelta(hours=24)]),
            'system_status': 'operational'
        }

class MockSecurityManager:
    """Mock security manager for demonstration purposes"""
    
    def __init__(self):
        self.vulnerabilities = []
        self.update_history = []
        print("✓ Mock Security Manager initialized")
    
    def simulate_security_scan(self):
        """Simulate security vulnerability scan"""
        print("\n=== Simulating Security Scan ===")
        
        # Simulate finding vulnerabilities
        mock_vulnerabilities = [
            {
                'cve_id': 'CVE-2023-1234',
                'severity': 'medium',
                'description': 'Example vulnerability in test package',
                'affected_packages': ['test-package-1']
            },
            {
                'cve_id': 'CVE-2023-5678',
                'severity': 'high',
                'description': 'Critical security flaw in network component',
                'affected_packages': ['network-lib']
            }
        ]
        
        self.vulnerabilities = mock_vulnerabilities
        
        for vuln in mock_vulnerabilities:
            print(f"🔍 Found vulnerability: {vuln['cve_id']} ({vuln['severity']}) - {vuln['description']}")
        
        return len(mock_vulnerabilities)
    
    def simulate_security_updates(self):
        """Simulate applying security updates"""
        print("\n=== Simulating Security Updates ===")
        
        mock_updates = [
            {'package': 'system-security', 'from': '1.0.0', 'to': '1.0.1', 'status': 'success'},
            {'package': 'network-monitor', 'from': '2.1.0', 'to': '2.1.2', 'status': 'success'},
            {'package': 'wifi-driver', 'from': '3.4.1', 'to': '3.4.3', 'status': 'success'}
        ]
        
        for update in mock_updates:
            self.update_history.append({
                'timestamp': datetime.now().isoformat(),
                'package': update['package'],
                'from_version': update['from'],
                'to_version': update['to'],
                'success': update['status'] == 'success'
            })
            print(f"📦 Updated {update['package']}: {update['from']} → {update['to']} ✓")
        
        return len(mock_updates)
    
    def get_security_status(self):
        """Get security status"""
        critical_count = sum(1 for v in self.vulnerabilities if v['severity'] == 'critical')
        high_count = sum(1 for v in self.vulnerabilities if v['severity'] == 'high')
        
        if critical_count > 0:
            return 'critical'
        elif high_count > 0:
            return 'high_risk'
        else:
            return 'secure'

def main():
    """Main demonstration function"""
    print("🚀 WiFi Monitoring and Security System Demonstration")
    print("=" * 60)
    
    # Initialize components
    monitor = MockWiFiMonitor()
    security_mgr = MockSecurityManager()
    
    # Demonstrate monitoring
    suspicious_events = monitor.simulate_monitoring()
    
    # Demonstrate security scanning
    vulnerabilities_found = security_mgr.simulate_security_scan()
    
    # Demonstrate security updates
    updates_applied = security_mgr.simulate_security_updates()
    
    # Generate reports
    print("\n=== System Status Report ===")
    status = monitor.get_status_report()
    for key, value in status.items():
        print(f"{key}: {value}")
    
    print(f"\nSecurity Status: {security_mgr.get_security_status()}")
    
    # Summary
    print("\n=== Demonstration Summary ===")
    print(f"✓ Monitored {len(monitor.connected_devices)} network devices")
    print(f"⚠ Detected {suspicious_events} suspicious events")
    print(f"🔍 Found {vulnerabilities_found} security vulnerabilities")
    print(f"📦 Applied {updates_applied} security updates")
    print(f"📊 System status: {status['system_status']}")
    
    # Export sample data
    sample_events = {
        'monitoring_events': monitor.suspicious_events,
        'vulnerabilities': security_mgr.vulnerabilities,
        'update_history': security_mgr.update_history,
        'generated_at': datetime.now().isoformat()
    }
    
    with open('demo_output.json', 'w') as f:
        json.dump(sample_events, f, indent=2)
    
    print("\n✅ Demonstration complete! Sample data exported to 'demo_output.json'")
    print("\nThis demonstrates the core functionality of the WiFi monitoring system:")
    print("- Real-time device monitoring and suspicious activity detection")
    print("- Security vulnerability scanning and alerting")
    print("- Automated security update management")
    print("- Comprehensive reporting and data export")

if __name__ == "__main__":
    main()
