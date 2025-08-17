# WiFi Capping NCUK - Quick Installation Guide

This guide demonstrates the network administrator validation flow for the FreeRADIUS-NAS-Backend system.

## Quick Setup (Development Mode)

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git
cd Wifi_Capping_NCUK

# Setup environment
cp .env.example .env
```

### 2. Install Dependencies
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install MySQL (if not already installed)
# Ubuntu/Debian:
sudo apt-get install mysql-server
# CentOS/RHEL:
sudo yum install mysql-server
```

### 3. Database Setup
```bash
# Create database and user
mysql -u root -p << EOF
CREATE DATABASE wifi_capping;
CREATE USER 'radius_user'@'localhost' IDENTIFIED BY 'radius_password';
GRANT ALL PRIVILEGES ON wifi_capping.* TO 'radius_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# Load schema
mysql -u root -p wifi_capping < database/schema.sql
```

### 4. Start the Backend
```bash
# Start the NAS backend API
python3 backend/nas/radius_backend.py
```

### 5. Network Administrator Validation

In a new terminal, run the validation tools:

```bash
# Complete validation report
python3 admin_tools/validation_tool.py --report

# Test specific components
python3 admin_tools/validation_tool.py --test db
python3 admin_tools/validation_tool.py --test api  
python3 admin_tools/validation_tool.py --test auth
python3 admin_tools/validation_tool.py --test accounting
python3 admin_tools/validation_tool.py --test nas

# Show active sessions
python3 admin_tools/validation_tool.py --sessions

# Reset user data
python3 admin_tools/validation_tool.py --reset-user testuser1
```

### 6. Run Test Suite
```bash
# Run comprehensive tests
python3 tests/test_radius_flow.py
```

## Expected Output

### Validation Report
```
==============================================================
FREERADIUS-NAS-BACKEND VALIDATION REPORT
==============================================================
Timestamp: 2024-01-01T12:00:00.000000

--- Database Connection ---
✓ Database connection successful. Found 3 users.

--- Backend API ---
✓ Backend API is healthy. Total users: 3

--- NAS Device Configuration ---
✓ Found 3 NAS devices:
  - Main WiFi Controller (192.168.1.1) - Active
  - Library WiFi Controller (192.168.1.2) - Active
  - Dorm WiFi Controller (192.168.1.3) - Active

--- RADIUS Authentication ---
✓ Authentication successful for testuser1
  Data remaining: 2000 MB

--- Accounting Flow ---
✓ Accounting session started: test-session-20240101-120000
✓ Accounting session updated with data usage
✓ Accounting session stopped successfully

==============================================================
SUMMARY
==============================================================
Database Connection: PASS
Backend API: PASS
NAS Device Configuration: PASS
RADIUS Authentication: PASS
Accounting Flow: PASS

Overall: 5/5 tests passed
✓ All tests passed! FreeRADIUS-NAS-Backend flow is properly configured.
```

### API Testing
You can also test the API directly:

```bash
# Test authentication
curl -X POST http://localhost:5000/api/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser1","password":"password123","nas_ip":"192.168.1.1"}'

# Test status
curl http://localhost:5000/api/status
```

## FreeRADIUS Integration (Production)

For full FreeRADIUS integration:

```bash
# Install FreeRADIUS
sudo apt-get install freeradius freeradius-mysql freeradius-utils

# Copy configurations
sudo cp config/freeradius/* /etc/freeradius/3.0/

# Enable the REST module and wifi-capping site
sudo ln -sf /etc/freeradius/3.0/mods-available/rest /etc/freeradius/3.0/mods-enabled/
sudo ln -sf /etc/freeradius/3.0/sites-available/wifi-capping /etc/freeradius/3.0/sites-enabled/

# Start FreeRADIUS
sudo systemctl start freeradius
sudo systemctl enable freeradius
```

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check MySQL service: `sudo systemctl status mysql`
   - Verify credentials in `.env` file
   - Test connection: `mysql -u radius_user -p wifi_capping`

2. **Backend API unhealthy**
   - Check if port 5000 is available: `netstat -tlnp | grep 5000`
   - Review backend logs for errors
   - Verify environment variables are loaded

3. **Authentication failures**
   - Check user credentials in database
   - Verify NAS IP address configuration
   - Review data limits and usage

## Network Administrator Workflow

1. **Daily Health Check**
   ```bash
   python3 admin_tools/validation_tool.py --report
   ```

2. **Monitor Active Sessions**
   ```bash
   python3 admin_tools/validation_tool.py --sessions
   ```

3. **User Management**
   ```bash
   # Reset user data usage
   python3 admin_tools/validation_tool.py --reset-user username
   ```

4. **Troubleshooting**
   ```bash
   # Test specific components
   python3 admin_tools/validation_tool.py --test auth
   python3 admin_tools/validation_tool.py --test accounting
   ```

This system provides comprehensive network administrator validation of the FreeRADIUS-NAS-Backend flow, ensuring proper operation of the WiFi capping system for NCUK.