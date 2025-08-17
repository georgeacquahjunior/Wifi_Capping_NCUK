# WiFi Capping NCUK

A comprehensive, secure WiFi bandwidth management system designed for NCUK (Northern Consortium of UK Universities) institutions. This system provides robust policy enforcement, Acceptable Use Policy (AUP) compliance monitoring, and advanced security features.

## 🔒 Security Features

### Encryption & Data Protection
- **AES-256 Encryption**: All sensitive data encrypted at rest and in transit
- **TLS/SSL**: Mandatory encryption for all communications
- **Key Management**: Secure key generation, rotation, and storage
- **Certificate Management**: Automated SSL certificate generation and management

### Authentication & Authorization
- **Strong Password Policies**: Minimum 12 characters with complexity requirements
- **JWT Token Security**: Secure session management with token expiration
- **Role-Based Access Control**: Admin, Staff, and User roles with appropriate permissions
- **Account Lockout**: Protection against brute force attacks

### Policy Enforcement
- **Real-time Bandwidth Management**: Dynamic allocation based on user groups and time
- **Content Filtering**: Category-based filtering (adult, gambling, malware, etc.)
- **Time-based Restrictions**: Different policies for peak/off-peak hours
- **Fair Usage Policies**: Automatic throttling for excessive usage

### AUP Compliance
- **Real-time Monitoring**: Continuous network traffic analysis
- **Violation Detection**: Automated detection of policy violations
- **Audit Trails**: Comprehensive logging of all network activities
- **Compliance Reporting**: Regular reports for institutional review

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Administrative privileges for network management
- SSL certificates (self-signed certificates can be auto-generated)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git
   cd Wifi_Capping_NCUK
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run security verification**:
   ```bash
   python security_verify.py --config production
   ```

5. **Start the application**:
   ```bash
   python app.py
   ```

## 📋 Security Verification

The system includes a comprehensive security verification tool that validates:

- ✅ **Configuration Security**: SSL/TLS, encryption keys, database settings
- ✅ **Encryption Implementation**: End-to-end encryption verification
- ✅ **Access Control**: Authentication and authorization mechanisms
- ✅ **Policy Enforcement**: Bandwidth and content filtering validation
- ✅ **AUP Compliance**: Monitoring and violation detection systems

### Running Security Audit

```bash
# Full security audit for production
python security_verify.py --config production

# Generate detailed report
python security_verify.py --config production --output security_report.txt

# JSON format for automated processing
python security_verify.py --config production --json --output security_report.json
```

## 🏗️ Architecture

### Core Components

1. **Security Module** (`src/wifi_capping/security/`)
   - Encryption management (Fernet/AES-256)
   - Password hashing (bcrypt)
   - JWT token management
   - SSL certificate handling

2. **Policy Engine** (`src/wifi_capping/policy/`)
   - Bandwidth management
   - Time-based access controls
   - User group management
   - Traffic shaping and QoS

3. **AUP Monitor** (`src/wifi_capping/aup/`)
   - Content filtering
   - Violation detection
   - Compliance reporting
   - Audit logging

4. **Web Interface** (`src/wifi_capping/web/`)
   - Administrative dashboard
   - Policy management
   - Monitoring and reporting
   - User authentication

## 🔧 Configuration

### Environment Variables

Key security configuration options:

```bash
# Security Configuration
SECRET_KEY=your-secret-key-here-change-this
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this
ENCRYPTION_KEY=your-encryption-key-here-change-this

# SSL/TLS Configuration
SSL_CERT_PATH=/etc/ssl/certs/wifi-capping.crt
SSL_KEY_PATH=/etc/ssl/private/wifi-capping.key
SSL_REQUIRED=true

# Database Security
DATABASE_URL=sqlite:///wifi_capping.db
DATABASE_ENCRYPTION=true

# AUP Configuration
AUP_ENABLED=true
CONTENT_FILTERING=true
AUDIT_LOGGING=true
```

### Default User Groups

The system comes with pre-configured user groups:

- **Students**: 10MB/s download, 5MB/s upload, time restrictions
- **Staff**: 50MB/s download, 20MB/s upload, full access
- **Guests**: 2MB/s download, 1MB/s upload, limited hours

## 📊 Monitoring & Reporting

### Real-time Dashboard
- Active session monitoring
- Bandwidth usage analytics
- Security event tracking
- Policy compliance metrics

### API Endpoints

Core API endpoints for integration:

```bash
# Policy evaluation
POST /api/network/evaluate

# Session management
POST /api/network/session/start
POST /api/network/session/{id}/update
POST /api/network/session/{id}/end

# AUP compliance
POST /api/aup/check-content
POST /api/aup/report-activity

# System health
GET /api/health
```

## 🛡️ Security Best Practices

### For Administrators

1. **Regular Security Audits**: Run `security_verify.py` monthly
2. **Key Rotation**: Update encryption keys quarterly
3. **Certificate Management**: Monitor SSL certificate expiration
4. **Log Monitoring**: Review security events and violations daily
5. **Updates**: Keep system and dependencies updated

### For Security Specialists

1. **Penetration Testing**: Conduct quarterly security assessments
2. **Compliance Verification**: Ensure AUP compliance monitoring is active
3. **Incident Response**: Test incident response procedures regularly
4. **Backup Security**: Verify encrypted backups and recovery procedures

## 📚 Documentation

- [Security Documentation](docs/SECURITY.md) - Comprehensive security guide
- [API Documentation](docs/API.md) - Complete API reference
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions

## 🧪 Testing

Run the security test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run security tests
python -m pytest tests/test_security.py -v

# Generate coverage report
python -m pytest tests/ --cov=wifi_capping --cov-report=html
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run security tests
4. Submit a pull request with security verification results

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For security-related issues or questions:
- Security Team: security@ncuk.ac.uk
- Technical Support: support@ncuk.ac.uk
- Emergency Contact: +44 (0) 161 XXX XXXX

## 🏆 Security Compliance

- ✅ GDPR compliant for student data protection
- ✅ ISO 27001 information security management alignment
- ✅ NIST cybersecurity framework compliance
- ✅ Educational institution security requirements
- ✅ Network security best practices implementation

---

**Note**: This system is designed for educational institutions and includes appropriate security measures for handling student and staff network access. All security features have been verified and tested for production deployment.