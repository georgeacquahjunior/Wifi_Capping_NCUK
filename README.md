# WiFi Capping NCUK - FreeRADIUS-NAS-Backend Validation System

A comprehensive WiFi access control and bandwidth capping system for NCUK (Northern Consortium of UK Universities) that integrates FreeRADIUS authentication with a custom NAS (Network Access Server) backend for network administrator validation.

## Overview

This system provides:
- **FreeRADIUS Integration**: Complete RADIUS authentication and accounting
- **NAS Backend**: RESTful API for RADIUS operations
- **Data Capping**: Per-user bandwidth monitoring and enforcement
- **Admin Validation**: Network administrator tools for flow validation
- **Session Management**: Real-time session tracking and control

## Architecture

```
[WiFi Controllers] → [FreeRADIUS] → [NAS Backend] → [MySQL Database]
                                          ↓
                              [Admin Validation Tools]
```

## Features

### Core Functionality
- ✅ RADIUS authentication with user credentials
- ✅ Accounting session management (start/update/stop)
- ✅ Data usage tracking and bandwidth capping
- ✅ Multiple NAS device support
- ✅ Real-time session monitoring

### Network Administrator Tools
- ✅ Flow validation testing
- ✅ Database connectivity verification
- ✅ API health monitoring
- ✅ Session management interface
- ✅ User data usage reports

### Security Features
- ✅ NAS device authentication
- ✅ Session isolation
- ✅ Admin audit logging
- ✅ Encrypted communications support

## Quick Start

### Prerequisites
- Python 3.8+
- MySQL/MariaDB 5.7+
- FreeRADIUS 3.0+ (optional for testing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git
   cd Wifi_Capping_NCUK
   ```

2. **Run the setup script**
   ```bash
   # For full system installation (requires root)
   sudo ./scripts/setup.sh
   
   # For development setup (user mode)
   ./scripts/setup.sh
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   nano .env
   ```

4. **Set up database**
   ```bash
   mysql -u root -p < database/schema.sql
   ```

5. **Start the backend**
   ```bash
   ./scripts/start_backend.sh
   ```

6. **Validate the installation**
   ```bash
   ./scripts/admin_validate.sh --report
   ```

## Configuration

### Environment Variables (.env)

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=wifi_capping
DB_USER=radius_user
DB_PASSWORD=radius_password

# FreeRADIUS Configuration
RADIUS_SECRET=testing123
RADIUS_HOST=localhost
RADIUS_AUTH_PORT=1812
RADIUS_ACCT_PORT=1813

# NAS Configuration
NAS_IP=192.168.1.1
NAS_SECRET=nas_secret_key
NAS_IDENTIFIER=wifi_controller

# Admin Configuration
ADMIN_PORT=5000
ADMIN_SECRET_KEY=admin_secret_key_change_me
```

### FreeRADIUS Configuration

The system includes pre-configured FreeRADIUS files:
- `config/freeradius/radiusd.conf` - Main FreeRADIUS configuration
- `config/freeradius/clients.conf` - NAS client definitions
- `config/freeradius/sites-available/wifi-capping` - Virtual server configuration
- `config/freeradius/mods-available/rest` - REST module for backend integration

## Usage

### Network Administrator Validation

The validation tool provides comprehensive testing of the FreeRADIUS-NAS-Backend flow:

```bash
# Run complete validation report
./scripts/admin_validate.sh --report

# Test specific components
./scripts/admin_validate.sh --test db        # Database connection
./scripts/admin_validate.sh --test api       # Backend API
./scripts/admin_validate.sh --test auth      # RADIUS authentication
./scripts/admin_validate.sh --test accounting # Accounting flow
./scripts/admin_validate.sh --test nas       # NAS device configuration

# Show active sessions
./scripts/admin_validate.sh --sessions

# Reset user data usage
./scripts/admin_validate.sh --reset-user testuser1
```

### API Endpoints

The NAS backend provides the following REST API endpoints:

#### Authentication
```bash
POST /api/auth
{
  "username": "testuser1",
  "password": "password123",
  "nas_ip": "192.168.1.1"
}
```

#### Accounting
```bash
# Start session
POST /api/accounting/start
{
  "session_id": "session-123",
  "username": "testuser1",
  "nas_ip": "192.168.1.1",
  "nas_port": 1
}

# Update session
POST /api/accounting/update
{
  "session_id": "session-123",
  "bytes_in": 1048576,
  "bytes_out": 524288
}

# Stop session
POST /api/accounting/stop
{
  "session_id": "session-123"
}
```

#### Status
```bash
GET /api/status
```

### Testing

Run the comprehensive test suite:

```bash
./scripts/run_tests.sh
```

## Database Schema

The system uses the following main tables:

- **users**: User credentials and data limits
- **radius_sessions**: Active and historical sessions
- **nas_devices**: Configured NAS devices
- **admin_log**: Administrative action audit trail

## Directory Structure

```
Wifi_Capping_NCUK/
├── admin_tools/           # Network administrator tools
│   └── validation_tool.py # Main validation interface
├── backend/               # NAS backend application
│   └── nas/
│       └── radius_backend.py # REST API server
├── config/                # Configuration files
│   └── freeradius/        # FreeRADIUS configurations
├── database/              # Database schemas and scripts
│   └── schema.sql         # MySQL database schema
├── docs/                  # Documentation
├── scripts/               # Setup and utility scripts
│   ├── setup.sh           # Main setup script
│   ├── start_backend.sh   # Backend startup
│   ├── admin_validate.sh  # Admin validation wrapper
│   └── run_tests.sh       # Test runner
├── tests/                 # Test suites
│   └── test_radius_flow.py # Main test suite
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify MySQL service is running
   - Check database credentials in `.env`
   - Ensure database schema is loaded

2. **Backend API Unhealthy**
   - Check if backend service is running
   - Verify port 5000 is available
   - Review backend logs

3. **RADIUS Authentication Failed**
   - Verify FreeRADIUS service is running
   - Check NAS client configuration
   - Review FreeRADIUS logs (`/var/log/freeradius/`)

4. **Test Failures**
   - Ensure all services are running
   - Check network connectivity
   - Verify test user credentials

### Logs

- Backend logs: Check console output when running `start_backend.sh`
- FreeRADIUS logs: `/var/log/freeradius/radius.log`
- Database logs: MySQL error logs
- Admin actions: `admin_log` table in database

## Development

### Adding New Features

1. Backend API: Extend `backend/nas/radius_backend.py`
2. Admin tools: Modify `admin_tools/validation_tool.py`
3. Tests: Add test cases to `tests/test_radius_flow.py`
4. Configuration: Update FreeRADIUS configs in `config/freeradius/`

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Security Considerations

- Change default passwords and secrets in production
- Use HTTPS for API communications in production
- Regularly rotate RADIUS shared secrets
- Monitor admin audit logs
- Implement proper firewall rules

## License

This project is developed for NCUK educational purposes.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review system logs
3. Run validation tests
4. Create an issue in the repository