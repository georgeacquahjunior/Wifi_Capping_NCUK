"""
Main WiFi Capping System Application

This is the main orchestrator that ties together all the components:
- Network encryption management
- Access control policies
- Bandwidth management
- Configuration management
- Monitoring and logging
"""

import os
import sys
import yaml
import logging
import signal
import time
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from encryption import NetworkEncryption, EncryptionType, SecurityLevel
from access_control import AccessControl, UserRole, AccessLevel
from bandwidth import BandwidthManager, TrafficClass


class WiFiCappingSystem:
    """Main WiFi Capping System application."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/system_config.yaml"
        self.config = {}
        self.running = False
        
        # Core components
        self.encryption_manager = None
        self.access_control = None
        self.bandwidth_manager = None
        
        # Setup logging
        self._setup_logging()
        
        # Load configuration
        self._load_configuration()
        
        # Initialize components
        self._initialize_components()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler("logs/wifi_system.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("WiFi Capping System starting up")
    
    def _load_configuration(self):
        """Load system configuration from YAML file."""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    self.config = yaml.safe_load(f)
                self.logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.logger.warning(f"Configuration file not found: {self.config_path}")
                self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create a default configuration."""
        self.config = {
            "network": {
                "primary_ssid": "NCUK-WiFi",
                "guest_ssid": "NCUK-Guest",
                "interface": "wlan0"
            },
            "encryption": {
                "default_type": "wpa3-psk"
            },
            "access_control": {
                "mac_filtering": {"enabled": True}
            },
            "bandwidth": {
                "interface": "wlan0",
                "limits": {
                    "restricted": {"download": 2, "upload": 1},
                    "basic": {"download": 10, "upload": 5},
                    "standard": {"download": 50, "upload": 25},
                    "premium": {"download": 200, "upload": 100}
                }
            }
        }
        self.logger.info("Using default configuration")
    
    def _initialize_components(self):
        """Initialize all system components."""
        try:
            # Initialize encryption manager
            self.encryption_manager = NetworkEncryption()
            self.logger.info("Encryption manager initialized")
            
            # Initialize access control
            self.access_control = AccessControl()
            self.logger.info("Access control initialized")
            
            # Initialize bandwidth manager
            interface = self.config.get("bandwidth", {}).get("interface", "wlan0")
            self.bandwidth_manager = BandwidthManager(interface=interface)
            self.logger.info("Bandwidth manager initialized")
            
            # Create default network configurations
            self._setup_default_networks()
            
            # Create default users
            self._setup_default_users()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _setup_default_networks(self):
        """Setup default network configurations."""
        try:
            # Primary WiFi network
            primary_ssid = self.config.get("network", {}).get("primary_ssid", "NCUK-WiFi")
            self.encryption_manager.create_encryption_policy(
                network_id=primary_ssid,
                encryption_type=EncryptionType.WPA3_PSK,
                security_level=SecurityLevel.HIGH,
                psk=self.encryption_manager.generate_psk(primary_ssid, 24)
            )
            
            # Guest network
            guest_ssid = self.config.get("network", {}).get("guest_ssid", "NCUK-Guest")
            self.encryption_manager.create_encryption_policy(
                network_id=guest_ssid,
                encryption_type=EncryptionType.WPA2_PSK,
                security_level=SecurityLevel.MEDIUM,
                psk=self.encryption_manager.generate_psk(guest_ssid, 20)
            )
            
            self.logger.info("Default network configurations created")
            
        except Exception as e:
            self.logger.error(f"Failed to setup default networks: {e}")
    
    def _setup_default_users(self):
        """Setup default user accounts."""
        try:
            # Create admin user
            admin_user = self.access_control.create_user(
                username="admin",
                email="admin@ncuk.edu",
                role=UserRole.ADMIN,
                access_level=AccessLevel.UNLIMITED,
                password="admin123"  # Should be changed in production
            )
            
            # Create sample faculty user
            faculty_user = self.access_control.create_user(
                username="faculty.user",
                email="faculty@ncuk.edu",
                role=UserRole.FACULTY,
                access_level=AccessLevel.PREMIUM,
                mac_addresses=["AA:BB:CC:DD:EE:FF"]
            )
            
            # Create sample student user
            student_user = self.access_control.create_user(
                username="student.user",
                email="student@ncuk.edu",
                role=UserRole.STUDENT,
                access_level=AccessLevel.BASIC,
                mac_addresses=["11:22:33:44:55:66"]
            )
            
            # Set bandwidth limits based on access levels
            self._apply_bandwidth_limits()
            
            self.logger.info("Default user accounts created")
            
        except Exception as e:
            self.logger.error(f"Failed to setup default users: {e}")
    
    def _apply_bandwidth_limits(self):
        """Apply bandwidth limits to users based on their access levels."""
        try:
            bandwidth_config = self.config.get("bandwidth", {}).get("limits", {})
            
            for user in self.access_control.users.values():
                access_level = user.access_level.value
                limits = bandwidth_config.get(access_level, {"download": 10, "upload": 5})
                
                if limits["download"] > 0:  # -1 means unlimited
                    self.bandwidth_manager.set_user_bandwidth_limit(
                        user.user_id,
                        limits["download"],
                        limits["upload"],
                        priority=limits.get("priority", 50)
                    )
            
            self.logger.info("Bandwidth limits applied to users")
            
        except Exception as e:
            self.logger.error(f"Failed to apply bandwidth limits: {e}")
    
    def start(self):
        """Start the WiFi Capping System."""
        try:
            self.running = True
            self.logger.info("WiFi Capping System started successfully")
            
            # Start bandwidth monitoring
            self.bandwidth_manager.start_monitoring()
            
            # Main event loop
            self._main_loop()
            
        except Exception as e:
            self.logger.error(f"Error starting system: {e}")
            self.stop()
    
    def _main_loop(self):
        """Main system event loop."""
        while self.running:
            try:
                # Perform periodic tasks
                self._periodic_maintenance()
                
                # Sleep for a short time to prevent busy waiting
                time.sleep(10)
                
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _periodic_maintenance(self):
        """Perform periodic maintenance tasks."""
        try:
            # Clean up expired guest accounts
            self._cleanup_expired_guests()
            
            # Apply fair usage policies
            self.bandwidth_manager.enforce_fair_usage_policy()
            
            # Log current system status
            if datetime.now().minute % 10 == 0:  # Every 10 minutes
                self._log_system_status()
                
        except Exception as e:
            self.logger.error(f"Error in periodic maintenance: {e}")
    
    def _cleanup_expired_guests(self):
        """Remove expired guest accounts."""
        current_time = datetime.now()
        
        for user_id, user in list(self.access_control.users.items()):
            if user.role == UserRole.GUEST and user.expires_at:
                expiry = datetime.fromisoformat(user.expires_at)
                if current_time > expiry:
                    self.access_control.deactivate_user(user_id)
                    self.bandwidth_manager.remove_user_bandwidth_limit(user_id)
                    self.logger.info(f"Deactivated expired guest account: {user.username}")
    
    def _log_system_status(self):
        """Log current system status."""
        active_users = len([u for u in self.access_control.users.values() if u.is_active])
        total_policies = len(self.encryption_manager.encryption_policies)
        bandwidth_rules = len(self.bandwidth_manager.user_limits)
        
        self.logger.info(f"System Status - Active Users: {active_users}, "
                        f"Encryption Policies: {total_policies}, "
                        f"Bandwidth Rules: {bandwidth_rules}")
    
    def stop(self):
        """Stop the WiFi Capping System."""
        self.logger.info("Shutting down WiFi Capping System")
        self.running = False
        
        # Stop bandwidth monitoring
        if self.bandwidth_manager:
            self.bandwidth_manager.stop_monitoring()
        
        self.logger.info("WiFi Capping System stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}")
        self.stop()
    
    # API methods for external management
    
    def create_guest_access(self, duration_hours: int = 24) -> Dict:
        """Create temporary guest access."""
        return self.access_control.create_guest_access(duration_hours)
    
    def authorize_device(self, mac_address: str, username: str = None) -> bool:
        """Authorize a device for network access."""
        if username:
            user = None
            for u in self.access_control.users.values():
                if u.username == username:
                    user = u
                    break
            
            if user:
                return self.access_control.authorize_mac_address(mac_address, user.user_id)
        
        return self.access_control.authorize_mac_address(mac_address)
    
    def get_network_config(self, ssid: str) -> Optional[str]:
        """Get hostapd configuration for a network."""
        return self.encryption_manager.generate_hostapd_config(ssid)
    
    def get_usage_report(self) -> Dict:
        """Generate current usage report."""
        return self.bandwidth_manager.generate_usage_report()
    
    def update_user_bandwidth(self, username: str, download_mbps: float, upload_mbps: float) -> bool:
        """Update bandwidth limits for a user."""
        for user in self.access_control.users.values():
            if user.username == username:
                return self.bandwidth_manager.set_user_bandwidth_limit(
                    user.user_id, download_mbps, upload_mbps
                )
        return False
    
    def block_mac_address(self, mac_address: str) -> bool:
        """Block a MAC address from network access."""
        return self.access_control.add_mac_to_blacklist(mac_address)
    
    def unblock_mac_address(self, mac_address: str) -> bool:
        """Unblock a MAC address."""
        return self.access_control.remove_mac_from_blacklist(mac_address)
    
    def export_configuration(self) -> Dict:
        """Export complete system configuration."""
        return {
            "system_config": self.config,
            "encryption_policies": self.encryption_manager.list_policies(),
            "users": self.access_control.export_user_list(),
            "access_rules": self.access_control.export_access_rules(),
            "bandwidth_config": self.bandwidth_manager.export_configuration()
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="NCUK WiFi Capping System")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--daemon", "-d", action="store_true", help="Run as daemon")
    parser.add_argument("--test", "-t", action="store_true", help="Test configuration and exit")
    
    args = parser.parse_args()
    
    try:
        # Initialize system
        system = WiFiCappingSystem(config_path=args.config)
        
        if args.test:
            print("Configuration test passed")
            print(f"Networks configured: {len(system.encryption_manager.encryption_policies)}")
            print(f"Users configured: {len(system.access_control.users)}")
            return 0
        
        if args.daemon:
            # Daemon mode implementation would go here
            print("Daemon mode not implemented yet")
            return 1
        
        # Start the system
        system.start()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())