#!/usr/bin/env python3
"""
Security Update Manager for WiFi Monitoring System
Handles automated security updates and vulnerability scanning
"""

import os
import sys
import json
import logging
import subprocess
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yaml
from dataclasses import dataclass

@dataclass
class SecurityUpdate:
    """Represents a security update"""
    package_name: str
    current_version: str
    new_version: str
    severity: str
    description: str
    cve_ids: List[str]

@dataclass
class Vulnerability:
    """Represents a security vulnerability"""
    cve_id: str
    severity: str
    description: str
    affected_packages: List[str]
    fixed_version: Optional[str] = None

class SecurityUpdateManager:
    """Manages security updates and vulnerability scanning"""
    
    def __init__(self, config_path: str = "config.yml"):
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.update_history: List[Dict] = []
        self.vulnerabilities: List[Vulnerability] = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"Error parsing configuration: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'security': {
                'auto_update': True,
                'update_check_interval_hours': 24,
                'security_sources': [
                    "https://api.github.com/repos/pypa/advisory-database/contents/vulns"
                ],
                'alert_threshold': 'medium'
            },
            'logging': {
                'level': 'INFO'
            }
        }

    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get('logging', {}).get('level', 'INFO'))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('security_manager')

    def check_system_updates(self) -> List[SecurityUpdate]:
        """Check for available system security updates"""
        updates = []
        
        try:
            # Check for Ubuntu/Debian updates
            if self._is_debian_based():
                updates.extend(self._check_apt_updates())
            
            # Check for Python package updates
            updates.extend(self._check_pip_updates())
            
            self.logger.info(f"Found {len(updates)} available security updates")
            return updates
            
        except Exception as e:
            self.logger.error(f"Error checking system updates: {e}")
            return []

    def _is_debian_based(self) -> bool:
        """Check if the system is Debian-based"""
        return os.path.exists('/etc/debian_version')

    def _check_apt_updates(self) -> List[SecurityUpdate]:
        """Check for APT package updates"""
        updates = []
        
        try:
            # Update package list
            subprocess.run(['sudo', 'apt', 'update'], 
                         capture_output=True, timeout=60)
            
            # Get upgradable packages
            result = subprocess.run(
                ['apt', 'list', '--upgradable', '--quiet'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if '/' in line and '[upgradable' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            package_name = parts[0].split('/')[0]
                            new_version = parts[1]
                            
                            # Check if it's a security update
                            if self._is_security_update(package_name, new_version):
                                updates.append(SecurityUpdate(
                                    package_name=package_name,
                                    current_version="unknown",
                                    new_version=new_version,
                                    severity="medium",
                                    description=f"Security update for {package_name}",
                                    cve_ids=[]
                                ))
            
        except subprocess.TimeoutExpired:
            self.logger.error("APT update check timed out")
        except Exception as e:
            self.logger.error(f"Error checking APT updates: {e}")
        
        return updates

    def _check_pip_updates(self) -> List[SecurityUpdate]:
        """Check for Python package security updates"""
        updates = []
        
        try:
            # Get list of outdated packages
            result = subprocess.run(
                ['pip', 'list', '--outdated', '--format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                outdated_packages = json.loads(result.stdout)
                
                for package in outdated_packages:
                    # Check if package has known vulnerabilities
                    vulnerabilities = self._check_package_vulnerabilities(
                        package['name'], 
                        package['version']
                    )
                    
                    if vulnerabilities:
                        updates.append(SecurityUpdate(
                            package_name=package['name'],
                            current_version=package['version'],
                            new_version=package['latest_version'],
                            severity=self._get_max_severity(vulnerabilities),
                            description=f"Security update for {package['name']}",
                            cve_ids=[v.cve_id for v in vulnerabilities]
                        ))
            
        except Exception as e:
            self.logger.error(f"Error checking pip updates: {e}")
        
        return updates

    def _is_security_update(self, package_name: str, version: str) -> bool:
        """Check if a package update is security-related"""
        # Simple heuristic - in a real implementation, this would check
        # against security databases
        security_keywords = ['security', 'cve', 'vulnerability', 'fix']
        return any(keyword in package_name.lower() for keyword in security_keywords)

    def _check_package_vulnerabilities(self, package_name: str, version: str) -> List[Vulnerability]:
        """Check if a package version has known vulnerabilities"""
        vulnerabilities = []
        
        try:
            # This is a simplified implementation
            # In production, you would check against actual vulnerability databases
            
            # Example: Check against PyPI advisory database
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # This would need actual vulnerability checking logic
                # For now, return empty list
                pass
                
        except Exception as e:
            self.logger.debug(f"Error checking vulnerabilities for {package_name}: {e}")
        
        return vulnerabilities

    def _get_max_severity(self, vulnerabilities: List[Vulnerability]) -> str:
        """Get the maximum severity from a list of vulnerabilities"""
        severity_order = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        
        max_severity = 'low'
        max_value = 0
        
        for vuln in vulnerabilities:
            value = severity_order.get(vuln.severity, 0)
            if value > max_value:
                max_value = value
                max_severity = vuln.severity
        
        return max_severity

    def apply_updates(self, updates: List[SecurityUpdate], 
                     auto_approve: bool = False) -> Dict[str, bool]:
        """Apply security updates"""
        results = {}
        
        if not auto_approve and not self.config['security']['auto_update']:
            self.logger.info("Auto-update disabled, skipping update application")
            return results
        
        for update in updates:
            try:
                success = self._apply_single_update(update)
                results[update.package_name] = success
                
                # Log the update
                self.update_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'package': update.package_name,
                    'from_version': update.current_version,
                    'to_version': update.new_version,
                    'success': success,
                    'severity': update.severity
                })
                
            except Exception as e:
                self.logger.error(f"Failed to update {update.package_name}: {e}")
                results[update.package_name] = False
        
        return results

    def _apply_single_update(self, update: SecurityUpdate) -> bool:
        """Apply a single security update"""
        try:
            if update.package_name in self._get_system_packages():
                # System package update
                result = subprocess.run(
                    ['sudo', 'apt', 'install', '-y', update.package_name],
                    capture_output=True,
                    timeout=300
                )
                success = result.returncode == 0
            else:
                # Python package update
                result = subprocess.run(
                    ['pip', 'install', '--upgrade', update.package_name],
                    capture_output=True,
                    timeout=120
                )
                success = result.returncode == 0
            
            if success:
                self.logger.info(f"Successfully updated {update.package_name} to {update.new_version}")
            else:
                self.logger.error(f"Failed to update {update.package_name}: {result.stderr}")
            
            return success
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Update timeout for {update.package_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error updating {update.package_name}: {e}")
            return False

    def _get_system_packages(self) -> List[str]:
        """Get list of system packages"""
        try:
            result = subprocess.run(
                ['dpkg', '--get-selections'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return [line.split()[0] for line in result.stdout.strip().split('\n')]
            
        except Exception as e:
            self.logger.debug(f"Error getting system packages: {e}")
        
        return []

    def scan_vulnerabilities(self) -> List[Vulnerability]:
        """Perform a comprehensive vulnerability scan"""
        self.logger.info("Starting vulnerability scan...")
        
        vulnerabilities = []
        
        try:
            # Scan system packages
            vulnerabilities.extend(self._scan_system_vulnerabilities())
            
            # Scan Python packages
            vulnerabilities.extend(self._scan_python_vulnerabilities())
            
            # Scan configuration files
            vulnerabilities.extend(self._scan_config_vulnerabilities())
            
            self.vulnerabilities = vulnerabilities
            self.logger.info(f"Vulnerability scan complete. Found {len(vulnerabilities)} issues.")
            
        except Exception as e:
            self.logger.error(f"Error during vulnerability scan: {e}")
        
        return vulnerabilities

    def _scan_system_vulnerabilities(self) -> List[Vulnerability]:
        """Scan system packages for vulnerabilities"""
        vulnerabilities = []
        
        # This would integrate with actual vulnerability databases
        # For now, return empty list
        
        return vulnerabilities

    def _scan_python_vulnerabilities(self) -> List[Vulnerability]:
        """Scan Python packages for vulnerabilities"""
        vulnerabilities = []
        
        try:
            # Get installed packages
            result = subprocess.run(
                ['pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                
                # Check each package (simplified implementation)
                for package in packages:
                    # This would check against actual vulnerability databases
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error scanning Python vulnerabilities: {e}")
        
        return vulnerabilities

    def _scan_config_vulnerabilities(self) -> List[Vulnerability]:
        """Scan configuration files for security issues"""
        vulnerabilities = []
        
        try:
            # Check for common configuration issues
            config_files = ['config.yml', '/etc/ssh/sshd_config', '/etc/nginx/nginx.conf']
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    vulns = self._check_config_security(config_file)
                    vulnerabilities.extend(vulns)
                    
        except Exception as e:
            self.logger.error(f"Error scanning configuration vulnerabilities: {e}")
        
        return vulnerabilities

    def _check_config_security(self, config_file: str) -> List[Vulnerability]:
        """Check a configuration file for security issues"""
        vulnerabilities = []
        
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Check for common security issues
            if 'password' in content.lower() and '=' in content:
                vulnerabilities.append(Vulnerability(
                    cve_id="CONFIG-001",
                    severity="medium",
                    description=f"Potential password in configuration file: {config_file}",
                    affected_packages=[config_file]
                ))
            
            if 'debug: true' in content.lower():
                vulnerabilities.append(Vulnerability(
                    cve_id="CONFIG-002",
                    severity="low",
                    description=f"Debug mode enabled in: {config_file}",
                    affected_packages=[config_file]
                ))
                
        except Exception as e:
            self.logger.debug(f"Error checking config security for {config_file}: {e}")
        
        return vulnerabilities

    def generate_security_report(self) -> Dict:
        """Generate a comprehensive security report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities': [
                {
                    'cve_id': v.cve_id,
                    'severity': v.severity,
                    'description': v.description,
                    'affected_packages': v.affected_packages
                }
                for v in self.vulnerabilities
            ],
            'update_history': self.update_history[-50:],  # Last 50 updates
            'last_scan': datetime.now().isoformat(),
            'security_status': self._get_security_status()
        }

    def _get_security_status(self) -> str:
        """Get overall security status"""
        if not self.vulnerabilities:
            return "secure"
        
        critical_count = sum(1 for v in self.vulnerabilities if v.severity == 'critical')
        high_count = sum(1 for v in self.vulnerabilities if v.severity == 'high')
        
        if critical_count > 0:
            return "critical"
        elif high_count > 0:
            return "high_risk"
        else:
            return "low_risk"

    def export_report(self, filename: str = None) -> str:
        """Export security report to file"""
        if filename is None:
            filename = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = self.generate_security_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Security report exported to {filename}")
        return filename


def main():
    """Main entry point for security update manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Security Update Manager')
    parser.add_argument('--config', default='config.yml', help='Configuration file path')
    parser.add_argument('--check', action='store_true', help='Check for updates only')
    parser.add_argument('--scan', action='store_true', help='Perform vulnerability scan')
    parser.add_argument('--apply', action='store_true', help='Apply available updates')
    parser.add_argument('--report', help='Generate security report to file')
    parser.add_argument('--force', action='store_true', help='Force apply updates')
    
    args = parser.parse_args()
    
    manager = SecurityUpdateManager(args.config)
    
    if args.scan:
        vulnerabilities = manager.scan_vulnerabilities()
        print(f"Found {len(vulnerabilities)} vulnerabilities")
        for vuln in vulnerabilities:
            print(f"  {vuln.severity.upper()}: {vuln.description}")
    
    if args.check or args.apply:
        updates = manager.check_system_updates()
        print(f"Found {len(updates)} available security updates")
        
        for update in updates:
            print(f"  {update.package_name}: {update.current_version} -> {update.new_version} ({update.severity})")
        
        if args.apply and updates:
            results = manager.apply_updates(updates, auto_approve=args.force)
            
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            print(f"Applied {successful}/{total} updates successfully")
    
    if args.report:
        filename = manager.export_report(args.report)
        print(f"Security report saved to {filename}")


if __name__ == "__main__":
    main()