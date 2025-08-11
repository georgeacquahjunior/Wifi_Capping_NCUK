"""
Access Control Module for NCUK WiFi Capping System

This module handles access policies, user management, and network permissions:
- User authentication and authorization
- MAC address filtering
- Time-based access control
- Bandwidth allocation per user/group
- Guest access management
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib
import secrets
from netaddr import EUI

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User roles with different access privileges."""
    GUEST = "guest"
    STUDENT = "student"
    STAFF = "staff"
    FACULTY = "faculty"
    ADMIN = "admin"


class AccessLevel(Enum):
    """Access levels for different user categories."""
    RESTRICTED = "restricted"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    UNLIMITED = "unlimited"


@dataclass
class User:
    """User data structure."""
    user_id: str
    username: str
    email: str
    role: UserRole
    access_level: AccessLevel
    mac_addresses: List[str]
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True
    password_hash: Optional[str] = None
    bandwidth_limit_mbps: Optional[int] = None
    daily_quota_gb: Optional[float] = None
    expires_at: Optional[str] = None


@dataclass
class AccessRule:
    """Access control rule definition."""
    rule_id: str
    name: str
    rule_type: str  # 'time', 'mac', 'user', 'group', 'bandwidth'
    conditions: Dict
    actions: Dict
    priority: int
    enabled: bool
    created_at: str


class TimeWindow:
    """Represents a time-based access window."""
    
    def __init__(self, start_time: str, end_time: str, days: List[str]):
        self.start_time = start_time  # Format: "HH:MM"
        self.end_time = end_time      # Format: "HH:MM"
        self.days = days              # List of day names: ["monday", "tuesday", ...]
    
    def is_active_now(self) -> bool:
        """Check if the current time falls within this window."""
        now = datetime.now()
        current_day = now.strftime("%A").lower()
        current_time = now.strftime("%H:%M")
        
        if current_day not in [day.lower() for day in self.days]:
            return False
        
        return self._time_in_range(current_time, self.start_time, self.end_time)
    
    def _time_in_range(self, current: str, start: str, end: str) -> bool:
        """Check if current time is between start and end time."""
        if start <= end:
            return start <= current <= end
        else:  # Crosses midnight
            return current >= start or current <= end


