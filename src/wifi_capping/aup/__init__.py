"""
Acceptable Use Policy (AUP) compliance module for monitoring and enforcement.
"""

import json
import logging
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import urllib.parse

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """Types of AUP violations."""
    CONTENT_VIOLATION = "content_violation"
    BANDWIDTH_ABUSE = "bandwidth_abuse"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE_DETECTED = "malware_detected"
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    HARASSMENT = "harassment"
    SPAM = "spam"
    ILLEGAL_ACTIVITY = "illegal_activity"


class ViolationSeverity(Enum):
    """Severity levels for violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContentCategory(Enum):
    """Content filtering categories."""
    ADULT = "adult"
    GAMBLING = "gambling"
    MALWARE = "malware"
    SOCIAL_MEDIA = "social_media"
    STREAMING = "streaming"
    GAMING = "gaming"
    P2P = "p2p"
    EDUCATIONAL = "educational"
    GENERAL = "general"
    NEWS = "news"
    BUSINESS = "business"


@dataclass
class AUPViolation:
    """AUP violation record."""
    id: str
    user_id: str
    device_mac: str
    violation_type: ViolationType
    severity: ViolationSeverity
    description: str
    evidence: Dict[str, Any]
    timestamp: datetime
    resolved: bool = False
    resolution_notes: str = ""
    penalty_applied: str = ""


@dataclass
class ContentFilter:
    """Content filtering rule."""
    id: str
    name: str
    category: ContentCategory
    patterns: List[str]  # URL patterns, domains, keywords
    action: str  # block, warn, log, allow
    enabled: bool = True
    whitelist_exceptions: List[str] = None


@dataclass
class AUPPolicy:
    """Acceptable Use Policy definition."""
    id: str
    name: str
    version: str
    effective_date: datetime
    content_filters: List[ContentFilter]
    bandwidth_limits: Dict[str, Any]
    time_restrictions: Dict[str, Any]
    monitoring_rules: Dict[str, Any]
    violation_thresholds: Dict[str, int]
    penalties: Dict[str, List[str]]


class AUPMonitor:
    """Monitors network activity for AUP compliance."""
    
    def __init__(self):
        self.violations: Dict[str, AUPViolation] = {}
        self.content_filters: Dict[str, ContentFilter] = {}
        self.policies: Dict[str, AUPPolicy] = {}
        self.user_violations: Dict[str, List[str]] = {}  # user_id -> violation_ids
        self.monitoring_active = True
        
        # Initialize default content filters
        self._initialize_default_filters()
    
    def _initialize_default_filters(self):
        """Initialize default content filtering rules."""
        default_filters = [
            ContentFilter(
                id="adult_content",
                name="Adult Content Filter",
                category=ContentCategory.ADULT,
                patterns=[
                    r".*porn.*",
                    r".*xxx.*",
                    r".*adult.*",
                    r".*sex.*",
                    # Add more patterns as needed
                ],
                action="block"
            ),
            ContentFilter(
                id="gambling",
                name="Gambling Sites Filter",
                category=ContentCategory.GAMBLING,
                patterns=[
                    r".*casino.*",
                    r".*poker.*",
                    r".*betting.*",
                    r".*gamble.*"
                ],
                action="block"
            ),
            ContentFilter(
                id="malware",
                name="Malware and Phishing Filter",
                category=ContentCategory.MALWARE,
                patterns=[
                    r".*phishing.*",
                    r".*malware.*",
                    r".*virus.*",
                    r".*suspicious-domain\.com"
                ],
                action="block"
            ),
            ContentFilter(
                id="social_media_limit",
                name="Social Media Time Limits",
                category=ContentCategory.SOCIAL_MEDIA,
                patterns=[
                    r".*facebook\.com.*",
                    r".*twitter\.com.*",
                    r".*instagram\.com.*",
                    r".*tiktok\.com.*",
                    r".*snapchat\.com.*"
                ],
                action="warn"
            )
        ]
        
        for filter_rule in default_filters:
            self.content_filters[filter_rule.id] = filter_rule
    
    def add_content_filter(self, content_filter: ContentFilter) -> bool:
        """Add a content filtering rule."""
        try:
            self.content_filters[content_filter.id] = content_filter
            logger.info(f"Content filter {content_filter.id} added successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to add content filter {content_filter.id}: {e}")
            return False
    
    def check_content_compliance(self, url: str, user_id: str, device_mac: str) -> Dict[str, Any]:
        """Check if content access complies with AUP."""
        result = {
            'allowed': True,
            'action': 'allow',
            'matched_filters': [],
            'warnings': [],
            'violations': []
        }
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.lower()
        full_url = url.lower()
        
        # Check against content filters
        for filter_rule in self.content_filters.values():
            if not filter_rule.enabled:
                continue
            
            # Check if URL matches any patterns
            for pattern in filter_rule.patterns:
                if re.search(pattern, full_url) or re.search(pattern, domain):
                    result['matched_filters'].append(filter_rule.id)
                    
                    # Check whitelist exceptions
                    if filter_rule.whitelist_exceptions:
                        if any(re.search(exc, full_url) for exc in filter_rule.whitelist_exceptions):
                            continue
                    
                    # Apply filter action
                    if filter_rule.action == "block":
                        result['allowed'] = False
                        result['action'] = 'block'
                        violation = self._create_violation(
                            user_id, device_mac, ViolationType.CONTENT_VIOLATION,
                            ViolationSeverity.MEDIUM,
                            f"Blocked access to {filter_rule.category.value} content",
                            {'url': url, 'filter': filter_rule.id}
                        )
                        result['violations'].append(violation.id)
                    
                    elif filter_rule.action == "warn":
                        result['warnings'].append(f"Warning: Accessing {filter_rule.category.value} content")
                    
                    elif filter_rule.action == "log":
                        logger.info(f"User {user_id} accessed {filter_rule.category.value} content: {url}")
                    
                    break  # First match wins
        
        return result
    
    def check_bandwidth_compliance(self, user_id: str, device_mac: str, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check bandwidth usage compliance."""
        result = {
            'compliant': True,
            'violations': [],
            'warnings': []
        }
        
        # Get user's bandwidth usage
        download_mb = usage_data.get('download_mb', 0)
        upload_mb = usage_data.get('upload_mb', 0)
        session_duration = usage_data.get('session_duration', 0)
        
        # Check for bandwidth abuse patterns
        if download_mb > 1000:  # More than 1GB in session
            violation = self._create_violation(
                user_id, device_mac, ViolationType.BANDWIDTH_ABUSE,
                ViolationSeverity.MEDIUM,
                f"Excessive bandwidth usage: {download_mb}MB downloaded",
                usage_data
            )
            result['violations'].append(violation.id)
            result['compliant'] = False
        
        # Check for sustained high usage
        if session_duration > 3600 and (download_mb + upload_mb) / (session_duration / 3600) > 50:  # >50MB/hour
            result['warnings'].append("Sustained high bandwidth usage detected")
        
        return result
    
    def check_time_compliance(self, user_id: str, access_time: datetime = None) -> Dict[str, Any]:
        """Check if access time complies with time restrictions."""
        if access_time is None:
            access_time = datetime.now()
        
        result = {
            'allowed': True,
            'violations': [],
            'restrictions': []
        }
        
        # Example time restrictions (can be configured per user group)
        current_hour = access_time.hour
        current_day = access_time.strftime('%A')
        
        # Night time restrictions for students (example)
        if user_id.startswith('student_'):
            if current_hour < 6 or current_hour > 23:
                result['restrictions'].append("Night time access restrictions apply")
                # This might result in reduced bandwidth rather than blocking
        
        return result
    
    def detect_suspicious_activity(self, user_id: str, device_mac: str, activity_data: Dict[str, Any]) -> List[AUPViolation]:
        """Detect suspicious network activity."""
        violations = []
        
        # Check for potential malware activity
        if activity_data.get('unusual_ports'):
            violation = self._create_violation(
                user_id, device_mac, ViolationType.MALWARE_DETECTED,
                ViolationSeverity.HIGH,
                "Suspicious network activity detected - unusual port usage",
                activity_data
            )
            violations.append(violation)
        
        # Check for unauthorized access attempts
        if activity_data.get('failed_auth_attempts', 0) > 5:
            violation = self._create_violation(
                user_id, device_mac, ViolationType.UNAUTHORIZED_ACCESS,
                ViolationSeverity.HIGH,
                f"Multiple failed authentication attempts: {activity_data['failed_auth_attempts']}",
                activity_data
            )
            violations.append(violation)
        
        # Check for P2P activity
        if activity_data.get('p2p_detected'):
            violation = self._create_violation(
                user_id, device_mac, ViolationType.COPYRIGHT_INFRINGEMENT,
                ViolationSeverity.MEDIUM,
                "Peer-to-peer file sharing detected",
                activity_data
            )
            violations.append(violation)
        
        return violations
    
    def _create_violation(self, user_id: str, device_mac: str, violation_type: ViolationType,
                         severity: ViolationSeverity, description: str, evidence: Dict[str, Any]) -> AUPViolation:
        """Create a new AUP violation record."""
        violation_id = hashlib.md5(f"{user_id}{device_mac}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        violation = AUPViolation(
            id=violation_id,
            user_id=user_id,
            device_mac=device_mac,
            violation_type=violation_type,
            severity=severity,
            description=description,
            evidence=evidence,
            timestamp=datetime.now()
        )
        
        self.violations[violation_id] = violation
        
        # Add to user's violation history
        if user_id not in self.user_violations:
            self.user_violations[user_id] = []
        self.user_violations[user_id].append(violation_id)
        
        logger.warning(f"AUP violation created: {violation_id} for user {user_id}")
        return violation
    
    def get_user_violations(self, user_id: str, days: int = 30) -> List[AUPViolation]:
        """Get violations for a user within specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        user_violation_ids = self.user_violations.get(user_id, [])
        
        return [
            self.violations[vid] for vid in user_violation_ids
            if vid in self.violations and self.violations[vid].timestamp > cutoff_date
        ]
    
    def get_violation_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary of violations over specified period."""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_violations = [
            v for v in self.violations.values()
            if v.timestamp > cutoff_date
        ]
        
        summary = {
            'total_violations': len(recent_violations),
            'by_type': {},
            'by_severity': {},
            'by_user': {},
            'resolution_rate': 0
        }
        
        resolved_count = 0
        for violation in recent_violations:
            # Count by type
            vtype = violation.violation_type.value
            summary['by_type'][vtype] = summary['by_type'].get(vtype, 0) + 1
            
            # Count by severity
            severity = violation.severity.value
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            # Count by user
            user = violation.user_id
            summary['by_user'][user] = summary['by_user'].get(user, 0) + 1
            
            # Count resolved
            if violation.resolved:
                resolved_count += 1
        
        if recent_violations:
            summary['resolution_rate'] = (resolved_count / len(recent_violations)) * 100
        
        return summary
    
    def apply_penalty(self, violation_id: str, penalty: str, notes: str = "") -> bool:
        """Apply penalty for a violation."""
        if violation_id not in self.violations:
            return False
        
        violation = self.violations[violation_id]
        violation.penalty_applied = penalty
        violation.resolution_notes = notes
        violation.resolved = True
        
        logger.info(f"Penalty applied to violation {violation_id}: {penalty}")
        return True
    
    def generate_aup_report(self, user_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive AUP compliance report."""
        if user_id:
            violations = self.get_user_violations(user_id, days)
            report = {
                'user_id': user_id,
                'report_period_days': days,
                'total_violations': len(violations),
                'violations_by_type': {},
                'compliance_score': 100,
                'recommendations': []
            }
            
            for violation in violations:
                vtype = violation.violation_type.value
                report['violations_by_type'][vtype] = report['violations_by_type'].get(vtype, 0) + 1
            
            # Calculate compliance score (simple algorithm)
            if violations:
                score_deduction = min(len(violations) * 10, 80)  # Max 80 points deduction
                report['compliance_score'] = 100 - score_deduction
            
            # Generate recommendations
            if report['violations_by_type'].get('content_violation', 0) > 0:
                report['recommendations'].append("Review content access policies")
            if report['violations_by_type'].get('bandwidth_abuse', 0) > 0:
                report['recommendations'].append("Monitor bandwidth usage patterns")
            
        else:
            # System-wide report
            summary = self.get_violation_summary(days)
            report = {
                'system_wide': True,
                'report_period_days': days,
                'summary': summary,
                'top_violators': self._get_top_violators(days),
                'trending_violations': self._get_trending_violations(days)
            }
        
        report['generated_at'] = datetime.now().isoformat()
        return report
    
    def _get_top_violators(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get top violators in the specified period."""
        cutoff_date = datetime.now() - timedelta(days=days)
        user_counts = {}
        
        for violation in self.violations.values():
            if violation.timestamp > cutoff_date:
                user_counts[violation.user_id] = user_counts.get(violation.user_id, 0) + 1
        
        return sorted(
            [{'user_id': uid, 'violation_count': count} for uid, count in user_counts.items()],
            key=lambda x: x['violation_count'],
            reverse=True
        )[:10]
    
    def _get_trending_violations(self, days: int = 30) -> Dict[str, Any]:
        """Get trending violation types."""
        cutoff_date = datetime.now() - timedelta(days=days)
        daily_counts = {}
        
        for violation in self.violations.values():
            if violation.timestamp > cutoff_date:
                day = violation.timestamp.strftime('%Y-%m-%d')
                vtype = violation.violation_type.value
                
                if day not in daily_counts:
                    daily_counts[day] = {}
                daily_counts[day][vtype] = daily_counts[day].get(vtype, 0) + 1
        
        return daily_counts


class AUPPolicyManager:
    """Manages AUP policies and configurations."""
    
    def __init__(self):
        self.policies: Dict[str, AUPPolicy] = {}
        self.active_policy_id: Optional[str] = None
    
    def create_default_policy(self) -> AUPPolicy:
        """Create default AUP policy for NCUK."""
        default_filters = [
            ContentFilter(
                id="educational_content",
                name="Educational Content Filter",
                category=ContentCategory.EDUCATIONAL,
                patterns=[r".*\.edu.*", r".*academic.*", r".*research.*"],
                action="allow"
            )
        ]
        
        policy = AUPPolicy(
            id="ncuk_default_aup",
            name="NCUK Default Acceptable Use Policy",
            version="1.0",
            effective_date=datetime.now(),
            content_filters=default_filters,
            bandwidth_limits={
                'students': {'download_mbps': 10, 'upload_mbps': 5},
                'staff': {'download_mbps': 50, 'upload_mbps': 20}
            },
            time_restrictions={
                'students': {'night_hours': '23:00-06:00'},
                'guests': {'business_hours': '08:00-18:00'}
            },
            monitoring_rules={
                'log_all_access': True,
                'real_time_monitoring': True,
                'deep_packet_inspection': False
            },
            violation_thresholds={
                'content_violations_per_day': 3,
                'bandwidth_warnings_per_week': 5
            },
            penalties={
                'first_offense': ['warning', 'mandatory_training'],
                'repeat_offense': ['bandwidth_reduction', 'access_suspension'],
                'severe_violation': ['immediate_suspension', 'investigation']
            }
        )
        
        return policy
    
    def set_active_policy(self, policy_id: str) -> bool:
        """Set the active AUP policy."""
        if policy_id in self.policies:
            self.active_policy_id = policy_id
            logger.info(f"Active AUP policy set to: {policy_id}")
            return True
        return False
    
    def get_active_policy(self) -> Optional[AUPPolicy]:
        """Get the currently active AUP policy."""
        if self.active_policy_id:
            return self.policies.get(self.active_policy_id)
        return None