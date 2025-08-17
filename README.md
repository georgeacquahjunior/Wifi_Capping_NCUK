# WiFi Capping System for NCUK

A comprehensive WiFi bandwidth management and access control system designed for Northern Consortium UK (NCUK) institutions. This system provides automated WiFi usage capping, user authentication, and administrative controls to ensure fair bandwidth distribution and network security.

## 🌟 Features

### Core Functionality
- **20GB Usage Capping**: Automatic bandwidth limitation with enforcement and user disconnection
- **Real-time Monitoring**: Live tracking of user bandwidth consumption
- **FreeRADIUS Integration**: Secure authentication and accounting through RADIUS protocol
- **Admin Dashboard**: Responsive web interface for system management

### Security & Access Control
- **Network Encryption**: WPA2/WPA3 security with configurable access policies
- **User Authentication**: Multi-factor authentication support
- **Policy Enforcement**: Automated Acceptable Use Policy (AUP) compliance
- **Security Monitoring**: Real-time threat detection and suspicious activity alerts

### Management & Reporting
- **Usage Analytics**: Comprehensive data visualization and reporting
- **User Management**: Account creation, modification, and deletion
- **Network Administration**: RADIUS server configuration and monitoring
- **Error Handling**: Robust error management with detailed logging

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   Backend API    │    │   FreeRADIUS    │
│   (Dashboard)   │◄──►│   (Node.js)      │◄──►│   (Auth/Acct)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    Database     │    │  Network Access  │    │  WiFi Access    │
│   (User Data)   │    │   Server (NAS)   │    │     Points      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Linux-based server (Ubuntu 20.04+ recommended)
- Node.js 16+ and npm
- MySQL/PostgreSQL database
- FreeRADIUS 3.0+
- Network infrastructure with RADIUS-capable access points

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git
   cd Wifi_Capping_NCUK
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Set up the database:
   ```bash
   npm run db:setup
   ```

5. Start the services:
   ```bash
   npm run start
   ```

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

## 📖 Documentation

- **[Deployment Guide](./DEPLOYMENT.md)** - Complete production deployment instructions
- **[Security Guidelines](./SECURITY.md)** - Security configuration and best practices
- **[API Documentation](./API.md)** - REST API endpoints and usage
- **[Contributing](./CONTRIBUTING.md)** - How to contribute to the project
- **[Changelog](./CHANGELOG.md)** - Version history and updates

## ⚙️ Configuration

### Environment Variables
```bash
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=wifi_capping
DB_USER=username
DB_PASS=password

# RADIUS
RADIUS_HOST=localhost
RADIUS_SECRET=shared_secret
RADIUS_AUTH_PORT=1812
RADIUS_ACCT_PORT=1813

# Application
APP_PORT=3000
JWT_SECRET=your_jwt_secret
BANDWIDTH_LIMIT=20GB
```

### FreeRADIUS Configuration
```bash
# /etc/freeradius/3.0/clients.conf
client nas {
    ipaddr = 192.168.1.0/24
    secret = shared_secret
    require_message_authenticator = yes
    nastype = other
}
```

## 🔧 Usage

### Admin Dashboard
Access the web interface at `http://your-server:3000/admin`

**Default credentials:**
- Username: `admin`
- Password: `admin123` (change immediately)

### Key Operations
1. **User Management**: Create, modify, and delete user accounts
2. **Usage Monitoring**: View real-time and historical usage data
3. **Policy Configuration**: Set bandwidth limits and access rules
4. **Security Monitoring**: Review security alerts and system logs

## 📊 Monitoring & Logging

### System Logs
- Application logs: `/var/log/wifi-capping/`
- RADIUS logs: `/var/log/freeradius/`
- Access logs: `/var/log/nginx/` (if using nginx proxy)

### Metrics
- Real-time bandwidth usage
- User connection statistics
- System performance metrics
- Security event tracking

## 🛠️ Troubleshooting

### Common Issues

**RADIUS Authentication Failures**
```bash
# Check RADIUS server status
sudo systemctl status freeradius
# Test RADIUS connectivity
radtest username password radius-server 1812 shared-secret
```

**Database Connection Issues**
```bash
# Verify database connectivity
npm run db:test
# Check database logs
sudo tail -f /var/log/mysql/error.log
```

**High Memory Usage**
```bash
# Monitor system resources
htop
# Restart services if needed
sudo systemctl restart wifi-capping
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Install development dependencies
npm install --dev
# Run tests
npm test
# Start development server
npm run dev
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🏫 About NCUK

This system is designed for institutions within the Northern Consortium UK (NCUK), providing standardized WiFi access management across member universities and colleges.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/georgeacquahjunior/Wifi_Capping_NCUK/issues)
- **Documentation**: [Project Wiki](https://github.com/georgeacquahjunior/Wifi_Capping_NCUK/wiki)
- **Email**: support@ncuk-wifi.org

---

**Version**: 1.0.0  
**Last Updated**: August 2025