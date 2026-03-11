#!/usr/bin/env python3
"""
Setup script for WiFi Capping NCUK
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')

setup(
    name="wifi-capping-ncuk",
    version="1.0.0",
    author="WiFi Capping NCUK Team",
    author_email="",
    description="Secure WiFi bandwidth capping system with freeRADIUS integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/georgeacquahjunior/Wifi_Capping_NCUK",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "wifi-capping=wifi_capping.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "wifi_capping": ["dictionary"],
    },
    project_urls={
        "Bug Reports": "https://github.com/georgeacquahjunior/Wifi_Capping_NCUK/issues",
        "Source": "https://github.com/georgeacquahjunior/Wifi_Capping_NCUK",
        "Documentation": "https://github.com/georgeacquahjunior/Wifi_Capping_NCUK#readme",
    },
    keywords="wifi radius bandwidth capping network security freeradius",
    platforms=["Linux", "Unix"],
)