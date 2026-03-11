# Deployment Guide

This guide provides comprehensive instructions for deploying the WiFi Capping System in production environments.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04 LTS or newer (CentOS 8+, RHEL 8+ also supported)
- **CPU**: Minimum 2 cores, 4 cores recommended for high-traffic environments
- **RAM**: Minimum 4GB, 8GB recommended
- **Storage**: 50GB minimum, SSD recommended
- **Network**: Dedicated network interface for RADIUS traffic

### Required Software
- Node.js 16.x or newer
- npm 8.x or newer
- MySQL 8.0+ or PostgreSQL 13+
- FreeRADIUS 3.0.x
- Nginx (recommended for reverse proxy)
- UFW or iptables for firewall configuration

## 🏗️ Infrastructure Setup

### 1. Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget git build-essential

# Install Node.js (using NodeSource repository)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
node --version
npm --version
```

### 2. Database Setup

#### MySQL Installation and Configuration
```bash
# Install MySQL
sudo apt install -y mysql-server

# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
-- In MySQL console
CREATE DATABASE wifi_capping CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wifi_user'@'localhost' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON wifi_capping.* TO 'wifi_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### PostgreSQL Alternative
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
```

```sql
-- In PostgreSQL console
CREATE DATABASE wifi_capping;
CREATE USER wifi_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE wifi_capping TO wifi_user;
\q
```

### 3. FreeRADIUS Installation

```bash
# Install FreeRADIUS
sudo apt install -y freeradius freeradius-utils freeradius-mysql

# Stop FreeRADIUS for configuration
sudo systemctl stop freeradius
```

## 🚀 Application Deployment

### 1. Application Setup

```bash
# Create application user
sudo adduser --system --group --home /opt/wifi-capping wifi-app

# Clone repository
sudo git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git /opt/wifi-capping
sudo chown -R wifi-app:wifi-app /opt/wifi-capping

# Switch to application user
sudo -u wifi-app -i
cd /opt/wifi-capping

# Install dependencies
npm ci --only=production

# Create logs directory
mkdir -p logs
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (use your preferred editor)
nano .env
```

#### Production Environment Variables
```bash
# Application
NODE_ENV=production
APP_PORT=3000
APP_HOST=0.0.0.0
JWT_SECRET=your_very_secure_jwt_secret_here_minimum_32_characters
SESSION_SECRET=your_secure_session_secret_here

# Database Configuration
DB_TYPE=mysql  # or postgresql
DB_HOST=localhost
DB_PORT=3306   # 5432 for PostgreSQL
DB_NAME=wifi_capping
DB_USER=wifi_user
DB_PASS=secure_password_here
DB_SSL=false   # Set to true for SSL connections

# RADIUS Configuration
RADIUS_HOST=127.0.0.1
RADIUS_SECRET=your_radius_shared_secret
RADIUS_AUTH_PORT=1812
RADIUS_ACCT_PORT=1813
RADIUS_TIMEOUT=5000

# Bandwidth Settings
DEFAULT_BANDWIDTH_LIMIT=20GB
BANDWIDTH_CHECK_INTERVAL=300  # seconds
DISCONNECT_GRACE_PERIOD=60    # seconds

# Security Settings
BCRYPT_ROUNDS=12
LOGIN_ATTEMPTS_LIMIT=5
LOGIN_LOCKOUT_DURATION=1800  # seconds

# Logging
LOG_LEVEL=info
LOG_FILE_PATH=/opt/wifi-capping/logs/app.log
LOG_MAX_SIZE=10m
LOG_MAX_FILES=5

# Email Configuration (for notifications)
SMTP_HOST=smtp.your-domain.com
SMTP_PORT=587
SMTP_USER=notifications@your-domain.com
SMTP_PASS=email_password
SMTP_FROM=WiFi System <notifications@your-domain.com>
```

### 3. Database Migration

```bash
# Run database migrations
npm run db:migrate

