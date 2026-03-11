# WiFi Capping NCUK - FreeRADIUS CoA Configuration

This repository contains FreeRADIUS configuration files for implementing Change of Authorization (CoA) disconnect functionality for WiFi bandwidth capping in NCUK (Northern Consortium of UK Universities) networks.

## Overview

The configuration provides:
- **CoA (Change of Authorization) Support**: Dynamic session management and disconnect functionality
- **WiFi Bandwidth Capping**: Configurable bandwidth limits per user category
- **Session Monitoring**: Real-time tracking of data usage and session time
- **Automatic Disconnect**: Policy-based session termination for limit violations

## Features

### CoA Disconnect Functionality
- **RFC 5176 Compliant**: Standard CoA and Disconnect-Request packet support
- **Multiple Trigger Conditions**: Data limits, time limits, administrative actions
- **Real-time Processing**: Immediate session termination capabilities
- **Comprehensive Logging**: Detailed audit trail of all disconnect actions

### WiFi Capping Policies
- **User Categories**: Student, Staff, Guest, Admin with different limits
- **Bandwidth Profiles**: 5Mbps, 10Mbps, 20Mbps, 50Mbps, Unlimited
- **Session Timeouts**: 30min to 24h based on user type
- **Data Monitoring**: Daily/monthly usage tracking

## Configuration Files

### Core Configuration
- `radiusd.conf` - Main FreeRADIUS configuration with CoA listener
- `clients.conf` - NAS clients and CoA server definitions
- `proxy.conf` - Proxy and home server configuration for CoA
- `users` - Test user accounts with bandwidth profiles

### Virtual Servers
- `sites-available/default` - Main authentication/accounting server
- `sites-available/coa_disconnect` - CoA packet processing server

### Policies and Modules
- `policy.d/wifi_capping` - WiFi capping and monitoring policies
- `mods-enabled/modules.conf` - Module configurations
- `dictionary.ncuk` - Custom attributes for WiFi capping

### Scripts
- `scripts/coa_disconnect.sh` - Command-line CoA disconnect tool

## Quick Start

### 1. Installation Prerequisites
```bash
# Install FreeRADIUS server and client tools
sudo apt-get update
sudo apt-get install freeradius freeradius-utils

# Or on CentOS/RHEL:
sudo yum install freeradius freeradius-utils
```

### 2. Configuration Deployment
```bash
# Clone the repository
git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git
cd Wifi_Capping_NCUK

# Copy configuration files to FreeRADIUS directory
sudo cp radiusd.conf /etc/raddb/
sudo cp clients.conf /etc/raddb/
sudo cp proxy.conf /etc/raddb/
sudo cp users /etc/raddb/
sudo cp dictionary.ncuk /etc/raddb/

# Copy sites and policies
sudo cp -r sites-available/* /etc/raddb/sites-available/
sudo cp -r policy.d/* /etc/raddb/policy.d/
sudo cp -r mods-enabled/* /etc/raddb/mods-enabled/

# Enable sites
sudo ln -sf ../sites-available/default /etc/raddb/sites-enabled/
sudo ln -sf ../sites-available/coa_disconnect /etc/raddb/sites-enabled/
```

### 3. Testing Configuration
```bash
# Test configuration syntax
sudo radiusd -X

# Test authentication
echo "User-Name = testuser, User-Password = testpass" | radclient localhost auth testing123

# Test CoA disconnect
./scripts/coa_disconnect.sh -u testuser -r "Test disconnect"
```

## CoA Disconnect Usage

### Manual Disconnect
```bash
# Disconnect by username
./scripts/coa_disconnect.sh -u student -r "Data limit exceeded"

# Disconnect by session ID
./scripts/coa_disconnect.sh -s "ABC123456" -r "Administrative disconnect"

# Disconnect with custom NAS
./scripts/coa_disconnect.sh -u guest -n 192.168.1.10 -r "Policy violation"
```

### Programmatic Integration
```python
# Python example for sending CoA disconnect
import subprocess

def disconnect_user(username, reason="Administrative disconnect"):
    result = subprocess.run([
        "./scripts/coa_disconnect.sh",
        "-u", username,
        "-r", reason
    ], capture_output=True, text=True)
    
    return result.returncode == 0
```

## User Categories and Limits

| Category | Bandwidth | Session Time | Data Limit |
|----------|-----------|--------------|------------|
| Guest    | 5 Mbps    | 30 minutes   | 100 MB     |
| Student  | 20 Mbps   | 2 hours      | 1 GB       |
| Staff    | 50 Mbps   | 4 hours      | 5 GB       |
| Admin    | Unlimited | 24 hours     | Unlimited  |

## Monitoring and Logging

### Log Files
- `/var/log/radius/radius.log` - General FreeRADIUS logs
- `/var/log/radius/radacct/` - Accounting records
- Session tracking via `radutmp`

### CoA Events
All CoA disconnect events are logged with:
- Username and session ID
- Disconnect reason
- Timestamp and source IP
- Success/failure status

## Network Configuration

### Firewall Rules
```bash
# Allow RADIUS authentication/accounting
sudo iptables -A INPUT -p udp --dport 1812 -j ACCEPT
sudo iptables -A INPUT -p udp --dport 1813 -j ACCEPT

# Allow CoA/Disconnect (RFC 5176)
sudo iptables -A INPUT -p udp --dport 3799 -j ACCEPT
```

### NAS Configuration
Configure your WiFi controllers/access points with:
- RADIUS server IP and shared secret
- CoA server settings (port 3799)
- Accounting interim updates enabled

## Troubleshooting

### Common Issues

1. **CoA packets not received**
   - Check firewall rules (port 3799)
   - Verify shared secret matches
   - Confirm NAS CoA configuration

2. **Authentication failures**
   - Test with `radclient` command
   - Check user credentials in `users` file
   - Review logs for error messages

3. **Session not found for disconnect**
   - Verify session is active
   - Check Acct-Session-Id format
   - Ensure User-Name matches exactly

### Debug Mode
```bash
# Run FreeRADIUS in debug mode
sudo radiusd -X

# Test specific components
radclient localhost:3799 coa testing123 < test_coa.txt
```

## Security Considerations

- **Shared Secrets**: Use strong, unique secrets for each NAS
- **Network Isolation**: Isolate RADIUS traffic on management VLAN
- **Access Control**: Limit CoA client IP ranges
- **Audit Logging**: Enable detailed logging for compliance

## Integration Examples

### Bandwidth Management System
```bash
#!/bin/bash
# Monitor data usage and trigger disconnects
while read session_data; do
    if [ "$data_usage" -gt "$limit" ]; then
        ./scripts/coa_disconnect.sh -u "$username" -r "Data limit exceeded"
    fi
done
```

### Time-based Policies
```bash
# Disconnect guest users after hours
if [ "$(date +%H)" -gt 22 ]; then
    ./scripts/coa_disconnect.sh -u guest -r "Outside permitted hours"
fi
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test configurations thoroughly
4. Submit a pull request with detailed description

## License

This configuration is provided for educational and operational use in NCUK environments.

## Support

For issues or questions:
- Create GitHub issues for bugs/enhancements
- Review FreeRADIUS documentation for general RADIUS questions
- Consult RFC 5176 for CoA implementation details