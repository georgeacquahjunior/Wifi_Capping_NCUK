"""
WiFi Bandwidth Capping System
Monitors and enforces bandwidth limits for WiFi users
"""

import time
import threading
import logging
import psutil
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

from ..radius import RadiusClient
from ..utils.config import Config
from ..utils.security import generate_session_id


logger = logging.getLogger(__name__)


class UserSession:
    """Represents an active user session with bandwidth tracking"""
    
    def __init__(self, username: str, user_ip: str, nas_ip: str, 
                 nas_port: int, bandwidth_limit_mb: int):
        self.username = username
        self.user_ip = user_ip
        self.nas_ip = nas_ip
        self.nas_port = nas_port
        self.bandwidth_limit_mb = bandwidth_limit_mb
        self.session_id = generate_session_id()
        
        # Session tracking
        self.start_time = datetime.now()
        self.last_update = self.start_time
        self.total_bytes_in = 0
        self.total_bytes_out = 0
        self.is_active = True
        self.is_capped = False
        
        # Rate limiting
        self.last_bytes_in = 0
        self.last_bytes_out = 0
        
        logger.info(f"New session created for user {username}: {self.session_id}")

    @property
    def session_duration(self) -> int:
        """Get session duration in seconds"""
        return int((datetime.now() - self.start_time).total_seconds())

    @property
    def total_bytes(self) -> int:
        """Get total bytes transferred"""
        return self.total_bytes_in + self.total_bytes_out

    @property
    def total_mb(self) -> float:
        """Get total MB transferred"""
        return self.total_bytes / (1024 * 1024)

    def update_usage(self, bytes_in: int, bytes_out: int):
        """Update usage statistics"""
        self.total_bytes_in += bytes_in
        self.total_bytes_out += bytes_out
        self.last_update = datetime.now()
        
        # Check if user has exceeded bandwidth limit
        if self.total_mb >= self.bandwidth_limit_mb:
            if not self.is_capped:
                logger.warning(f"User {self.username} exceeded bandwidth limit: "
                             f"{self.total_mb:.2f}MB / {self.bandwidth_limit_mb}MB")
                self.is_capped = True

    def get_remaining_bandwidth_mb(self) -> float:
        """Get remaining bandwidth in MB"""
        remaining = self.bandwidth_limit_mb - self.total_mb
        return max(0, remaining)


class BandwidthMonitor:
    """Monitors network usage and enforces bandwidth caps"""
    
    def __init__(self, config: Config, radius_client: RadiusClient):
        self.config = config
        self.radius_client = radius_client
        self.active_sessions: Dict[str, UserSession] = {}
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        logger.info("Bandwidth monitor initialized")

    def start_monitoring(self):
        """Start the bandwidth monitoring thread"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            logger.warning("Monitoring already started")
            return
            
        self.stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("Bandwidth monitoring started")

    def stop_monitoring_service(self):
        """Stop the bandwidth monitoring thread"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.stop_monitoring.set()
            self.monitoring_thread.join(timeout=10)
            
        logger.info("Bandwidth monitoring stopped")

    def create_session(self, username: str, user_ip: str, nas_ip: str, 
                      nas_port: int, bandwidth_limit_mb: Optional[int] = None) -> str:
        """
        Create a new user session
        
        Args:
            username: User's username
            user_ip: User's IP address
            nas_ip: Network Access Server IP
            nas_port: Network Access Server port
            bandwidth_limit_mb: Bandwidth limit in MB (uses default if None)
            
        Returns:
            str: Session ID
        """
        if bandwidth_limit_mb is None:
            bandwidth_limit_mb = self.config.default_bandwidth_limit_mb
            
        session = UserSession(username, user_ip, nas_ip, nas_port, bandwidth_limit_mb)
        self.active_sessions[session.session_id] = session
        
        # Send accounting start to RADIUS server
        success = self.radius_client.send_accounting_start(
            username, session.session_id, nas_ip, nas_port, user_ip
        )
        
        if not success:
            logger.error(f"Failed to send accounting start for session {session.session_id}")
            
        return session.session_id

    def end_session(self, session_id: str, terminate_cause: str = "User-Request") -> bool:
        """
        End a user session
        
        Args:
            session_id: Session ID to end
            terminate_cause: Reason for termination
            
        Returns:
            bool: True if session was successfully ended
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Attempted to end non-existent session: {session_id}")
            return False
            
        session = self.active_sessions[session_id]
        session.is_active = False
        
        # Send accounting stop to RADIUS server
        success = self.radius_client.send_accounting_stop(
            session.username,
            session_id,
            session.session_duration,
            session.total_bytes_in,
            session.total_bytes_out,
            session.nas_ip,
            session.nas_port,
            terminate_cause
        )
        
        if success:
            logger.info(f"Session {session_id} ended successfully for user {session.username}")
        else:
            logger.error(f"Failed to send accounting stop for session {session_id}")
            
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        return success

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get information about a session
        
        Args:
            session_id: Session ID
            
        Returns:
            dict: Session information or None if not found
        """
        if session_id not in self.active_sessions:
            return None
            
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "username": session.username,
            "user_ip": session.user_ip,
            "start_time": session.start_time.isoformat(),
            "duration_seconds": session.session_duration,
            "total_bytes_in": session.total_bytes_in,
            "total_bytes_out": session.total_bytes_out,
            "total_mb": session.total_mb,
            "bandwidth_limit_mb": session.bandwidth_limit_mb,
            "remaining_mb": session.get_remaining_bandwidth_mb(),
            "is_capped": session.is_capped,
            "is_active": session.is_active
        }

    def get_all_sessions(self) -> Dict[str, Dict]:
        """Get information about all active sessions"""
        return {sid: self.get_session_info(sid) for sid in self.active_sessions}

    def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting bandwidth monitoring loop")
        
        while not self.stop_monitoring.is_set():
            try:
                self._update_all_sessions()
                self._check_session_limits()
                self._send_accounting_updates()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                
            # Wait for next monitoring cycle
            self.stop_monitoring.wait(self.config.monitoring_interval_seconds)

    def _update_all_sessions(self):
        """Update usage statistics for all active sessions"""
        for session_id, session in list(self.active_sessions.items()):
            if not session.is_active:
                continue
                
            try:
                # Get current network stats (simplified - in production would use more sophisticated monitoring)
                bytes_in, bytes_out = self._get_user_network_stats(session.user_ip)
                
                # Calculate delta since last update
                delta_in = max(0, bytes_in - session.last_bytes_in)
                delta_out = max(0, bytes_out - session.last_bytes_out)
                
                # Update session with delta
                if delta_in > 0 or delta_out > 0:
                    session.update_usage(delta_in, delta_out)
                    logger.debug(f"Session {session_id} updated: "
                               f"+{delta_in}B in, +{delta_out}B out")
                
                # Store current values for next delta calculation
                session.last_bytes_in = bytes_in
                session.last_bytes_out = bytes_out
                
            except Exception as e:
                logger.error(f"Error updating session {session_id}: {str(e)}")

    def _get_user_network_stats(self, user_ip: str) -> Tuple[int, int]:
        """
        Get network statistics for a specific user IP
        Note: This is a simplified implementation
        In production, you would use netfilter, iptables, or SNMP
        """
        # This is a placeholder implementation
        # In a real system, you would query network interfaces or firewall rules
        # to get actual per-IP statistics
        
        # For demonstration, we'll use system-wide stats divided by active sessions
        net_stats = psutil.net_io_counters()
        active_count = len([s for s in self.active_sessions.values() if s.is_active])
        
        if active_count == 0:
            return 0, 0
            
        # Simplified approximation - in production use proper per-IP monitoring
        bytes_in = net_stats.bytes_recv // active_count
        bytes_out = net_stats.bytes_sent // active_count
        
        return bytes_in, bytes_out

    def _check_session_limits(self):
        """Check if any sessions have exceeded their limits"""
        current_time = datetime.now()
        max_session_duration = timedelta(hours=self.config.max_session_time_hours)
        
        for session_id, session in list(self.active_sessions.items()):
            if not session.is_active:
                continue
                
            # Check session time limit
            if current_time - session.start_time > max_session_duration:
                logger.warning(f"Session {session_id} exceeded time limit, terminating")
                self.end_session(session_id, "Session-Timeout")
                continue
                
            # Check bandwidth limit
            if session.is_capped:
                logger.info(f"Session {session_id} is bandwidth capped")
                # In production, you would implement actual traffic shaping here
                # For now, we just log the event

    def _send_accounting_updates(self):
        """Send accounting updates for active sessions"""
        for session in self.active_sessions.values():
            if not session.is_active:
                continue
                
            # Send update every monitoring interval
            success = self.radius_client.send_accounting_update(
                session.username,
                session.session_id,
                session.session_duration,
                session.total_bytes_in,
                session.total_bytes_out,
                session.nas_ip,
                session.nas_port
            )
            
            if not success:
                logger.warning(f"Failed to send accounting update for session {session.session_id}")