# Seed initial data (optional)
npm run db:seed
```

### 4. FreeRADIUS Configuration

#### Configure Database Connection
```bash
# Edit SQL module configuration
sudo nano /etc/freeradius/3.0/mods-available/sql
```

```bash
# SQL module configuration
sql {
    driver = "rlm_sql_mysql"
    dialect = "mysql"
    
    server = "localhost"
    port = 3306
    login = "wifi_user"
    password = "secure_password_here"
    radius_db = "wifi_capping"
    
    acct_table1 = "radacct"
    acct_table2 = "radacct"
    postauth_table = "radpostauth"
    authcheck_table = "radcheck"
    groupcheck_table = "radgroupcheck"
    authreply_table = "radreply"
    groupreply_table = "radgroupreply"
    usergroup_table = "radusergroup"
    
    read_groups = yes
    delete_stale_sessions = yes
    pool {
        start = 5
        min = 4
        max = 32
        spare = 3
        uses = 0
        retry_delay = 30
        lifetime = 0
        idle_timeout = 60
    }
}
```

#### Configure Clients
```bash
# Edit clients configuration
sudo nano /etc/freeradius/3.0/clients.conf
```

```bash
# Add your network access servers
client nas_switch_1 {
    ipaddr = 192.168.1.10
    secret = your_nas_shared_secret
    require_message_authenticator = yes
    nastype = cisco
}

client nas_ap_subnet {
    ipaddr = 192.168.2.0/24
    secret = your_ap_shared_secret
    require_message_authenticator = yes
    nastype = other
}

# Localhost for testing
client localhost {
    ipaddr = 127.0.0.1
    secret = testing123
    require_message_authenticator = no
}
```

#### Enable SQL Module
```bash
# Enable SQL module
sudo ln -s /etc/freeradius/3.0/mods-available/sql /etc/freeradius/3.0/mods-enabled/

# Configure sites
sudo nano /etc/freeradius/3.0/sites-available/default
```

Add SQL to authorize and accounting sections:
```bash
# In authorize section
authorize {
    preprocess
    chap
    mschap
    digest
    suffix
    eap {
        ok = return
    }
    sql  # Add this line
    expiration
    logintime
    pap
}

# In accounting section
accounting {
    detail
    sql  # Add this line
    radutmp
    attr_filter.accounting_response
}
```

### 5. Systemd Service Configuration

```bash
# Create systemd service file
sudo nano /etc/systemd/system/wifi-capping.service
```

```ini
[Unit]
Description=WiFi Capping System
Documentation=https://github.com/georgeacquahjunior/Wifi_Capping_NCUK
After=network.target mysql.service freeradius.service

[Service]
Type=simple
User=wifi-app
Group=wifi-app
WorkingDirectory=/opt/wifi-capping
Environment=NODE_ENV=production
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=wifi-capping

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/wifi-capping/logs

[Install]
WantedBy=multi-user.target
```

### 6. Nginx Reverse Proxy Setup

```bash
# Install Nginx
sudo apt install -y nginx

# Create site configuration
sudo nano /etc/nginx/sites-available/wifi-capping
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # Proxy to Node.js application
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # Static files
    location /static {
        alias /opt/wifi-capping/public;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # API rate limiting
    location /api {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Rate limiting configuration
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=1r/s;
}
```

```bash
# Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/wifi-capping /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔐 Security Configuration

### 1. Firewall Setup

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (adjust port if needed)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow RADIUS traffic
sudo ufw allow 1812/udp
sudo ufw allow 1813/udp

# Allow from specific NAS devices only
sudo ufw allow from 192.168.1.0/24 to any port 1812
sudo ufw allow from 192.168.1.0/24 to any port 1813

# Enable firewall
sudo ufw enable
```

### 2. SSL Certificate Setup

#### Using Let's Encrypt
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Set up auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. File Permissions

```bash
# Set proper permissions
sudo chown -R wifi-app:wifi-app /opt/wifi-capping
sudo chmod 755 /opt/wifi-capping
sudo chmod 644 /opt/wifi-capping/.env
sudo chmod 600 /opt/wifi-capping/logs

# Create log rotation
sudo nano /etc/logrotate.d/wifi-capping
```

```bash
/opt/wifi-capping/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 wifi-app wifi-app
    postrotate
        systemctl reload wifi-capping
    endscript
}
```

## 🚀 Service Startup

### 1. Start Services

```bash
# Reload systemd and start services
sudo systemctl daemon-reload

