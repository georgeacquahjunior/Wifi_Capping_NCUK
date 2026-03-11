"""
WiFi Capping NCUK - Core Package
A secure WiFi bandwidth management system for NCUK institutions.
"""

__version__ = "1.0.0"
__author__ = "NCUK Security Team"
__email__ = "security@ncuk.ac.uk"

from .core.app import create_app
from .core.config import Config

__all__ = ['create_app', 'Config']