# NCUK WiFi Capping System

A comprehensive WiFi network management system designed for educational institutions, specifically the Northern Consortium UK (NCUK). This system provides robust network encryption, access control policies, and bandwidth management capabilities.

## Features

### 🔒 Network Encryption & Security
- **Multi-Protocol Support**: WPA2/WPA3-PSK and Enterprise authentication
- **Dynamic Key Management**: Automatic PSK generation and rotation
- **Certificate Management**: Enterprise-grade certificate handling
- **Security Policies**: Configurable encryption standards and validation

### 👥 Access Control & User Management
- **Role-Based Access**: Support for Admin, Faculty, Staff, Student, and Guest roles
- **MAC Address Filtering**: Whitelist/blacklist management
- **Time-Based Access**: Configurable access windows by user role
- **Session Management**: Concurrent session limits and timeout controls
- **Guest Access**: Temporary credentials with automatic expiration

### 📊 Bandwidth Management & QoS
- **Per-User Limits**: Customizable download/upload speed limits
- **Traffic Classification**: Priority-based Quality of Service (QoS)
- **Fair Usage Policy**: Automatic throttling for heavy users
- **Real-time Monitoring**: Bandwidth usage tracking and reporting
- **Emergency Controls**: System-wide bandwidth throttling capabilities

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git
cd Wifi_Capping_NCUK
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the system:
```bash
cp config/system_config.yaml.example config/system_config.yaml
# Edit the configuration file as needed
```

### Running the System

1. **Test Configuration**:
```bash
python wifi_capping_system.py --test
```

2. **Start the System**:
```bash
python wifi_capping_system.py
```

3. **Run with Custom Configuration**:
```bash
python wifi_capping_system.py --config /path/to/config.yaml
```

## Configuration

The system is configured through `config/system_config.yaml`. Key sections include:

### Network Settings
```yaml
network:
  primary_ssid: "NCUK-WiFi"
  guest_ssid: "NCUK-Guest"
  interface: "wlan0"
  channel: 6
  country_code: "GB"
```

### Encryption Policies
```yaml
encryption:
  default_type: "wpa3-psk"
  security_policies:
    min_password_length: 12
    key_rotation_days: 90
```

### Access Control
```yaml
access_control:
  mac_filtering:
    enabled: true
    default_policy: "deny"
  time_restrictions:
    enabled: true
```

### Bandwidth Limits
```yaml
bandwidth:
  limits:
    student:
      download: 10  # Mbps
      upload: 5
    faculty:
      download: 200
      upload: 100
```

## API Usage

### Creating Users
```python
from src.access_control import AccessControl, UserRole, AccessLevel

access_control = AccessControl()

# Create a student user
user = access_control.create_user(
    username="john.doe",
    email="john.doe@student.ncuk.edu",
    role=UserRole.STUDENT,
    access_level=AccessLevel.BASIC,
    mac_addresses=["AA:BB:CC:DD:EE:FF"]
)
```

### Managing Encryption
```python
from src.encryption import NetworkEncryption, EncryptionType, SecurityLevel

encryption = NetworkEncryption()

# Create WPA3 network policy
policy = encryption.create_encryption_policy(
    network_id="SecureNetwork",
    encryption_type=EncryptionType.WPA3_PSK,
    security_level=SecurityLevel.HIGH
)

# Generate hostapd configuration
config = encryption.generate_hostapd_config("SecureNetwork")
```

### Bandwidth Management
```python
from src.bandwidth import BandwidthManager

bandwidth_mgr = BandwidthManager(interface="wlan0")

# Set user bandwidth limits
bandwidth_mgr.set_user_bandwidth_limit(
    user_id="user123",
    download_mbps=25.0,
    upload_mbps=10.0,
    priority=60
)

# Generate usage report
report = bandwidth_mgr.generate_usage_report()
```

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                WiFi Capping System                 │
├─────────────────────────────────────────────────────┤
│  Main Application (wifi_capping_system.py)         │
├─────────────────┬───────────────┬───────────────────┤
│  Encryption     │ Access Control│ Bandwidth Manager │
│  - WPA2/WPA3    │ - User Mgmt   │ - QoS Rules       │
│  - Certificates │ - MAC Filter  │ - Traffic Shaping │
│  - Key Rotation │ - Time Access │ - Usage Monitoring│
└─────────────────┴───────────────┴───────────────────┘
```

## Testing

Run the comprehensive test suite:

```bash
python -m pytest tests/ -v
```

Or run specific test modules:

```bash
# Test encryption functionality
python tests/test_wifi_system.py TestNetworkEncryption

# Test access control
python tests/test_wifi_system.py TestAccessControl

# Test bandwidth management
python tests/test_wifi_system.py TestBandwidthManager
```

## Security Considerations

### Default Credentials
⚠️ **Important**: Change default admin credentials before deployment:
- Default admin username: `admin`
- Default admin password: `admin123`

### Network Security
- WPA3 is recommended for new deployments
- Regular key rotation is enforced
- Certificate validation is performed for enterprise networks
- MAC address randomization detection is supported

### System Security
- Sensitive data is encrypted at rest
- Password hashing uses PBKDF2 with high iteration count
- Session management prevents unauthorized access
- Audit logging tracks all security events

## Monitoring & Maintenance

### Usage Reports
Generate detailed usage reports:
```bash
# Via API
report = system.get_usage_report()

# Via command line (future feature)
python wifi_capping_system.py --report --format json
```

### Log Files
- Access logs: `/var/log/ncuk-wifi/access.log`
- Security logs: `/var/log/ncuk-wifi/security.log`
- Bandwidth logs: `/var/log/ncuk-wifi/bandwidth.log`
- Error logs: `/var/log/ncuk-wifi/error.log`

### Maintenance Tasks
- Automatic cleanup of expired guest accounts
- Fair usage policy enforcement
- Log rotation and archival
- Database optimization

## Integration

### LDAP/Active Directory
```yaml
integration:
  ldap:
    enabled: true
    server: "ldap.ncuk.edu"
    base_dn: "ou=users,dc=ncuk,dc=edu"
```

### External Authentication
```yaml
integration:
  external_auth:
    enabled: true
    type: "oauth2"
    provider_url: "https://auth.ncuk.edu"
```

## Troubleshooting

### Common Issues

1. **Traffic Control Initialization Failed**
   - Ensure the system has root privileges
   - Check that the network interface exists
   - Verify tc (traffic control) utilities are installed

2. **User Authentication Failing**
   - Check password hash validation
   - Verify user account is active
   - Confirm time-based access rules

3. **Bandwidth Limits Not Applied**
   - Verify traffic control is initialized
   - Check that user has bandwidth limits set
   - Ensure network interface is active

### Debug Mode
Enable debug logging:
```yaml
development:
  debug_mode: true
  verbose_logging: true
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact the NCUK IT team
- Check the documentation in the `docs/` directory

## Acknowledgments

- Northern Consortium UK (NCUK) for project requirements
- Educational technology community for best practices
- Open source networking tools and libraries used in this project
