"""
Policy enforcement module for bandwidth management and access control.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re

logger = logging.getLogger(__name__)


class PolicyAction(Enum):
    """Policy enforcement actions."""
    ALLOW = "allow"
    DENY = "deny"
    LIMIT = "limit"
    REDIRECT = "redirect"
    LOG = "log"


class PolicyType(Enum):
    """Types of policies."""
    BANDWIDTH = "bandwidth"
    TIME_BASED = "time_based"
    CONTENT = "content"
    USER_GROUP = "user_group"
    DEVICE = "device"


@dataclass
class BandwidthLimit:
    """Bandwidth limitation configuration."""
    download_mbps: float
    upload_mbps: float
    total_mb: Optional[float] = None
    burst_mbps: Optional[float] = None
    priority: int = 5  # 1-10, higher = higher priority


@dataclass
class TimeWindow:
    """Time-based access window."""
    start_time: str  # HH:MM format
    end_time: str    # HH:MM format
    days: List[str]  # Mon, Tue, Wed, Thu, Fri, Sat, Sun
    timezone: str = "UTC"


@dataclass
class UserGroup:
    """User group definition."""
    name: str
    description: str
    members: List[str]  # User IDs or patterns
    bandwidth_limit: BandwidthLimit
    time_windows: List[TimeWindow]
    allowed_content: List[str]
    blocked_content: List[str]


@dataclass
class Policy:
    """Network policy definition."""
    id: str
    name: str
    description: str
    policy_type: PolicyType
    enabled: bool
    priority: int
    conditions: Dict[str, Any]
    actions: List[PolicyAction]
    parameters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class PolicyEngine:
    """Core policy enforcement engine."""
    
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        self.user_groups: Dict[str, UserGroup] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.policy_cache = {}
        
    def add_policy(self, policy: Policy) -> bool:
        """Add a new policy."""
        try:
            self.policies[policy.id] = policy
            self._invalidate_cache()
            logger.info(f"Policy {policy.id} added successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to add policy {policy.id}: {e}")
            return False
    
    def remove_policy(self, policy_id: str) -> bool:
        """Remove a policy."""
        if policy_id in self.policies:
            del self.policies[policy_id]
            self._invalidate_cache()
            logger.info(f"Policy {policy_id} removed")
            return True
        return False
    
    def add_user_group(self, group: UserGroup) -> bool:
        """Add a user group."""
        try:
            self.user_groups[group.name] = group
            logger.info(f"User group {group.name} added successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to add user group {group.name}: {e}")
            return False
    
    def evaluate_policies(self, user_id: str, device_mac: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate all policies for a user request."""
        result = {
            'allowed': True,
            'bandwidth_limit': None,
            'actions': [],
            'reasons': [],
            'applied_policies': []
        }
        
        # Get applicable policies sorted by priority
        applicable_policies = self._get_applicable_policies(user_id, device_mac, request_data)
        
        for policy in applicable_policies:
            if not policy.enabled:
                continue
                
            if self._matches_conditions(policy, user_id, device_mac, request_data):
                policy_result = self._apply_policy(policy, user_id, device_mac, request_data)
                
                # Merge results
                if not policy_result['allowed']:
                    result['allowed'] = False
                    result['reasons'].extend(policy_result['reasons'])
                
                result['actions'].extend(policy_result['actions'])
                result['applied_policies'].append(policy.id)
                
                # Apply bandwidth limit (most restrictive wins)
                if policy_result.get('bandwidth_limit'):
                    if not result['bandwidth_limit'] or self._is_more_restrictive(
                        policy_result['bandwidth_limit'], result['bandwidth_limit']
                    ):
                        result['bandwidth_limit'] = policy_result['bandwidth_limit']
        
        return result
    
    def _get_applicable_policies(self, user_id: str, device_mac: str, request_data: Dict[str, Any]) -> List[Policy]:
        """Get policies applicable to the request."""
        applicable = []
        
        for policy in self.policies.values():
            if self._is_policy_applicable(policy, user_id, device_mac, request_data):
                applicable.append(policy)
        
        # Sort by priority (higher priority first)
        return sorted(applicable, key=lambda p: p.priority, reverse=True)
    
    def _is_policy_applicable(self, policy: Policy, user_id: str, device_mac: str, request_data: Dict[str, Any]) -> bool:
        """Check if policy is applicable to the request."""
        # Basic applicability checks
        if not policy.enabled:
            return False
        
        # Check user group membership
        user_group = self._get_user_group(user_id)
        if policy.policy_type == PolicyType.USER_GROUP and user_group:
            return policy.conditions.get('group_name') == user_group.name
        
        # Check time-based conditions
        if policy.policy_type == PolicyType.TIME_BASED:
            return self._is_time_window_active(policy.conditions.get('time_windows', []))
        
        # Check device-based conditions
        if policy.policy_type == PolicyType.DEVICE:
            device_patterns = policy.conditions.get('device_patterns', [])
            return any(re.match(pattern, device_mac) for pattern in device_patterns)
        
        return True
    
    def _matches_conditions(self, policy: Policy, user_id: str, device_mac: str, request_data: Dict[str, Any]) -> bool:
        """Check if request matches policy conditions."""
        conditions = policy.conditions
        
        # Check source IP
        if 'source_ip' in conditions:
            if request_data.get('source_ip') != conditions['source_ip']:
                return False
        
        # Check destination patterns
        if 'destination_patterns' in conditions:
            destination = request_data.get('destination', '')
            patterns = conditions['destination_patterns']
            if not any(re.match(pattern, destination) for pattern in patterns):
                return False
        
        # Check protocol
        if 'protocol' in conditions:
            if request_data.get('protocol') != conditions['protocol']:
                return False
        
        # Check port ranges
        if 'port_ranges' in conditions:
            port = request_data.get('port')
            if port:
                port_ranges = conditions['port_ranges']
                if not any(start <= port <= end for start, end in port_ranges):
                    return False
        
        return True
    
    def _apply_policy(self, policy: Policy, user_id: str, device_mac: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply policy and return result."""
        result = {
            'allowed': True,
            'actions': [],
            'reasons': [],
            'bandwidth_limit': None
        }
        
        # Apply actions
        for action in policy.actions:
            if action == PolicyAction.DENY:
                result['allowed'] = False
                result['reasons'].append(f"Denied by policy {policy.name}")
            
            elif action == PolicyAction.LIMIT:
                bandwidth_params = policy.parameters.get('bandwidth_limit')
                if bandwidth_params:
                    result['bandwidth_limit'] = BandwidthLimit(**bandwidth_params)
            
            elif action == PolicyAction.REDIRECT:
                redirect_url = policy.parameters.get('redirect_url')
                if redirect_url:
                    result['actions'].append(('redirect', redirect_url))
            
            elif action == PolicyAction.LOG:
                result['actions'].append(('log', f"Policy {policy.name} applied"))
        
        return result
    
    def _get_user_group(self, user_id: str) -> Optional[UserGroup]:
        """Get user group for a user."""
        for group in self.user_groups.values():
            if user_id in group.members:
                return group
            # Check pattern matching
            for pattern in group.members:
                if '*' in pattern or '?' in pattern:
                    if re.match(pattern.replace('*', '.*').replace('?', '.'), user_id):
                        return group
        return None
    
    def _is_time_window_active(self, time_windows: List[Dict[str, Any]]) -> bool:
        """Check if current time is within any time window."""
        now = datetime.now()
        current_day = now.strftime('%a')
        current_time = now.strftime('%H:%M')
        
        for window in time_windows:
            if current_day in window.get('days', []):
                start_time = window.get('start_time', '00:00')
                end_time = window.get('end_time', '23:59')
                
                if start_time <= current_time <= end_time:
                    return True
        
        return False
    
    def _is_more_restrictive(self, limit1: BandwidthLimit, limit2: BandwidthLimit) -> bool:
        """Check if limit1 is more restrictive than limit2."""
        return (limit1.download_mbps < limit2.download_mbps or 
                limit1.upload_mbps < limit2.upload_mbps)
    
    def _invalidate_cache(self):
        """Invalidate policy cache."""
        self.policy_cache.clear()
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get summary of all policies."""
        return {
            'total_policies': len(self.policies),
            'enabled_policies': len([p for p in self.policies.values() if p.enabled]),
            'user_groups': len(self.user_groups),
            'policy_types': {
                pt.value: len([p for p in self.policies.values() if p.policy_type == pt])
                for pt in PolicyType
            }
        }


class DefaultPolicyTemplates:
    """Default policy templates for common scenarios."""
    
    @staticmethod
    def create_student_bandwidth_policy() -> Policy:
        """Create default student bandwidth policy."""
        return Policy(
            id="student_bandwidth",
            name="Student Bandwidth Limit",
            description="Default bandwidth limits for students",
            policy_type=PolicyType.BANDWIDTH,
            enabled=True,
            priority=5,
            conditions={"group_name": "students"},
            actions=[PolicyAction.LIMIT],
            parameters={
                "bandwidth_limit": {
                    "download_mbps": 10.0,
                    "upload_mbps": 5.0,
                    "priority": 3
                }
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @staticmethod
    def create_staff_bandwidth_policy() -> Policy:
        """Create default staff bandwidth policy."""
        return Policy(
            id="staff_bandwidth",
            name="Staff Bandwidth Limit",
            description="Default bandwidth limits for staff",
            policy_type=PolicyType.BANDWIDTH,
            enabled=True,
            priority=7,
            conditions={"group_name": "staff"},
            actions=[PolicyAction.LIMIT],
            parameters={
                "bandwidth_limit": {
                    "download_mbps": 50.0,
                    "upload_mbps": 20.0,
                    "priority": 7
                }
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @staticmethod
    def create_night_time_policy() -> Policy:
        """Create night time restriction policy."""
        return Policy(
            id="night_restriction",
            name="Night Time Restrictions",
            description="Reduced bandwidth during night hours",
            policy_type=PolicyType.TIME_BASED,
            enabled=True,
            priority=6,
            conditions={
                "time_windows": [{
                    "start_time": "23:00",
                    "end_time": "06:00",
                    "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                }]
            },
            actions=[PolicyAction.LIMIT],
            parameters={
                "bandwidth_limit": {
                    "download_mbps": 5.0,
                    "upload_mbps": 2.0,
                    "priority": 2
                }
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @staticmethod
    def create_default_user_groups() -> List[UserGroup]:
        """Create default user groups."""
        return [
            UserGroup(
                name="students",
                description="Student users",
                members=["student_*", "*@student.ncuk.ac.uk"],
                bandwidth_limit=BandwidthLimit(download_mbps=10.0, upload_mbps=5.0, priority=3),
                time_windows=[TimeWindow(start_time="06:00", end_time="23:00", days=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])],
                allowed_content=["educational", "general"],
                blocked_content=["adult", "gambling", "malware"]
            ),
            UserGroup(
                name="staff",
                description="Staff and faculty",
                members=["staff_*", "*@staff.ncuk.ac.uk", "*@ncuk.ac.uk"],
                bandwidth_limit=BandwidthLimit(download_mbps=50.0, upload_mbps=20.0, priority=7),
                time_windows=[TimeWindow(start_time="00:00", end_time="23:59", days=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])],
                allowed_content=["*"],
                blocked_content=["malware"]
            ),
            UserGroup(
                name="guests",
                description="Guest users",
                members=["guest_*"],
                bandwidth_limit=BandwidthLimit(download_mbps=2.0, upload_mbps=1.0, priority=1),
                time_windows=[TimeWindow(start_time="08:00", end_time="18:00", days=["Mon", "Tue", "Wed", "Thu", "Fri"])],
                allowed_content=["general"],
                blocked_content=["adult", "gambling", "malware", "social_media"]
            )
        ]