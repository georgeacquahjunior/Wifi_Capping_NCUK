"""
System monitoring module for performance and security metrics.
"""

import psutil
import time
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SystemMonitor:
    """Monitors system performance and resource usage."""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count
                },
                'memory': {
                    'total_mb': memory.total / (1024 * 1024),
                    'available_mb': memory.available / (1024 * 1024),
                    'percent': memory.percent
                },
                'disk': {
                    'total_gb': disk.total / (1024 * 1024 * 1024),
                    'used_gb': disk.used / (1024 * 1024 * 1024),
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {
                'error': 'Failed to collect metrics',
                'timestamp': datetime.utcnow().isoformat()
            }