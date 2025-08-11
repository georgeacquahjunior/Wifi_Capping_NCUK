# WiFi Monitoring and Security System for NCUK

A comprehensive WiFi network monitoring and security management system designed for the Northern Consortium of UK Universities (NCUK). This system monitors for suspicious network activity, manages security updates, and provides automated threat detection capabilities.

## Features

### 🔍 Network Monitoring
- **Real-time device tracking** - Monitor connected devices and detect unauthorized access
- **Traffic pattern analysis** - Identify unusual bandwidth usage and suspicious traffic
- **Port scanning detection** - Alert on suspicious port access attempts
- **Device whitelisting** - Maintain trusted device lists based on MAC address patterns

### 🛡️ Security Management
- **Automated security updates** - Keep system packages and dependencies current
- **Vulnerability scanning** - Regular checks for known security vulnerabilities
- **Configuration security** - Audit configuration files for security issues
- **Threat intelligence** - Integration with security databases and CVE feeds

### 📊 Monitoring & Reporting
- **Real-time alerting** - Immediate notifications for security events
- **Comprehensive logging** - Detailed audit trails and event history
- **Status dashboards** - System health and security status reports
- **Data export** - Export security events and reports for analysis

## Quick Start

### Installation

1. **Run the automated setup**:
   ```bash
   sudo ./setup.sh
   ```

2. **Configure the system**:
   ```bash
   nano config.yml  # Edit configuration to match your network
   ```

3. **Start monitoring**:
   ```bash
   sudo systemctl start wifi-monitor
   sudo systemctl enable wifi-monitor
   ```

## Configuration

The system is configured through `config.yml`. Key sections include:

- **Monitoring thresholds** - Device limits, bandwidth alerts, suspicious ports
- **Security settings** - Auto-update preferences, alert configurations
- **Network settings** - Interface selection, trusted device patterns

## Usage

### Basic Commands

**Start monitoring**:
```bash
python3 wifi_monitor.py --daemon
```

**Check system status**:
```bash
python3 wifi_monitor.py --status
```

**Run security scan**:
```bash
python3 security_manager.py --scan
```

**Apply security updates**:
```bash
python3 security_manager.py --check --apply
```

### Utility Scripts

- `./check_status.sh` - Check overall system status
- `./run_updates.sh` - Run manual security updates
- `./emergency_stop.sh` - Emergency stop all monitoring

## Security Features

- **Suspicious Activity Detection** - Monitors for unauthorized devices, unusual traffic patterns, and port scanning
- **Automated Security Updates** - Keeps system packages and Python dependencies current
- **Vulnerability Scanning** - Regular checks against known security databases
- **Configuration Auditing** - Scans configuration files for security issues

## Requirements

- Python 3.6+
- Linux system with systemd
- Network interface access
- Sudo privileges for system updates

## Testing

Run the comprehensive test suite:
```bash
python3 test_suite.py
```

## License

This project is licensed under the MIT License.