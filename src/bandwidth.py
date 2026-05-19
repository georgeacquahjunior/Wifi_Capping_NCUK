"""
Bandwidth Management Module for NCUK WiFi Capping System

This module handles bandwidth allocation, throttling, and monitoring:
- Per-user bandwidth limits
- Quality of Service (QoS) rules
- Traffic shaping and prioritization
- Usage monitoring and reporting
"""

import subprocess
import logging
import time
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import json
from threading import Thread, Lock

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available - some monitoring features will be disabled")

logger = logging.getLogger(__name__)


class TrafficClass(Enum):
    """Traffic classification for QoS."""
    CRITICAL = "critical"      # Administrative traffic
    HIGH = "high"              # Faculty, important services
    NORMAL = "normal"          # Staff, standard users
    LOW = "low"                # Students, general use
    GUEST = "guest"            # Guest access


class Protocol(Enum):
    """Network protocols for traffic rules."""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ALL = "all"


@dataclass
class BandwidthLimit:
    """Bandwidth limit configuration."""
    download_mbps: float
    upload_mbps: float
    burst_download_mbps: Optional[float] = None
    burst_upload_mbps: Optional[float] = None
    priority: int = 50  # 0-100, higher is better priority


@dataclass
class QosRule:
    """Quality of Service rule definition."""
    rule_id: str
    name: str
    protocol: Protocol
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    traffic_class: TrafficClass = TrafficClass.NORMAL
    bandwidth_limit: Optional[BandwidthLimit] = None
    enabled: bool = True


@dataclass
class UsageStats:
    """Network usage statistics."""
    user_id: str
    mac_address: str
    bytes_downloaded: int
    bytes_uploaded: int
    packets_downloaded: int
    packets_uploaded: int
    session_start: str
    last_seen: str
    current_download_rate: float  # Mbps
    current_upload_rate: float    # Mbps


