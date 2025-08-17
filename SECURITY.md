# Security Guidelines

This document outlines security best practices, configuration guidelines, and compliance requirements for the WiFi Capping System.

## 🔒 Security Overview

The WiFi Capping System implements multi-layered security controls to protect user data, network infrastructure, and administrative access. This includes authentication mechanisms, encryption protocols, access controls, and monitoring capabilities.

## 🛡️ Core Security Principles

### 1. Defense in Depth
- Multiple security layers to prevent single points of failure
- Network segmentation and access controls
- Application-level and infrastructure-level security measures

### 2. Principle of Least Privilege
- Minimal access rights for users and services
- Role-based access control (RBAC)
- Regular access reviews and updates

### 3. Zero Trust Architecture
- Verify every user and device
- Continuous monitoring and validation
- Never trust, always verify approach

## 🔐 Authentication and Authorization

### RADIUS Authentication Security

#### Strong Password Policies
```bash
# Minimum password requirements
- Length: 12 characters minimum
- Complexity: Upper, lower, numbers, special characters
- History: Cannot reuse last 12 passwords
- Expiration: 90 days maximum
- Account lockout: 5 failed attempts, 30-minute lockout
```

#### Multi-Factor Authentication (MFA)
```bash
# Enable TOTP for administrative accounts
# Configure in .env
MFA_ENABLED=true
MFA_ISSUER=NCUK-WiFi-System
MFA_WINDOW=1
MFA_RECOVERY_CODES=10
```

#### Certificate-Based Authentication
```bash
# Client certificates for high-security areas
# Configure in FreeRADIUS
eap {
    tls-config tls-common {
        private_key_file = /etc/ssl/private/server.key
        certificate_file = /etc/ssl/certs/server.pem
        ca_file = /etc/ssl/certs/ca.pem
        dh_file = /etc/ssl/certs/dh2048.pem
        cipher_list = "HIGH:!aNULL:!MD5:!RC4:!3DES"
        cipher_server_preference = yes
        tls_min_version = "1.2"
        tls_max_version = "1.3"
    }
}
```

### Application Authentication

#### JWT Token Security
```bash
# Strong JWT configuration
JWT_SECRET=your_256_bit_secret_key_here_minimum_32_characters
JWT_EXPIRE_TIME=3600  # 1 hour
JWT_REFRESH_EXPIRE_TIME=604800  # 7 days
JWT_ALGORITHM=HS256
```

#### Session Management
```bash
# Secure session configuration
SESSION_SECRET=your_secure_session_secret_minimum_32_characters
SESSION_SECURE=true  # HTTPS only
SESSION_HTTP_ONLY=true
SESSION_SAME_SITE=strict
SESSION_MAX_AGE=1800000  # 30 minutes
```

## 🔑 Encryption Standards

### Data at Rest

#### Database Encryption
```sql
-- MySQL encryption at rest
ALTER TABLE users ENCRYPTION='Y';
ALTER TABLE user_sessions ENCRYPTION='Y';
ALTER TABLE audit_logs ENCRYPTION='Y';

-- Transparent data encryption
SET GLOBAL innodb_encryption_threads=4;
```

#### File System Encryption
```bash
# LUKS encryption for sensitive directories
sudo cryptsetup luksFormat /dev/sdb
sudo cryptsetup luksOpen /dev/sdb encrypted_storage
sudo mkfs.ext4 /dev/mapper/encrypted_storage
```

### Data in Transit

#### TLS Configuration
```nginx
# Nginx SSL/TLS security
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_timeout 10m;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;

# HSTS
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
```

#### RADIUS Encryption
```bash
# FreeRADIUS security configuration
# /etc/freeradius/3.0/radiusd.conf
security {
    max_attributes = 200
    reject_delay = 1
    status_server = yes
    allow_core_dumps = no
}

# Strong shared secrets (minimum 16 characters)
# Use cryptographically secure random generation
openssl rand -base64 32
```

## 🚧 Network Security

### Firewall Configuration