# Enable and start database
sudo systemctl enable mysql  # or postgresql
sudo systemctl start mysql

# Enable and start FreeRADIUS
sudo systemctl enable freeradius
sudo systemctl start freeradius

# Enable and start application
sudo systemctl enable wifi-capping
sudo systemctl start wifi-capping

# Enable and start Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 2. Verify Deployment

```bash
# Check service status
sudo systemctl status mysql
sudo systemctl status freeradius
sudo systemctl status wifi-capping
sudo systemctl status nginx

# Check logs
sudo journalctl -u wifi-capping -f
sudo tail -f /var/log/freeradius/radius.log
sudo tail -f /opt/wifi-capping/logs/app.log

# Test application
curl -I http://localhost:3000/health
curl -I https://your-domain.com/health

# Test RADIUS
radtest testuser testpass localhost 1812 testing123
```

## 📊 Monitoring and Maintenance

### 1. Log Monitoring

```bash
# Set up log monitoring with rsyslog
sudo nano /etc/rsyslog.d/50-wifi-capping.conf
```

```bash
# WiFi Capping logs
:programname, isequal, "wifi-capping" /var/log/wifi-capping.log
& stop
```

### 2. Health Checks

Create monitoring script:
```bash
sudo nano /opt/wifi-capping/scripts/health-check.sh
```

```bash
#!/bin/bash
# Health check script

# Check services
systemctl is-active --quiet mysql || echo "MySQL is down"
systemctl is-active --quiet freeradius || echo "FreeRADIUS is down"
systemctl is-active --quiet wifi-capping || echo "WiFi Capping is down"
systemctl is-active --quiet nginx || echo "Nginx is down"

# Check application health
curl -f http://localhost:3000/health || echo "Application health check failed"

# Check database connectivity
mysql -u wifi_user -p"$DB_PASS" -e "SELECT 1" wifi_capping || echo "Database connection failed"

# Check RADIUS
radtest testuser testpass localhost 1812 testing123 || echo "RADIUS test failed"
```

### 3. Backup Strategy

```bash
# Create backup script
sudo nano /opt/wifi-capping/scripts/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/wifi-capping"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u wifi_user -p"$DB_PASS" wifi_capping > $BACKUP_DIR/database_$DATE.sql

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /opt/wifi-capping/.env /etc/freeradius/3.0/

# Backup logs (last 7 days)
find /opt/wifi-capping/logs -name "*.log" -mtime -7 -exec cp {} $BACKUP_DIR/ \;

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR"
```

```bash
# Schedule backup
sudo crontab -e
# Add: 0 2 * * * /opt/wifi-capping/scripts/backup.sh
```

## 🔄 Updates and Maintenance

### 1. Application Updates

```bash
# Update application
cd /opt/wifi-capping
sudo -u wifi-app git pull origin main
sudo -u wifi-app npm ci --only=production
sudo systemctl restart wifi-capping
```

### 2. Database Migrations

```bash
# Run database migrations
cd /opt/wifi-capping
sudo -u wifi-app npm run db:migrate
```

### 3. System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Node.js (if needed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Restart services after updates
sudo systemctl restart wifi-capping
```

## 🆘 Troubleshooting

### Common Issues

1. **Service won't start**: Check logs with `journalctl -u wifi-capping`
2. **Database connection failed**: Verify credentials and network connectivity
3. **RADIUS authentication failed**: Check shared secrets and client configuration
4. **High memory usage**: Monitor with `htop` and adjust Node.js memory limits
5. **SSL certificate issues**: Verify certificate validity and nginx configuration

### Performance Tuning

```bash
# Increase file descriptor limits
echo "wifi-app soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "wifi-app hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize database
sudo mysql_secure_installation
# Configure my.cnf for production workload

# Monitor performance
sudo apt install -y htop iotop nethogs
```

---

This deployment guide provides a comprehensive setup for production environments. Adjust configurations based on your specific infrastructure requirements and security policies.