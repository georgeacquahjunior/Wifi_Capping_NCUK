# NCUK WiFi Capping System

A complete FreeRADIUS-based WiFi authentication and bandwidth management system for NCUK (Northern Consortium of UK Universities).

## Features

- **RADIUS Authentication**: Secure WiFi user authentication
- **Bandwidth Management**: Per-user speed and data limits
- **User Categories**: Student, Faculty, Guest, and Admin accounts
- **Data Capping**: Daily data usage limits with automatic reset
- **Time Restrictions**: Access control based on time of day
- **Comprehensive Logging**: Detailed authentication and accounting logs

## Quick Start

1. **Install FreeRADIUS**:
   ```bash
   cd freeradius/scripts
   ./install.sh
   ```

2. **Test Authentication**:
   ```bash
   ./test_auth.sh
   ```

3. **Configure Access Points**:
   - RADIUS Server: Your server IP
   - Auth Port: 1812
   - Acct Port: 1813
   - Shared Secret: See `freeradius/config/clients.conf`

## Test Users

| Username | Password | Type | Data Limit | Speed Limit |
|----------|----------|------|------------|-------------|
| student1 | password123 | Student | 5GB/day | 10/10 Mbps |
| faculty1 | faculty123 | Faculty | 20GB/day | 50/50 Mbps |
| guest1 | guest2024 | Guest | 500MB/day | 2/2 Mbps |
| admin1 | admin_ncuk_2024 | Admin | Unlimited | Unlimited |

## Documentation

See [docs/README.md](docs/README.md) for detailed installation, configuration, and troubleshooting instructions.

## Security Note

⚠️ **Change all default passwords and secrets before production use!**

## Structure

```
├── freeradius/
│   ├── config/          # FreeRADIUS configuration files
│   ├── users/           # User authentication database
│   └── scripts/         # Installation and testing scripts
└── docs/               # Comprehensive documentation
```