#### IPTables Rules
```bash
#!/bin/bash
# Comprehensive firewall rules

# Flush existing rules
iptables -F
iptables -t nat -F
iptables -t mangle -F

# Default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# SSH access (restrict source IPs)
iptables -A INPUT -p tcp --dport 22 -s 192.168.1.0/24 -j ACCEPT

# Web traffic
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# RADIUS traffic (restrict to NAS devices)
iptables -A INPUT -p udp --dport 1812 -s 192.168.2.0/24 -j ACCEPT
iptables -A INPUT -p udp --dport 1813 -s 192.168.2.0/24 -j ACCEPT

# Rate limiting for SSH
iptables -A INPUT -p tcp --dport 22 -m recent --name ssh --update --seconds 60 --hitcount 4 -j DROP
iptables -A INPUT -p tcp --dport 22 -m recent --name ssh --set -j ACCEPT

# Log dropped packets
iptables -A INPUT -j LOG --log-prefix "DROPPED: "
iptables -A INPUT -j DROP
```

### Network Segmentation

#### VLAN Configuration
```bash
# Management VLAN (ID: 100)
- Admin dashboard access
- System management
- Backup and monitoring

# User VLAN (ID: 200)
- Student/staff WiFi access
- Internet access with bandwidth limits
- Isolated from management network

# DMZ VLAN (ID: 300)
- Web servers
- Public-facing services
- Limited internal access
```

### VPN Access for Administration
```bash
# OpenVPN configuration for secure admin access
# /etc/openvpn/server.conf
port 1194
proto udp
dev tun
ca ca.crt
cert server.crt
key server.key
dh dh2048.pem
auth SHA256
cipher AES-256-CBC
user nobody
group nogroup
persist-key
persist-tun
status openvpn-status.log
verb 3
explicit-exit-notify 1
```

## 📊 Monitoring and Logging

### Security Event Monitoring

#### SIEM Integration
```bash
# Rsyslog configuration for centralized logging
# /etc/rsyslog.d/50-security.conf

# Application security events
:programname, isequal, "wifi-capping" @@siem-server:514

# RADIUS authentication events
:programname, isequal, "freeradius" @@siem-server:514

# System authentication events
authpriv.* @@siem-server:514

# Failed login attempts
:msg, contains, "Failed password" @@siem-server:514
:msg, contains, "Invalid user" @@siem-server:514
```

#### Real-time Alerting
```bash
# Configure fail2ban for intrusion detection
# /etc/fail2ban/jail.local

[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
backend = systemd

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3

[wifi-capping]
enabled = true
filter = wifi-capping
logpath = /opt/wifi-capping/logs/app.log
maxretry = 5
```

### Audit Logging

#### Database Audit Trail
```sql
-- Create audit tables
CREATE TABLE audit_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(50) NOT NULL,
    user_id INT,
    admin_user VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSON
);

CREATE TABLE audit_system (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'),
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_ip VARCHAR(45),
    additional_data JSON
);
```

#### File Integrity Monitoring
```bash
# AIDE configuration
# /etc/aide/aide.conf

/opt/wifi-capping/server.js f+p+u+g+s+m+c+md5+sha256
/opt/wifi-capping/.env f+p+u+g+s+m+c+md5+sha256
/etc/freeradius f+p+u+g+s+m+c+md5+sha256
/etc/nginx f+p+u+g+s+m+c+md5+sha256

# Initialize and check
aide --init
aide --check
```

## 🔍 Vulnerability Management

### Security Scanning

#### Automated Vulnerability Scanning
```bash
#!/bin/bash
# security-scan.sh

# Network scanning with nmap
nmap -sS -O -A localhost > /var/log/security/nmap-$(date +%Y%m%d).log

# Web application scanning with nikto
nikto -h https://localhost -output /var/log/security/nikto-$(date +%Y%m%d).txt

# SSL/TLS testing
testssl.sh --parallel https://localhost > /var/log/security/testssl-$(date +%Y%m%d).log

# System package vulnerabilities
apt list --upgradable > /var/log/security/upgradable-$(date +%Y%m%d).log
```

#### Dependency Scanning
```bash
# NPM audit for Node.js dependencies
npm audit --audit-level moderate

# Automated security updates
npm update
npm audit fix

# Alternative: use renovate or dependabot for automated PR
```

### Penetration Testing

#### Regular Security Assessments
```bash
# Quarterly penetration testing checklist:
1. External network perimeter testing
2. Wireless network security assessment
3. Web application security testing
4. Social engineering assessment
5. Physical security evaluation
```

## 🚨 Incident Response

### Security Incident Procedures

#### Incident Classification
```bash
# Severity Levels:
CRITICAL: System compromise, data breach, service unavailable
HIGH: Unauthorized access, malware detection, DoS attacks
MEDIUM: Failed intrusion attempts, policy violations
LOW: Suspicious activities, minor configuration issues
```

