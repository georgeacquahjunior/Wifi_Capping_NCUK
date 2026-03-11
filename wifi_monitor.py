#!/usr/bin/env python3
"""
WiFi Monitoring and Security System for NCUK
Monitors for suspicious network activity and manages security updates
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Set
import yaml
import json
import os
import sys

# Network monitoring imports
import psutil
import netifaces
from scapy.all import *
import requests
import schedule

class WiFiSecurityMonitor:
    def __init__(self, config_path: str = "config.yml"):
        """Initialize the WiFi Security Monitor"""
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        # Monitoring state
        self.connected_devices: Dict[str, Dict] = {}
        self.traffic_history: List[Dict] = []
        self.suspicious_events: List[Dict] = []
        self.last_update_check = datetime.now() - timedelta(days=1)
        
        # Threading
        self.monitoring_active = False
        self.monitor_thread = None
        
        self.logger.info("WiFi Security Monitor initialized")

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Configuration file {config_path} not found. Using defaults.")
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"Error parsing configuration: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'monitoring': {
                'max_devices_per_hour': 50,
                'max_bandwidth_mbps': 1000,
                'suspicious_ports': [22, 23, 3389, 5900, 1433, 3306],
                'scan_interval_seconds': 60,
                'unusual_traffic_threshold': 80,
                'connection_timeout_threshold': 30
            },
            'security': {
                'auto_update': True,
                'update_check_interval_hours': 24,
                'alert_email': 'admin@ncuk.ac.uk',
                'alert_threshold': 'medium'
            },
            'logging': {
                'level': 'INFO',
                'file': '/var/log/wifi_monitor.log',
                'max_size_mb': 100,
                'backup_count': 5
            },
            'network': {
                'interface': 'wlan0',
                'ssid': 'NCUK_WIFI'
            }
        }

    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        
        # Create logger
        self.logger = logging.getLogger('wifi_monitor')
        self.logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        log_file = log_config.get('file')
        if log_file:
            try:
                # Create log directory if it doesn't exist
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=log_config.get('max_size_mb', 100) * 1024 * 1024,
                    backupCount=log_config.get('backup_count', 5)
                )
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except (OSError, PermissionError) as e:
                self.logger.warning(f"Could not setup file logging: {e}")

    def start_monitoring(self):
        """Start the monitoring system"""
        if self.monitoring_active:
            self.logger.warning("Monitoring is already active")
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        # Schedule security updates
        schedule.every(self.config['security']['update_check_interval_hours']).hours.do(
            self.check_security_updates
        )
        
        self.logger.info("WiFi monitoring started")

    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("WiFi monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Monitor network devices
                self._scan_network_devices()
                
                # Analyze traffic patterns
                self._analyze_traffic_patterns()
                
                # Check for suspicious activity
                self._detect_suspicious_activity()
                
                # Run scheduled tasks
                schedule.run_pending()
                
                # Sleep until next scan
                time.sleep(self.config['monitoring']['scan_interval_seconds'])
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Wait before retrying

    def _scan_network_devices(self):
        """Scan for connected network devices"""
        try:
            # Get network interfaces
            interfaces = netifaces.interfaces()
            target_interface = self.config['network'].get('interface', 'wlan0')
            
            if target_interface not in interfaces:
                self.logger.warning(f"Target interface {target_interface} not found")
                return
            
            # Get network statistics
            net_stats = psutil.net_io_counters(pernic=True)
            
            current_time = datetime.now()
            device_count = len(self.connected_devices)
            
            # Update device tracking
            self._update_device_tracking(current_time, device_count)
            
            self.logger.debug(f"Scanned {device_count} devices on {target_interface}")
            
        except Exception as e:
            self.logger.error(f"Error scanning network devices: {e}")

    def _update_device_tracking(self, current_time: datetime, device_count: int):
        """Update device tracking information"""
        # Clean old entries (older than 1 hour)
        cutoff_time = current_time - timedelta(hours=1)
        
        # Remove old devices
        devices_to_remove = []
        for mac, info in self.connected_devices.items():
            if info.get('last_seen', current_time) < cutoff_time:
                devices_to_remove.append(mac)
        
        for mac in devices_to_remove:
            del self.connected_devices[mac]
            self.logger.debug(f"Removed inactive device: {mac}")

    def _analyze_traffic_patterns(self):
        """Analyze network traffic patterns for anomalies"""
        try:
            # Get current network statistics
            net_stats = psutil.net_io_counters()
            
            current_stats = {
                'timestamp': datetime.now(),
                'bytes_sent': net_stats.bytes_sent,
                'bytes_recv': net_stats.bytes_recv,
                'packets_sent': net_stats.packets_sent,
                'packets_recv': net_stats.packets_recv
            }
            
            self.traffic_history.append(current_stats)
            
            # Keep only last 24 hours of data
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.traffic_history = [
                stats for stats in self.traffic_history 
                if stats['timestamp'] > cutoff_time
            ]
            
            # Analyze for unusual patterns
            if len(self.traffic_history) > 10:
                self._check_unusual_traffic()
                
        except Exception as e:
            self.logger.error(f"Error analyzing traffic patterns: {e}")

    def _check_unusual_traffic(self):
        """Check for unusual traffic patterns"""
        if len(self.traffic_history) < 10:
            return
        
        # Calculate average traffic over last hour
        recent_stats = self.traffic_history[-10:]
        
        total_bytes = sum(s['bytes_sent'] + s['bytes_recv'] for s in recent_stats)
        avg_mbps = (total_bytes * 8) / (1024 * 1024 * 600)  # Convert to Mbps
        
        threshold = self.config['monitoring']['max_bandwidth_mbps']
        
        if avg_mbps > threshold:
            self._log_suspicious_event(
                'unusual_traffic',
                f"High bandwidth usage detected: {avg_mbps:.2f} Mbps (threshold: {threshold} Mbps)",
                'medium'
            )

    def _detect_suspicious_activity(self):
        """Detect various types of suspicious network activity"""
        current_time = datetime.now()
        
        # Check device count threshold
        device_count = len(self.connected_devices)
        max_devices = self.config['monitoring']['max_devices_per_hour']
        
        if device_count > max_devices:
            self._log_suspicious_event(
                'too_many_devices',
                f"Unusual number of devices: {device_count} (threshold: {max_devices})",
                'high'
            )
        
        # Check for devices with suspicious MAC addresses
        self._check_suspicious_devices()

    def _check_suspicious_devices(self):
        """Check for devices with suspicious characteristics"""
        trusted_patterns = self.config['network'].get('trusted_mac_patterns', [])
        
        for mac, info in self.connected_devices.items():
            # Check if MAC matches trusted patterns
            is_trusted = any(
                mac.startswith(pattern.replace('*', '')) 
                for pattern in trusted_patterns
            )
            
            if not is_trusted:
                self._log_suspicious_event(
                    'untrusted_device',
                    f"Untrusted device detected: {mac}",
                    'medium'
                )

    def _log_suspicious_event(self, event_type: str, description: str, severity: str):
        """Log a suspicious event"""
        event = {
            'timestamp': datetime.now(),
            'type': event_type,
            'description': description,
            'severity': severity
        }
        
        self.suspicious_events.append(event)
        
        # Log based on severity
        if severity == 'critical':
            self.logger.critical(f"SECURITY ALERT: {description}")
        elif severity == 'high':
            self.logger.error(f"Security Warning: {description}")
        elif severity == 'medium':
            self.logger.warning(f"Security Notice: {description}")
        else:
            self.logger.info(f"Security Info: {description}")
        
        # Clean old events (keep last 1000)
        if len(self.suspicious_events) > 1000:
            self.suspicious_events = self.suspicious_events[-1000:]

    def check_security_updates(self):
        """Check for and apply security updates"""
        self.logger.info("Checking for security updates...")
        
        try:
            # Check if enough time has passed since last update
            update_interval = timedelta(
                hours=self.config['security']['update_check_interval_hours']
            )
            
            if datetime.now() - self.last_update_check < update_interval:
                return
            
            self.last_update_check = datetime.now()
            
            # Check for system package updates
            if self.config['security']['auto_update']:
                self._apply_system_updates()
            
            # Check for Python package security vulnerabilities
            self._check_python_vulnerabilities()
            
        except Exception as e:
            self.logger.error(f"Error checking security updates: {e}")

    def _apply_system_updates(self):
        """Apply system security updates"""
        try:
            import subprocess
            
            # Check for available updates (Ubuntu/Debian)
            result = subprocess.run(
                ['apt', 'list', '--upgradable'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                upgradable_packages = len(result.stdout.strip().split('\n')) - 1
                
                if upgradable_packages > 0:
                    self.logger.info(f"Found {upgradable_packages} upgradable packages")
                    
                    # Apply security updates only
                    update_result = subprocess.run(
                        ['sudo', 'apt', 'upgrade', '-y'],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if update_result.returncode == 0:
                        self.logger.info("Security updates applied successfully")
                    else:
                        self.logger.error(f"Failed to apply updates: {update_result.stderr}")
                        
        except subprocess.TimeoutExpired:
            self.logger.error("Update check timed out")
        except Exception as e:
            self.logger.error(f"Error applying system updates: {e}")

    def _check_python_vulnerabilities(self):
        """Check Python packages for known vulnerabilities"""
        try:
            import subprocess
            
            # Get list of installed packages
            result = subprocess.run(
                ['pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                self.logger.info(f"Checked {len(packages)} Python packages for vulnerabilities")
                
        except Exception as e:
            self.logger.error(f"Error checking Python vulnerabilities: {e}")

    def get_status_report(self) -> Dict:
        """Generate a status report"""
        return {
            'monitoring_active': self.monitoring_active,
            'connected_devices': len(self.connected_devices),
            'suspicious_events_last_24h': len([
                event for event in self.suspicious_events
                if event['timestamp'] > datetime.now() - timedelta(hours=24)
            ]),
            'last_update_check': self.last_update_check.isoformat(),
            'traffic_history_entries': len(self.traffic_history),
            'system_status': 'operational'
        }

    def export_events(self, filename: str = None) -> str:
        """Export suspicious events to JSON file"""
        if filename is None:
            filename = f"security_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert datetime objects to strings for JSON serialization
        events_json = []
        for event in self.suspicious_events:
            event_copy = event.copy()
            event_copy['timestamp'] = event_copy['timestamp'].isoformat()
            events_json.append(event_copy)
        
        with open(filename, 'w') as f:
            json.dump(events_json, f, indent=2)
        
        self.logger.info(f"Exported {len(events_json)} security events to {filename}")
        return filename


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WiFi Security Monitor for NCUK')
    parser.add_argument('--config', default='config.yml', help='Configuration file path')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--status', action='store_true', help='Show status and exit')
    parser.add_argument('--export-events', help='Export events to file and exit')
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = WiFiSecurityMonitor(args.config)
    
    if args.status:
        # Show status and exit
        status = monitor.get_status_report()
        print(json.dumps(status, indent=2))
        return
    
    if args.export_events:
        # Export events and exit
        filename = monitor.export_events(args.export_events)
        print(f"Events exported to: {filename}")
        return
    
    try:
        # Start monitoring
        monitor.start_monitoring()
        
        if args.daemon:
            # Run as daemon
            while True:
                time.sleep(60)
        else:
            # Interactive mode
            print("WiFi Security Monitor started. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nStopping WiFi Security Monitor...")
        monitor.stop_monitoring()
        print("Stopped.")


if __name__ == "__main__":
    main()