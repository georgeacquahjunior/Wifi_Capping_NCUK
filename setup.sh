#!/bin/bash
# Setup script for WiFi Monitoring and Security System

set -e  # Exit on any error

echo "=== WiFi Monitoring and Security System Setup ==="
echo "Setting up NCUK WiFi monitoring and security system..."

# Check if running as root for system-level operations
check_root() {
    if [[ $EUID -eq 0 ]]; then
        echo "✓ Running with root privileges"
        return 0
    else
        echo "⚠ Some operations may require sudo privileges"
        return 1
    fi
}

# Install system dependencies
install_system_deps() {
    echo "Installing system dependencies..."
    
    # Update package list
    sudo apt update
    
    # Install required system packages
    sudo apt install -y \
        python3-dev \
        python3-pip \
        python3-venv \
        libpcap-dev \
        net-tools \
        iproute2 \
        wireless-tools \
        curl \
        jq
    
    echo "✓ System dependencies installed"
}

# Create Python virtual environment
setup_python_env() {
    echo "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✓ Created Python virtual environment"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo "✓ Python dependencies installed"
    else
        echo "⚠ requirements.txt not found, installing minimal dependencies"
        pip install psutil netifaces pyyaml requests schedule
    fi
}

# Create necessary directories
create_directories() {
    echo "Creating necessary directories..."
    
    # Create log directory
    sudo mkdir -p /var/log/wifi_monitor
    sudo chown $USER:$USER /var/log/wifi_monitor
    
    # Create configuration directory
    mkdir -p ~/.config/wifi_monitor
    
    # Create data directory
    mkdir -p ./data
    mkdir -p ./reports
    
    echo "✓ Directories created"
}

# Setup configuration files
setup_config() {
    echo "Setting up configuration..."
    
    # Copy default config if it doesn't exist
    if [ ! -f "config.yml" ]; then
        echo "Creating default configuration..."
        cat > config.yml << 'EOF'
# WiFi Network Monitoring Configuration
monitoring:
  max_devices_per_hour: 50
  max_bandwidth_mbps: 1000
  suspicious_ports: [22, 23, 3389, 5900, 1433, 3306]
  scan_interval_seconds: 60
  unusual_traffic_threshold: 80
  connection_timeout_threshold: 30

security:
  auto_update: false  # Set to true for automatic updates
  update_check_interval_hours: 24
  alert_email: "admin@ncuk.ac.uk"
  alert_threshold: "medium"

logging:
  level: "INFO"
  file: "/var/log/wifi_monitor/wifi_monitor.log"
  max_size_mb: 100
  backup_count: 5

network:
  interface: "wlan0"  # Change to your network interface
  ssid: "NCUK_WIFI"   # Change to your network SSID
  trusted_mac_patterns:
    - "00:1B:44:*"    # Add your trusted device patterns
EOF
        echo "✓ Default configuration created"
        echo "⚠ Please edit config.yml to match your network setup"
    else
        echo "✓ Configuration file already exists"
    fi
}

# Create systemd service files
create_services() {
    echo "Creating systemd service files..."
    
    # WiFi Monitor service
    sudo tee /etc/systemd/system/wifi-monitor.service > /dev/null << EOF
[Unit]
Description=WiFi Security Monitor for NCUK
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python $(pwd)/wifi_monitor.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Security Update Manager service
    sudo tee /etc/systemd/system/security-updater.service > /dev/null << EOF
[Unit]
Description=Security Update Manager for WiFi Monitor
After=network.target

[Service]
Type=oneshot
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python $(pwd)/security_manager.py --check --apply
EOF
    
    # Security Update Timer
    sudo tee /etc/systemd/system/security-updater.timer > /dev/null << EOF
[Unit]
Description=Run security updates daily
Requires=security-updater.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    echo "✓ Systemd services created"
}

# Setup log rotation
setup_logrotate() {
    echo "Setting up log rotation..."
    
    sudo tee /etc/logrotate.d/wifi-monitor > /dev/null << EOF
/var/log/wifi_monitor/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 $USER $USER
    postrotate
        systemctl reload wifi-monitor || true
    endscript
}
EOF
    
    echo "✓ Log rotation configured"
}

# Create monitoring scripts
create_scripts() {
    echo "Creating utility scripts..."
    
    # Status check script
    cat > check_status.sh << 'EOF'
#!/bin/bash
echo "=== WiFi Monitor Status ==="
systemctl status wifi-monitor --no-pager
echo
echo "=== Recent Security Events ==="
python3 wifi_monitor.py --status
echo
echo "=== System Security Status ==="
python3 security_manager.py --scan
EOF
    chmod +x check_status.sh
    
    # Manual update script
    cat > run_updates.sh << 'EOF'
#!/bin/bash
echo "=== Running Security Updates ==="
python3 security_manager.py --check --apply --force
echo
echo "=== Generating Security Report ==="
python3 security_manager.py --report ./reports/security_report_$(date +%Y%m%d).json
EOF
    chmod +x run_updates.sh
    
    # Emergency stop script
    cat > emergency_stop.sh << 'EOF'
#!/bin/bash
echo "=== Emergency Stop ==="
sudo systemctl stop wifi-monitor
sudo systemctl stop security-updater.timer
echo "All monitoring services stopped"
EOF
    chmod +x emergency_stop.sh
    
    echo "✓ Utility scripts created"
}

# Test the installation
test_installation() {
    echo "Testing installation..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Test Python modules can be imported
    python3 -c "import wifi_monitor; import security_manager; print('✓ Python modules can be imported')"
    
    # Test configuration loading
    python3 -c "from wifi_monitor import WiFiSecurityMonitor; m = WiFiSecurityMonitor(); print('✓ Monitor can be initialized')"
    
    # Test security manager
    python3 -c "from security_manager import SecurityUpdateManager; s = SecurityUpdateManager(); print('✓ Security manager can be initialized')"
    
    # Run unit tests if available
    if [ -f "test_suite.py" ]; then
        echo "Running unit tests..."
        python3 test_suite.py
        if [ $? -eq 0 ]; then
            echo "✓ All tests passed"
        else
            echo "⚠ Some tests failed"
        fi
    fi
    
    echo "✓ Installation test completed"
}

# Main setup function
main() {
    echo "Starting setup process..."
    
    # Check system requirements
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed"
        exit 1
    fi
    
    if ! command -v sudo &> /dev/null; then
        echo "❌ sudo is required but not available"
        exit 1
    fi
    
    # Run setup steps
    install_system_deps
    setup_python_env
    create_directories
    setup_config
    create_services
    setup_logrotate
    create_scripts
    test_installation
    
    echo
    echo "=== Setup Complete ==="
    echo "✓ WiFi Monitoring and Security System installed successfully"
    echo
    echo "Next steps:"
    echo "1. Edit config.yml to match your network configuration"
    echo "2. Start the monitor: sudo systemctl start wifi-monitor"
    echo "3. Enable auto-start: sudo systemctl enable wifi-monitor"
    echo "4. Enable security updates: sudo systemctl enable security-updater.timer"
    echo "5. Check status: ./check_status.sh"
    echo
    echo "Important files:"
    echo "- Configuration: ./config.yml"
    echo "- Logs: /var/log/wifi_monitor/"
    echo "- Status script: ./check_status.sh"
    echo "- Update script: ./run_updates.sh"
    echo "- Emergency stop: ./emergency_stop.sh"
    echo
    echo "For help, run: python3 wifi_monitor.py --help"
}

# Run main function
main "$@"