#### Response Team
```bash
# Incident Response Team Contacts:
Security Officer: security@ncuk.ac.uk
System Administrator: sysadmin@ncuk.ac.uk
Network Administrator: netadmin@ncuk.ac.uk
Management: management@ncuk.ac.uk
```

#### Response Procedures
```bash
# Immediate Actions (0-30 minutes):
1. Identify and isolate affected systems
2. Preserve evidence and logs
3. Notify incident response team
4. Begin containment procedures

# Short-term Actions (30 minutes - 4 hours):
1. Detailed impact assessment
2. Implement temporary workarounds
3. Notify stakeholders
4. Begin forensic analysis

# Recovery Actions (4+ hours):
1. System restoration from clean backups
2. Security patches and updates
3. Enhanced monitoring
4. Post-incident review
```

### Backup and Recovery

#### Secure Backup Strategy
```bash
# Encrypted backup configuration
#!/bin/bash
BACKUP_DIR="/secure/backups"
ENCRYPT_KEY="/etc/backup/backup.key"

# Create encrypted backup
tar -czf - /opt/wifi-capping | gpg --symmetric --cipher-algo AES256 --compress-algo 1 --compress-level 6 --output "$BACKUP_DIR/wifi-capping-$(date +%Y%m%d).tar.gz.gpg"

# Database backup with encryption
mysqldump wifi_capping | gpg --symmetric --cipher-algo AES256 --output "$BACKUP_DIR/database-$(date +%Y%m%d).sql.gpg"
```

## 📋 Compliance and Regulations

### GDPR Compliance

#### Data Protection Measures
```bash
# Personal data encryption
# Anonymization of logs older than 30 days
# Right to erasure implementation
# Data breach notification procedures (72 hours)
# Privacy by design principles
```

#### Data Retention Policy
```sql
-- Automated data retention
CREATE EVENT user_data_cleanup
ON SCHEDULE EVERY 1 DAY
DO
BEGIN
    -- Delete old sessions (30 days)
    DELETE FROM user_sessions WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
    
    -- Anonymize old logs (90 days)
    UPDATE audit_logs SET user_id = NULL, ip_address = 'anonymized' 
    WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
    
    -- Delete very old logs (2 years)
    DELETE FROM audit_logs WHERE timestamp < DATE_SUB(NOW(), INTERVAL 2 YEAR);
END;
```

### Industry Standards

#### ISO 27001 Alignment
```bash
# Information Security Management System (ISMS)
- Risk assessment and treatment
- Security policies and procedures
- Access control management
- Cryptography controls
- System security procedures
- Security monitoring and review
```

## 🔧 Security Configuration Checklist

### Pre-Deployment Security
- [ ] Strong password policies implemented
- [ ] Multi-factor authentication configured
- [ ] Database encryption enabled
- [ ] TLS 1.2/1.3 only for all connections
- [ ] Firewall rules configured and tested
- [ ] Security headers implemented
- [ ] Logging and monitoring configured
- [ ] Backup encryption verified
- [ ] Vulnerability scanning completed
- [ ] Security documentation reviewed

### Post-Deployment Security
- [ ] Security monitoring alerts tested
- [ ] Incident response procedures tested
- [ ] Access controls verified
- [ ] Backup and recovery tested
- [ ] Security training completed
- [ ] Compliance requirements met
- [ ] Regular security assessments scheduled

### Ongoing Security Maintenance
- [ ] Monthly security updates applied
- [ ] Quarterly vulnerability assessments
- [ ] Annual penetration testing
- [ ] Security awareness training
- [ ] Policy and procedure reviews
- [ ] Access permission audits
- [ ] Log analysis and review
- [ ] Backup integrity verification

## 🆘 Security Contacts

### Emergency Contacts
- **Security Incident Hotline**: +44-XXX-XXX-XXXX
- **Email**: security-incident@ncuk.ac.uk
- **24/7 Support**: support@ncuk.ac.uk

### Security Team
- **Chief Information Security Officer**: ciso@ncuk.ac.uk
- **Security Analyst**: security-analyst@ncuk.ac.uk
- **System Administrator**: sysadmin@ncuk.ac.uk

---

**Document Version**: 1.0  
**Last Updated**: August 2025  
**Next Review**: November 2025

**Classification**: Confidential - Internal Use Only