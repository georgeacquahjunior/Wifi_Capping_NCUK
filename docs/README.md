# NCUK WiFi Capping System - FreeRADIUS Setup

This repository contains the complete FreeRADIUS configuration for the NCUK (Northern Consortium of UK Universities) WiFi capping system. The system provides authentication, authorization, and accounting (AAA) services with bandwidth management and data capping capabilities.

## Features

- **User Authentication**: Secure WiFi authentication using RADIUS protocol
- **Bandwidth Management**: Per-user bandwidth limits and data caps
- **User Categories**: Different access levels for students, faculty, guests, and administrators
- **Time-based Restrictions**: Access control based on time of day
- **Data Tracking**: Daily data usage monitoring and limits
- **Device Management**: Concurrent device limits per user
- **Comprehensive Logging**: Detailed accounting and audit logs

## Architecture

The system consists of:
- FreeRADIUS server for authentication and accounting
- User database with predefined test accounts
- Bandwidth policies and rate limiting
- Client configuration for access points
- Monitoring and testing scripts

## Quick Start

### Prerequisites

- Ubuntu 18.04+ or Debian 9+ (recommended)
- Root or sudo access
- Network connectivity for package installation

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git
   cd Wifi_Capping_NCUK
   ```

2. Run the installation script:
   ```bash
   cd freeradius/scripts
   ./install.sh
   ```

3. Test the installation:
   ```bash
   ./test_auth.sh
   ```

### Manual Installation

If you prefer manual installation:

1. Install FreeRADIUS:
   ```bash
   sudo apt update
   sudo apt install freeradius freeradius-utils freeradius-common
   ```

2. Copy configuration files:
   ```bash
   sudo cp freeradius/config/* /etc/freeradius/3.0/
   sudo cp freeradius/users/* /etc/freeradius/3.0/users/
   ```

3. Set permissions:
   ```bash
   sudo chown -R freerad:freerad /etc/freeradius/3.0/
   sudo chmod 600 /etc/freeradius/3.0/users/users
   ```

4. Start the service:
   ```bash
   sudo systemctl enable freeradius
   sudo systemctl start freeradius
   ```

## Configuration

### Test Users

The system includes pre-configured test users:

| Username | Password | Type | Data Limit | Speed Limit | Session Time |
|----------|----------|------|------------|-------------|--------------|
| student1 | password123 | Student | 5GB/day | 10/10 Mbps | 8 hours |
| student2 | student2pass | Student | 2GB/day | 5/5 Mbps | 4 hours |
| faculty1 | faculty123 | Faculty | 20GB/day | 50/50 Mbps | 12 hours |
| guest1 | guest2024 | Guest | 500MB/day | 2/2 Mbps | 2 hours |
| admin1 | admin_ncuk_2024 | Admin | Unlimited | Unlimited | 24 hours |
| testuser | testpass | Test | Unlimited | Unlimited | Unlimited |

### Access Points Configuration

Configure your access points with these settings:

- **RADIUS Server IP**: Your FreeRADIUS server IP
- **Auth Port**: 1812
- **Acct Port**: 1813
- **Shared Secret**: See `clients.conf` for specific secrets

### Client Configuration

Edit `/etc/freeradius/3.0/clients.conf` to add your access points:

```
client your_ap {
    ipaddr = 192.168.1.100
    secret = your_shared_secret
    shortname = your-ap-name
    nas_type = access_point
}
```

## Testing

### Authentication Testing

Test individual users:
```bash
radtest student1 password123 localhost 1812 testing123
```

Test all users:
```bash
cd freeradius/scripts
./test_auth.sh
```

### Monitoring

View real-time logs:
```bash
sudo tail -f /var/log/freeradius/radius.log
```

View accounting data:
```bash
sudo ls -la /var/log/freeradius/radacct/
```

## Bandwidth Management

### Rate Limiting

The system uses Mikrotik-Rate-Limit attributes for bandwidth control:

```
Mikrotik-Rate-Limit = "download/upload burst_download/burst_upload data_limit/data_limit burst_time/burst_time"
```

Example:
- `10M/10M` = 10 Mbps download/upload
- `20M/20M` = 20 Mbps burst rates
- `5G/5G` = 5GB data limit
- `300/300` = 300 second burst time

### User Categories

**Students**:
- Basic: 5/5 Mbps, 2GB/day
- Standard: 10/10 Mbps, 5GB/day

**Faculty**:
- High-speed: 50/50 Mbps, 20GB/day
- Extended sessions: 12-hour limit

**Guests**:
- Limited: 2/2 Mbps, 500MB/day
- Short sessions: 2-hour limit

## Security Considerations

### Default Passwords

⚠️ **Important**: Change all default passwords before production use:

1. Edit `/etc/freeradius/3.0/users/users`
2. Update shared secrets in `/etc/freeradius/3.0/clients.conf`
3. Consider using SQL database for user management

### SSL/TLS

For production deployment:
1. Generate SSL certificates
2. Configure EAP-TLS for enhanced security
3. Use strong shared secrets (minimum 20 characters)

### Firewall Rules

Ensure proper firewall configuration:
```bash
sudo ufw allow 1812/udp  # RADIUS Auth
sudo ufw allow 1813/udp  # RADIUS Acct
```

## Troubleshooting

### Common Issues

1. **Service won't start**:
   ```bash
   sudo freeradius -X  # Debug mode
   sudo journalctl -u freeradius  # Check logs
   ```

2. **Authentication failures**:
   - Check user credentials in `/etc/freeradius/3.0/users/users`
   - Verify client shared secrets
   - Review logs for error messages

3. **Permission errors**:
   ```bash
   sudo chown -R freerad:freerad /etc/freeradius/3.0/
   sudo chmod 600 /etc/freeradius/3.0/users/users
   ```

### Debug Commands

Start FreeRADIUS in debug mode:
```bash
sudo systemctl stop freeradius
sudo freeradius -X
```

Test configuration syntax:
```bash
sudo freeradius -C
```

## Advanced Configuration

### SQL Database Integration

For larger deployments, consider using MySQL/PostgreSQL:

1. Install database module:
   ```bash
   sudo apt install freeradius-mysql
   ```

2. Configure SQL module in `/etc/freeradius/3.0/mods-available/sql`

3. Create database schema using provided SQL files

### LDAP Integration

For Active Directory integration:

1. Install LDAP module:
   ```bash
   sudo apt install freeradius-ldap
   ```

2. Configure LDAP module in `/etc/freeradius/3.0/mods-available/ldap`

### High Availability

For production environments:
- Set up FreeRADIUS in failover configuration
- Use database replication
- Implement load balancing

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review FreeRADIUS documentation
3. Examine log files for detailed error messages
4. Create an issue in this repository

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Acknowledgments

- FreeRADIUS team for the excellent RADIUS server
- NCUK for supporting open-source networking solutions
- Community contributors and testers