class WifiCappingService:
    """Main WiFi capping service that coordinates all components"""
    
    def __init__(self, config: Config):
        self.config = config
        self.radius_client = RadiusClient(config)
        self.bandwidth_monitor = BandwidthMonitor(config, self.radius_client)
        
        logger.info("WiFi capping service initialized")

    def start(self):
        """Start the WiFi capping service"""
        logger.info("Starting WiFi capping service")
        
        # Test RADIUS connection
        if not self.radius_client.test_connection():
            logger.error("Failed to connect to RADIUS server")
            raise ConnectionError("RADIUS server not accessible")
            
        # Start bandwidth monitoring
        self.bandwidth_monitor.start_monitoring()
        
        logger.info("WiFi capping service started successfully")

    def stop(self):
        """Stop the WiFi capping service"""
        logger.info("Stopping WiFi capping service")
        
        # End all active sessions
        session_ids = list(self.bandwidth_monitor.active_sessions.keys())
        for session_id in session_ids:
            self.bandwidth_monitor.end_session(session_id, "Admin-Reset")
            
        # Stop monitoring
        self.bandwidth_monitor.stop_monitoring_service()
        
        logger.info("WiFi capping service stopped")

    def authenticate_and_start_session(self, username: str, password: str,
                                     user_ip: str, nas_ip: str, nas_port: int,
                                     bandwidth_limit_mb: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Authenticate user and start a session if successful
        
        Returns:
            Tuple of (success, session_id)
        """
        # Authenticate with RADIUS server
        auth_success, attributes = self.radius_client.authenticate_user(
            username, password, nas_ip, nas_port
        )
        
        if not auth_success:
            logger.warning(f"Authentication failed for user {username}")
            return False, None
            
        # Create session for authenticated user
        session_id = self.bandwidth_monitor.create_session(
            username, user_ip, nas_ip, nas_port, bandwidth_limit_mb
        )
        
        logger.info(f"User {username} authenticated and session {session_id} started")
        return True, session_id

    def get_service_status(self) -> Dict:
        """Get overall service status"""
        return {
            "service_running": True,
            "radius_connected": self.radius_client.test_connection(),
            "active_sessions": len(self.bandwidth_monitor.active_sessions),
            "monitoring_interval": self.config.monitoring_interval_seconds,
            "default_bandwidth_limit_mb": self.config.default_bandwidth_limit_mb
        }