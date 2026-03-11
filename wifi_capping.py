#!/usr/bin/env python3
"""
Wi-Fi Usage Capping System for NCUK

This module implements a Wi-Fi data usage monitoring and capping system
that automatically disconnects Wi-Fi when usage exceeds 20GB.
"""

import os
import sys
import json
import time
import logging
import subprocess
import psutil
from datetime import datetime, timedelta
from pathlib import Path


class WiFiUsageCapper:
    """
    Wi-Fi usage monitoring and capping system.
    
    Monitors network data usage and disconnects Wi-Fi when the 20GB limit is reached.
    """
    
    def __init__(self, config_path="config.json"):
        """Initialize the Wi-Fi usage capper."""
        self.config_path = config_path
        self.data_file = "usage_data.json"
        self.load_config()
        self.setup_logging()
        self.usage_data = self.load_usage_data()
        
    def load_config(self):
        """Load configuration from file or create default config."""
        default_config = {
            "data_limit_gb": 20,
            "reset_period_days": 30,
            "check_interval_seconds": 60,
            "wifi_interface": "wlan0",
            "log_level": "INFO"
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                # Ensure all required keys exist
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('wifi_capping.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_usage_data(self):
        """Load usage data from file or create new data structure."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                # Check if data needs to be reset based on period
                if self.should_reset_usage(data.get('last_reset')):
                    self.logger.info("Resetting usage data for new period")
                    return self.create_new_usage_data()
                return data
            except Exception as e:
                self.logger.error(f"Error loading usage data: {e}")
                return self.create_new_usage_data()
        else:
            return self.create_new_usage_data()
    
    def create_new_usage_data(self):
        """Create new usage data structure."""
        return {
            "total_bytes": 0,
            "last_reset": datetime.now().isoformat(),
            "last_check": None,
            "is_disconnected": False,
            "disconnect_time": None
        }
    
    def should_reset_usage(self, last_reset_str):
        """Check if usage data should be reset based on configured period."""
        if not last_reset_str:
            return True
        
        try:
            last_reset = datetime.fromisoformat(last_reset_str)
            days_passed = (datetime.now() - last_reset).days
            return days_passed >= self.config["reset_period_days"]
        except Exception:
            return True
    
    def save_usage_data(self):
        """Save usage data to file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving usage data: {e}")
    
    def get_network_stats(self):
        """Get current network statistics."""
        try:
            stats = psutil.net_io_counters()
            return stats.bytes_sent + stats.bytes_recv
        except Exception as e:
            self.logger.error(f"Error getting network stats: {e}")
            return 0
    
    def update_usage(self):
        """Update usage data with current network statistics."""
        current_bytes = self.get_network_stats()
        
        if self.usage_data["last_check"] is None:
            # First run, just record current stats
            self.usage_data["last_check"] = current_bytes
            self.usage_data["total_bytes"] = 0
        else:
            # Calculate new data usage
            bytes_used = current_bytes - self.usage_data["last_check"]
            if bytes_used > 0:  # Only count positive usage (handles counter resets)
                self.usage_data["total_bytes"] += bytes_used
            self.usage_data["last_check"] = current_bytes
        
        self.save_usage_data()
    
    def get_usage_gb(self):
        """Get current usage in GB."""
        return self.usage_data["total_bytes"] / (1024 ** 3)
    
    def is_limit_exceeded(self):
        """Check if data limit has been exceeded."""
        return self.get_usage_gb() >= self.config["data_limit_gb"]
    
    def get_wifi_interface(self):
        """Get the current Wi-Fi interface name."""
        try:
            # Try to find active wireless interface
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'IEEE 802.11' in line:
                        interface = line.split()[0]
                        return interface
            # Fallback to configured interface
            return self.config["wifi_interface"]
        except Exception:
            return self.config["wifi_interface"]
    
    def disconnect_wifi(self):
        """Disconnect Wi-Fi connection."""
        try:
            interface = self.get_wifi_interface()
            
            # Try multiple methods to disconnect
            methods = [
                ['nmcli', 'device', 'disconnect', interface],
                ['ifconfig', interface, 'down'],
                ['ip', 'link', 'set', interface, 'down']
            ]
            
            for method in methods:
                try:
                    result = subprocess.run(method, capture_output=True, text=True)
                    if result.returncode == 0:
                        self.logger.info(f"Wi-Fi disconnected using {method[0]}")
                        self.usage_data["is_disconnected"] = True
                        self.usage_data["disconnect_time"] = datetime.now().isoformat()
                        self.save_usage_data()
                        return True
                except Exception as e:
                    self.logger.debug(f"Failed to disconnect using {method[0]}: {e}")
                    continue
            
            self.logger.error("Failed to disconnect Wi-Fi using all available methods")
            return False
            
        except Exception as e:
            self.logger.error(f"Error disconnecting Wi-Fi: {e}")
            return False
    
    def reconnect_wifi(self):
        """Reconnect Wi-Fi (for manual override or reset)."""
        try:
            interface = self.get_wifi_interface()
            
            # Try to reconnect
            methods = [
                ['nmcli', 'device', 'connect', interface],
                ['ifconfig', interface, 'up'],
                ['ip', 'link', 'set', interface, 'up']
            ]
            
            for method in methods:
                try:
                    result = subprocess.run(method, capture_output=True, text=True)
                    if result.returncode == 0:
                        self.logger.info(f"Wi-Fi reconnected using {method[0]}")
                        self.usage_data["is_disconnected"] = False
                        self.usage_data["disconnect_time"] = None
                        self.save_usage_data()
                        return True
                except Exception as e:
                    self.logger.debug(f"Failed to reconnect using {method[0]}: {e}")
                    continue
            
            self.logger.error("Failed to reconnect Wi-Fi using all available methods")
            return False
            
        except Exception as e:
            self.logger.error(f"Error reconnecting Wi-Fi: {e}")
            return False
    
    def get_status(self):
        """Get current status information."""
        usage_gb = self.get_usage_gb()
        limit_gb = self.config["data_limit_gb"]
        percentage = (usage_gb / limit_gb) * 100
        
        status = {
            "usage_gb": round(usage_gb, 2),
            "limit_gb": limit_gb,
            "percentage": round(percentage, 1),
            "is_disconnected": self.usage_data["is_disconnected"],
            "disconnect_time": self.usage_data.get("disconnect_time"),
            "last_reset": self.usage_data["last_reset"]
        }
        
        return status
    
    def monitor_loop(self):
        """Main monitoring loop."""
        self.logger.info("Starting Wi-Fi usage monitoring...")
        
        try:
            while True:
                self.update_usage()
                status = self.get_status()
                
                self.logger.info(f"Current usage: {status['usage_gb']:.2f}GB / {status['limit_gb']}GB ({status['percentage']:.1f}%)")
                
                if not self.usage_data["is_disconnected"] and self.is_limit_exceeded():
                    self.logger.warning(f"Data limit exceeded! Disconnecting Wi-Fi...")
                    if self.disconnect_wifi():
                        self.logger.info("Wi-Fi successfully disconnected")
                    else:
                        self.logger.error("Failed to disconnect Wi-Fi")
                
                time.sleep(self.config["check_interval_seconds"])
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
    
    def reset_usage(self):
        """Manually reset usage data."""
        self.usage_data = self.create_new_usage_data()
        self.save_usage_data()
        self.logger.info("Usage data reset")
        
        # Reconnect if currently disconnected
        if self.usage_data["is_disconnected"]:
            self.reconnect_wifi()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Wi-Fi Usage Capping System")
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--reset', action='store_true', help='Reset usage data')
    parser.add_argument('--reconnect', action='store_true', help='Reconnect Wi-Fi')
    parser.add_argument('--monitor', action='store_true', help='Start monitoring (default)')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    
    args = parser.parse_args()
    
    capper = WiFiUsageCapper(args.config)
    
    if args.status:
        status = capper.get_status()
        print(f"Current Usage: {status['usage_gb']:.2f}GB / {status['limit_gb']}GB ({status['percentage']:.1f}%)")
        print(f"Status: {'DISCONNECTED' if status['is_disconnected'] else 'CONNECTED'}")
        if status['disconnect_time']:
            print(f"Disconnected at: {status['disconnect_time']}")
        print(f"Last reset: {status['last_reset']}")
    elif args.reset:
        capper.reset_usage()
        print("Usage data reset successfully")
    elif args.reconnect:
        if capper.reconnect_wifi():
            print("Wi-Fi reconnected successfully")
        else:
            print("Failed to reconnect Wi-Fi")
    else:
        # Default action is to monitor
        capper.monitor_loop()


if __name__ == "__main__":
    main()