class AccessControl:
    """Manages access control policies and user permissions."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.access_rules: Dict[str, AccessRule] = {}
        self.mac_whitelist: Set[str] = set()
        self.mac_blacklist: Set[str] = set()
        self.active_sessions: Dict[str, Dict] = {}
        self.bandwidth_allocations = {}
        self._load_default_policies()
    
    def _load_default_policies(self):
        """Load default access policies."""
        # Default bandwidth limits by access level
        self.bandwidth_allocations = {
            AccessLevel.RESTRICTED: {"download": 1, "upload": 0.5},  # Mbps
            AccessLevel.BASIC: {"download": 5, "upload": 2},
            AccessLevel.STANDARD: {"download": 25, "upload": 10},
            AccessLevel.PREMIUM: {"download": 100, "upload": 50},
            AccessLevel.UNLIMITED: {"download": -1, "upload": -1}  # No limit
        }
        
        # Create default time-based access rule for students
        self.create_time_based_rule(
            rule_id="student_hours",
            name="Student Access Hours",
            start_time="06:00",
            end_time="23:00",
            days=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            target_roles=[UserRole.STUDENT],
            priority=100
        )
        
        # Create default guest access rule (limited hours)
        self.create_time_based_rule(
            rule_id="guest_hours",
            name="Guest Access Hours",
            start_time="08:00",
            end_time="20:00",
            days=["monday", "tuesday", "wednesday", "thursday", "friday"],
            target_roles=[UserRole.GUEST],
            priority=200
        )
        
        logger.info("Default access policies loaded")
    
    def create_user(self, 
                   username: str,
                   email: str,
                   role: UserRole,
                   access_level: AccessLevel = None,
                   mac_addresses: List[str] = None,
                   password: str = None,
                   **kwargs) -> User:
        """Create a new user account."""
        user_id = self._generate_user_id(username)
        
        # Set default access level based on role
        if access_level is None:
            access_level_map = {
                UserRole.GUEST: AccessLevel.RESTRICTED,
                UserRole.STUDENT: AccessLevel.BASIC,
                UserRole.STAFF: AccessLevel.STANDARD,
                UserRole.FACULTY: AccessLevel.PREMIUM,
                UserRole.ADMIN: AccessLevel.UNLIMITED
            }
            access_level = access_level_map.get(role, AccessLevel.BASIC)
        
        # Validate and normalize MAC addresses
        validated_macs = []
        if mac_addresses:
            for mac in mac_addresses:
                try:
                    normalized_mac = str(EUI(mac)).replace('-', ':').upper()
                    validated_macs.append(normalized_mac)
                except Exception as e:
                    logger.warning(f"Invalid MAC address {mac}: {e}")
        
        # Hash password if provided
        password_hash = None
        if password:
            password_hash = self._hash_password(password)
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            access_level=access_level,
            mac_addresses=validated_macs,
            created_at=datetime.now().isoformat(),
            password_hash=password_hash,
            bandwidth_limit_mbps=kwargs.get('bandwidth_limit_mbps'),
            daily_quota_gb=kwargs.get('daily_quota_gb'),
            expires_at=kwargs.get('expires_at')
        )
        
        self.users[user_id] = user
        logger.info(f"Created user: {username} ({role.value}) with access level: {access_level.value}")
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        for user in self.users.values():
            if user.username == username and user.is_active:
                if user.password_hash and self._verify_password(password, user.password_hash):
                    user.last_login = datetime.now().isoformat()
                    logger.info(f"User authenticated: {username}")
                    return user
        
        logger.warning(f"Authentication failed for user: {username}")
        return None
    
    def authorize_mac_address(self, mac_address: str, user_id: str = None) -> bool:
        """Check if a MAC address is authorized for network access."""
        try:
            normalized_mac = str(EUI(mac_address)).replace('-', ':').upper()
        except:
            logger.error(f"Invalid MAC address format: {mac_address}")
            return False
        
        # Check blacklist first
        if normalized_mac in self.mac_blacklist:
            logger.warning(f"MAC address {normalized_mac} is blacklisted")
            return False
        
        # If whitelist is active and MAC is not in it
        if self.mac_whitelist and normalized_mac not in self.mac_whitelist:
            logger.warning(f"MAC address {normalized_mac} not in whitelist")
            return False
        
        # Check if MAC is associated with an active user
        if user_id:
            user = self.users.get(user_id)
            if user and user.is_active:
                if normalized_mac in user.mac_addresses:
                    return self._check_user_access_permissions(user)
        
        # Check all users for this MAC address
        for user in self.users.values():
            if user.is_active and normalized_mac in user.mac_addresses:
                return self._check_user_access_permissions(user)
        
        logger.warning(f"MAC address {normalized_mac} not associated with any active user")
        return False
    
    def _check_user_access_permissions(self, user: User) -> bool:
        """Check if user has current access permissions."""
        # Check if account has expired
        if user.expires_at:
            expiry = datetime.fromisoformat(user.expires_at)
            if datetime.now() > expiry:
                logger.warning(f"User account expired: {user.username}")
                return False
        
        # Check time-based access rules
        if not self._check_time_based_access(user):
            logger.warning(f"Time-based access denied for user: {user.username}")
            return False
        
        # Check quota limits
        if user.daily_quota_gb:
            usage = self.get_daily_usage(user.user_id)
            if usage >= user.daily_quota_gb:
                logger.warning(f"Daily quota exceeded for user: {user.username}")
                return False
        
        return True
    
    def _check_time_based_access(self, user: User) -> bool:
        """Check if user has access based on current time and applicable rules."""
        applicable_rules = []
        
        for rule in self.access_rules.values():
            if not rule.enabled:
                continue
            
            if rule.rule_type == "time":
                conditions = rule.conditions
                target_roles = conditions.get("target_roles", [])
                
                # Check if rule applies to this user's role
                if user.role.value in target_roles:
                    applicable_rules.append(rule)
        
        if not applicable_rules:
            return True  # No time restrictions apply
        
        # Check each applicable rule
        for rule in sorted(applicable_rules, key=lambda x: x.priority):
            time_window = TimeWindow(
                rule.conditions["start_time"],
                rule.conditions["end_time"],
                rule.conditions["days"]
            )
            
            action = rule.actions.get("action", "allow")
            if time_window.is_active_now():
                return action == "allow"
        
        return False  # Default deny if no rule matches current time
    
    def create_time_based_rule(self,
                              rule_id: str,
                              name: str,
                              start_time: str,
                              end_time: str,
                              days: List[str],
                              target_roles: List[UserRole],
                              priority: int = 100,
                              action: str = "allow") -> AccessRule:
        """Create a time-based access rule."""
        rule = AccessRule(
            rule_id=rule_id,
            name=name,
            rule_type="time",
            conditions={
                "start_time": start_time,
                "end_time": end_time,
                "days": days,
                "target_roles": [role.value for role in target_roles]
            },
            actions={"action": action},
            priority=priority,
            enabled=True,
            created_at=datetime.now().isoformat()
        )
        
        self.access_rules[rule_id] = rule
        logger.info(f"Created time-based access rule: {name}")
        return rule
    
    def add_mac_to_whitelist(self, mac_address: str) -> bool:
        """Add MAC address to whitelist."""
        try:
            normalized_mac = str(EUI(mac_address)).replace('-', ':').upper()
            self.mac_whitelist.add(normalized_mac)
            logger.info(f"Added MAC to whitelist: {normalized_mac}")
            return True
        except Exception as e:
            logger.error(f"Failed to add MAC to whitelist: {e}")
            return False
    
    def add_mac_to_blacklist(self, mac_address: str) -> bool:
        """Add MAC address to blacklist."""
        try:
            normalized_mac = str(EUI(mac_address)).replace('-', ':').upper()
            self.mac_blacklist.add(normalized_mac)
            # Remove from whitelist if present
            self.mac_whitelist.discard(normalized_mac)
            logger.info(f"Added MAC to blacklist: {normalized_mac}")
            return True
        except Exception as e:
            logger.error(f"Failed to add MAC to blacklist: {e}")
            return False
    
    def remove_mac_from_whitelist(self, mac_address: str) -> bool:
        """Remove MAC address from whitelist."""
        try:
            normalized_mac = str(EUI(mac_address)).replace('-', ':').upper()
            self.mac_whitelist.discard(normalized_mac)
            logger.info(f"Removed MAC from whitelist: {normalized_mac}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove MAC from whitelist: {e}")
            return False
    
    def remove_mac_from_blacklist(self, mac_address: str) -> bool:
        """Remove MAC address from blacklist."""
        try:
            normalized_mac = str(EUI(mac_address)).replace('-', ':').upper()
            self.mac_blacklist.discard(normalized_mac)
            logger.info(f"Removed MAC from blacklist: {normalized_mac}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove MAC from blacklist: {e}")
            return False
    
    def get_bandwidth_limit(self, user_id: str) -> Tuple[int, int]:
        """Get bandwidth limits for a user (download, upload in Mbps)."""
        user = self.users.get(user_id)
        if not user:
            return (1, 0.5)  # Default restrictive limits
        
        # Use user-specific limit if set
        if user.bandwidth_limit_mbps:
            return (user.bandwidth_limit_mbps, user.bandwidth_limit_mbps // 2)
        
        # Use access level defaults
        limits = self.bandwidth_allocations.get(user.access_level)
        if limits:
            return (limits["download"], limits["upload"])
        
        return (5, 2)  # Default fallback
    
    def create_guest_access(self, duration_hours: int = 24, bandwidth_limit: int = 5) -> Dict:
        """Create temporary guest access credentials."""
        guest_id = f"guest_{int(time.time())}_{secrets.token_hex(4)}"
        temp_password = secrets.token_urlsafe(12)
        
        expires_at = (datetime.now() + timedelta(hours=duration_hours)).isoformat()
        
        guest_user = self.create_user(
            username=guest_id,
            email=f"{guest_id}@guest.ncuk.edu",
            role=UserRole.GUEST,
            access_level=AccessLevel.RESTRICTED,
            password=temp_password,
            bandwidth_limit_mbps=bandwidth_limit,
            expires_at=expires_at
        )
        
        return {
            "username": guest_id,
            "password": temp_password,
            "expires_at": expires_at,
            "bandwidth_limit_mbps": bandwidth_limit,
            "instructions": "Connect to NCUK-Guest network and use these credentials"
        }
    
    def get_user_by_mac(self, mac_address: str) -> Optional[User]:
        """Find user by MAC address."""
        try:
            normalized_mac = str(EUI(mac_address)).replace('-', ':').upper()
            for user in self.users.values():
                if normalized_mac in user.mac_addresses:
                    return user
        except:
            pass
        return None
    
    def get_daily_usage(self, user_id: str) -> float:
        """Get daily data usage for a user in GB."""
        # This would integrate with actual usage tracking
        # For now, return a placeholder value
        return 0.0
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account."""
        if user_id in self.users:
            self.users[user_id].is_active = False
            logger.info(f"Deactivated user: {user_id}")
            return True
        return False
    
    def reactivate_user(self, user_id: str) -> bool:
        """Reactivate a user account."""
        if user_id in self.users:
            self.users[user_id].is_active = True
            logger.info(f"Reactivated user: {user_id}")
            return True
        return False
    
    def export_user_list(self) -> List[Dict]:
        """Export user list for external systems."""
        return [asdict(user) for user in self.users.values()]
    
    def export_access_rules(self) -> List[Dict]:
        """Export access rules configuration."""
        return [asdict(rule) for rule in self.access_rules.values()]
    
    def _generate_user_id(self, username: str) -> str:
        """Generate a unique user ID."""
        timestamp = str(int(time.time()))
        hash_input = f"{username}_{timestamp}".encode()
        return hashlib.md5(hash_input).hexdigest()[:12]
    
    def _hash_password(self, password: str) -> str:
        """Hash a password for secure storage."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify a password against stored hash."""
        try:
            salt, hash_hex = stored_hash.split(':')
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash.hex() == hash_hex
        except:
            return False