class BandwidthManager:
    """Manages bandwidth allocation and traffic shaping."""
    
    def __init__(self, interface: str = "wlan0"):
        self.interface = interface
        self.user_limits: Dict[str, BandwidthLimit] = {}
        self.qos_rules: Dict[str, QosRule] = {}
        self.usage_stats: Dict[str, UsageStats] = {}
        self.active_sessions: Dict[str, Dict] = {}
        self.stats_lock = Lock()
        self.monitoring_thread = None
        self._initialize_traffic_control()
        self._load_default_rules()
    
    def _initialize_traffic_control(self):
        """Initialize Linux traffic control (tc) for the interface."""
        try:
            # Remove existing qdisc
            subprocess.run(
                ["tc", "qdisc", "del", "dev", self.interface, "root"],
                capture_output=True, check=False
            )
            
            # Add HTB (Hierarchical Token Bucket) root qdisc
            cmd = [
                "tc", "qdisc", "add", "dev", self.interface, "root", "handle", "1:",
                "htb", "default", "50"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to initialize traffic control: {result.stderr}")
                return False
            
            # Create root class with total bandwidth
            cmd = [
                "tc", "class", "add", "dev", self.interface, "parent", "1:",
                "classid", "1:1", "htb", "rate", "1000mbit", "ceil", "1000mbit"
            ]
            subprocess.run(cmd, capture_output=True)
            
            logger.info(f"Traffic control initialized on {self.interface}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize traffic control: {e}")
            return False
    
    def _load_default_rules(self):
        """Load default QoS rules for different traffic types."""
        # Critical traffic (admin, DNS, DHCP)
        self.add_qos_rule(
            "admin_traffic",
            "Administrative Traffic",
            Protocol.ALL,
            traffic_class=TrafficClass.CRITICAL,
            bandwidth_limit=BandwidthLimit(100, 100, priority=95)
        )
        
        # High priority for faculty
        self.add_qos_rule(
            "faculty_default",
            "Faculty Default Traffic",
            Protocol.ALL,
            traffic_class=TrafficClass.HIGH,
            bandwidth_limit=BandwidthLimit(50, 25, priority=80)
        )
        
        # Normal priority for staff
        self.add_qos_rule(
            "staff_default",
            "Staff Default Traffic",
            Protocol.ALL,
            traffic_class=TrafficClass.NORMAL,
            bandwidth_limit=BandwidthLimit(25, 10, priority=60)
        )
        
        # Lower priority for students
        self.add_qos_rule(
            "student_default",
            "Student Default Traffic",
            Protocol.ALL,
            traffic_class=TrafficClass.LOW,
            bandwidth_limit=BandwidthLimit(10, 5, priority=40)
        )
        
        # Restricted guest access
        self.add_qos_rule(
            "guest_default",
            "Guest Default Traffic",
            Protocol.ALL,
            traffic_class=TrafficClass.GUEST,
            bandwidth_limit=BandwidthLimit(5, 2, priority=20)
        )
        
        logger.info("Default QoS rules loaded")
    
    def add_qos_rule(self,
                     rule_id: str,
                     name: str,
                     protocol: Protocol,
                     src_port: int = None,
                     dst_port: int = None,
                     traffic_class: TrafficClass = TrafficClass.NORMAL,
                     bandwidth_limit: BandwidthLimit = None) -> bool:
        """Add a new QoS rule."""
        rule = QosRule(
            rule_id=rule_id,
            name=name,
            protocol=protocol,
            src_port=src_port,
            dst_port=dst_port,
            traffic_class=traffic_class,
            bandwidth_limit=bandwidth_limit
        )
        
        self.qos_rules[rule_id] = rule
        logger.info(f"Added QoS rule: {name}")
        return True
    
    def set_user_bandwidth_limit(self,
                                user_id: str,
                                download_mbps: float,
                                upload_mbps: float,
                                priority: int = 50) -> bool:
        """Set bandwidth limits for a specific user."""
        limit = BandwidthLimit(
            download_mbps=download_mbps,
            upload_mbps=upload_mbps,
            burst_download_mbps=download_mbps * 1.2,  # Allow 20% burst
            burst_upload_mbps=upload_mbps * 1.2,
            priority=priority
        )
        
        self.user_limits[user_id] = limit
        
        # Apply the limit using traffic control
        self._apply_user_bandwidth_limit(user_id, limit)
        
        logger.info(f"Set bandwidth limit for user {user_id}: {download_mbps}↓/{upload_mbps}↑ Mbps")
        return True
    
    def _apply_user_bandwidth_limit(self, user_id: str, limit: BandwidthLimit) -> bool:
        """Apply bandwidth limits using Linux tc (traffic control)."""
        try:
            # Calculate class ID based on user ID hash
            class_id = abs(hash(user_id)) % 900 + 100  # Range: 100-999
            
            # Create download class
            cmd = [
                "tc", "class", "add", "dev", self.interface, "parent", "1:1",
                "classid", f"1:{class_id}", "htb",
                "rate", f"{limit.download_mbps}mbit",
                "ceil", f"{limit.burst_download_mbps or limit.download_mbps}mbit",
                "prio", str(100 - limit.priority)
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            
            # Add SFQ (Stochastic Fair Queueing) for this class
            cmd = [
                "tc", "qdisc", "add", "dev", self.interface, "parent", f"1:{class_id}",
                "handle", f"{class_id}:", "sfq", "perturb", "10"
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            
            logger.debug(f"Applied bandwidth limit for user {user_id} (class {class_id})")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to apply bandwidth limit for user {user_id}: {e}")
            return False
    
    def remove_user_bandwidth_limit(self, user_id: str) -> bool:
        """Remove bandwidth limits for a user."""
        if user_id in self.user_limits:
            del self.user_limits[user_id]
            
            # Remove traffic control class
            class_id = abs(hash(user_id)) % 900 + 100
            try:
                subprocess.run([
                    "tc", "class", "del", "dev", self.interface, "classid", f"1:{class_id}"
                ], capture_output=True, check=False)
            except:
                pass
            
            logger.info(f"Removed bandwidth limit for user {user_id}")
            return True
        return False
    
    def get_user_bandwidth_limit(self, user_id: str) -> Optional[BandwidthLimit]:
        """Get current bandwidth limits for a user."""
        return self.user_limits.get(user_id)
    
    def create_traffic_filter(self,
                             user_id: str,
                             src_ip: str = None,
                             dst_ip: str = None,
                             protocol: Protocol = Protocol.ALL,
                             port: int = None) -> bool:
        """Create a traffic filter to direct user traffic to appropriate class."""
        try:
            class_id = abs(hash(user_id)) % 900 + 100
            
            # Build filter command
            cmd = [
                "tc", "filter", "add", "dev", self.interface, "parent", "1:",
                "protocol", "ip", "prio", "10", "u32"
            ]
            
            # Add match conditions
            if src_ip:
                cmd.extend(["match", "ip", "src", src_ip])
            if dst_ip:
                cmd.extend(["match", "ip", "dst", dst_ip])
            if protocol != Protocol.ALL:
                if protocol == Protocol.TCP:
                    cmd.extend(["match", "ip", "protocol", "6", "0xff"])
                elif protocol == Protocol.UDP:
                    cmd.extend(["match", "ip", "protocol", "17", "0xff"])
                elif protocol == Protocol.ICMP:
                    cmd.extend(["match", "ip", "protocol", "1", "0xff"])
            
            if port and protocol in [Protocol.TCP, Protocol.UDP]:
                cmd.extend(["match", "ip", "dport", str(port), "0xffff"])
            
            # Specify target class
            cmd.extend(["flowid", f"1:{class_id}"])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.debug(f"Created traffic filter for user {user_id}")
                return True
            else:
                logger.error(f"Failed to create traffic filter: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating traffic filter: {e}")
            return False
    
    def start_monitoring(self):
        """Start bandwidth monitoring thread."""
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.monitoring_thread = Thread(target=self._monitor_bandwidth, daemon=True)
            self.monitoring_thread.start()
            logger.info("Bandwidth monitoring started")
    
    def stop_monitoring(self):
        """Stop bandwidth monitoring thread."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            # In a real implementation, you'd use a threading.Event to signal stop
            logger.info("Bandwidth monitoring stopped")
    
    def _monitor_bandwidth(self):
        """Monitor bandwidth usage for all users."""
        while True:
            try:
                self._collect_usage_stats()
                time.sleep(10)  # Collect stats every 10 seconds
            except Exception as e:
                logger.error(f"Error in bandwidth monitoring: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _collect_usage_stats(self):
        """Collect bandwidth usage statistics."""
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available - cannot collect detailed usage stats")
            return
            
        try:
            # Get network interface statistics
            net_io = psutil.net_io_counters(pernic=True)
            if self.interface not in net_io:
                return
            
            interface_stats = net_io[self.interface]
            
            with self.stats_lock:
                # This is a simplified version - in reality, you'd need to
                # parse detailed traffic control statistics and map to users
                for user_id in self.user_limits.keys():
                    if user_id not in self.usage_stats:
                        self.usage_stats[user_id] = UsageStats(
                            user_id=user_id,
                            mac_address="00:00:00:00:00:00",  # Would be populated from active sessions
                            bytes_downloaded=0,
                            bytes_uploaded=0,
                            packets_downloaded=0,
                            packets_uploaded=0,
                            session_start=time.strftime("%Y-%m-%d %H:%M:%S"),
                            last_seen=time.strftime("%Y-%m-%d %H:%M:%S"),
                            current_download_rate=0.0,
                            current_upload_rate=0.0
                        )
                    
                    # Update last seen
                    self.usage_stats[user_id].last_seen = time.strftime("%Y-%m-%d %H:%M:%S")
            
        except Exception as e:
            logger.error(f"Error collecting usage stats: {e}")
    
    def get_usage_stats(self, user_id: str = None) -> Dict:
        """Get usage statistics for a user or all users."""
        with self.stats_lock:
            if user_id:
                return self.usage_stats.get(user_id)
            return dict(self.usage_stats)
    
    def get_top_users_by_usage(self, limit: int = 10) -> List[Tuple[str, float]]:
        """Get top users by bandwidth usage."""
        with self.stats_lock:
            user_usage = []
            for user_id, stats in self.usage_stats.items():
                total_gb = (stats.bytes_downloaded + stats.bytes_uploaded) / (1024**3)
                user_usage.append((user_id, total_gb))
            
            return sorted(user_usage, key=lambda x: x[1], reverse=True)[:limit]
    
    def enforce_fair_usage_policy(self):
        """Implement fair usage policy by adjusting limits for heavy users."""
        top_users = self.get_top_users_by_usage(20)
        
        for user_id, usage_gb in top_users:
            current_limit = self.get_user_bandwidth_limit(user_id)
            if current_limit and usage_gb > 50:  # Heavy usage threshold
                # Reduce bandwidth by 20% for heavy users
                new_download = current_limit.download_mbps * 0.8
                new_upload = current_limit.upload_mbps * 0.8
                
                self.set_user_bandwidth_limit(user_id, new_download, new_upload, current_limit.priority - 10)
                logger.info(f"Applied fair usage policy to user {user_id}: reduced to {new_download:.1f}/{new_upload:.1f} Mbps")
    
    def generate_usage_report(self, start_date: str = None, end_date: str = None) -> Dict:
        """Generate bandwidth usage report."""
        with self.stats_lock:
            report = {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "period": {"start": start_date or "N/A", "end": end_date or "N/A"},
                "total_users": len(self.usage_stats),
                "total_download_gb": 0,
                "total_upload_gb": 0,
                "user_stats": []
            }
            
            for user_id, stats in self.usage_stats.items():
                download_gb = stats.bytes_downloaded / (1024**3)
                upload_gb = stats.bytes_uploaded / (1024**3)
                
                report["total_download_gb"] += download_gb
                report["total_upload_gb"] += upload_gb
                
                report["user_stats"].append({
                    "user_id": user_id,
                    "download_gb": round(download_gb, 2),
                    "upload_gb": round(upload_gb, 2),
                    "total_gb": round(download_gb + upload_gb, 2),
                    "current_download_rate_mbps": stats.current_download_rate,
                    "current_upload_rate_mbps": stats.current_upload_rate,
                    "session_duration_hours": self._calculate_session_duration(stats.session_start)
                })
            
            # Sort by total usage
            report["user_stats"].sort(key=lambda x: x["total_gb"], reverse=True)
            
            return report
    
    def _calculate_session_duration(self, session_start: str) -> float:
        """Calculate session duration in hours."""
        try:
            from datetime import datetime
            start_time = datetime.strptime(session_start, "%Y-%m-%d %H:%M:%S")
            duration = datetime.now() - start_time
            return duration.total_seconds() / 3600
        except:
            return 0.0
    
    def reset_traffic_control(self):
        """Reset all traffic control rules."""
        try:
            subprocess.run([
                "tc", "qdisc", "del", "dev", self.interface, "root"
            ], capture_output=True, check=False)
            
            self._initialize_traffic_control()
            logger.info("Traffic control rules reset")
            
        except Exception as e:
            logger.error(f"Failed to reset traffic control: {e}")
    
    def apply_emergency_throttle(self, download_limit: float = 1.0, upload_limit: float = 0.5):
        """Apply emergency bandwidth throttle to all users."""
        logger.warning(f"Applying emergency throttle: {download_limit}/{upload_limit} Mbps")
        
        for user_id in list(self.user_limits.keys()):
            self.set_user_bandwidth_limit(user_id, download_limit, upload_limit, priority=10)
    
    def remove_emergency_throttle(self):
        """Remove emergency throttle and restore normal limits."""
        logger.info("Removing emergency throttle")
        
        # This would restore from saved configuration
        self._load_default_rules()
    
    def get_interface_stats(self) -> Dict:
        """Get overall interface statistics."""
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available - returning empty interface stats")
            return {}
            
        try:
            net_io = psutil.net_io_counters(pernic=True)
            if self.interface in net_io:
                stats = net_io[self.interface]
                return {
                    "bytes_sent": stats.bytes_sent,
                    "bytes_recv": stats.bytes_recv,
                    "packets_sent": stats.packets_sent,
                    "packets_recv": stats.packets_recv,
                    "errin": stats.errin,
                    "errout": stats.errout,
                    "dropin": stats.dropin,
                    "dropout": stats.dropout
                }
        except Exception as e:
            logger.error(f"Error getting interface stats: {e}")
        
        return {}
    
    def export_configuration(self) -> Dict:
        """Export current bandwidth management configuration."""
        return {
            "interface": self.interface,
            "user_limits": {
                user_id: {
                    "download_mbps": limit.download_mbps,
                    "upload_mbps": limit.upload_mbps,
                    "priority": limit.priority
                } for user_id, limit in self.user_limits.items()
            },
            "qos_rules": {
                rule_id: {
                    "name": rule.name,
                    "protocol": rule.protocol.value,
                    "traffic_class": rule.traffic_class.value,
                    "enabled": rule.enabled
                } for rule_id, rule in self.qos_rules.items()
            }
        }