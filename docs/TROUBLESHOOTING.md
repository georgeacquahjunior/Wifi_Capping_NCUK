# Troubleshooting Guide

This guide helps diagnose and resolve common issues with the WiFi Capping System.

## 🚨 Common Issues

### Authentication Problems

#### Issue: Users Cannot Connect to WiFi
**Symptoms:**
- Authentication failures in RADIUS logs
- Users receive "network authentication required" messages
- Connection attempts timeout

**Diagnosis:**
```bash
# Check RADIUS server status
sudo systemctl status freeradius

# Test RADIUS authentication
radtest username password radius-server 1812 shared-secret

# Check RADIUS logs
sudo tail -f /var/log/freeradius/radius.log

# Verify database connectivity
mysql -u wifi_user -p wifi_capping -e "SELECT COUNT(*) FROM users WHERE status='active'"
```

**Solutions:**
1. **Invalid Credentials:**
   ```bash
   # Reset user password
   npm run user:reset-password username
   
   # Check user status
   mysql -u wifi_user -p -e "SELECT username, status FROM users WHERE username='problematic_user'"
   ```

2. **RADIUS Configuration:**
   ```bash
   # Verify shared secret
   sudo grep -A 5 "client nas" /etc/freeradius/3.0/clients.conf
   
   # Test RADIUS debug mode
   sudo freeradius -X
   ```

3. **Database Issues:**
   ```bash
   # Check database connection
   npm run db:test
   
   # Verify RADIUS database tables
   mysql -u wifi_user -p wifi_capping -e "SHOW TABLES LIKE 'rad%'"
   ```

#### Issue: Authentication Succeeds but No Internet Access
**Symptoms:**
- RADIUS shows Access-Accept
- User connects to WiFi but cannot browse
- Network connectivity tests fail

**Diagnosis:**
```bash
# Check user's current usage
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/v1/usage/users/123"

# Verify firewall rules
sudo iptables -L -n

# Check NAS configuration
ping nas-ip-address
```

**Solutions:**
1. **Bandwidth Limit Exceeded:**
   ```bash
   # Check user usage
   npm run usage:check username
   
   # Reset usage if needed
   npm run usage:reset username --reason "technical_issue"
   ```

2. **Network Configuration:**
   ```bash
   # Verify routing
   sudo route -n
   
   # Check DNS resolution
   nslookup google.com
   ```

### Performance Issues

#### Issue: Slow Response Times
**Symptoms:**
- API requests take longer than 5 seconds
- Dashboard loads slowly
- User complaints about lag

**Diagnosis:**
```bash
# Check system resources
htop
free -h
df -h

# Monitor database performance
mysql -u wifi_user -p -e "SHOW PROCESSLIST"

# Check application logs
tail -f /opt/wifi-capping/logs/app.log | grep "slow"

# Network latency test
ping -c 10 database-server
```

**Solutions:**
1. **High CPU Usage:**
   ```bash
   # Identify CPU-intensive processes
   top -o %CPU
   
   # Restart application if needed
   sudo systemctl restart wifi-capping
   ```

2. **Memory Issues:**
   ```bash
   # Check memory usage
   cat /proc/meminfo
   
   # Clear cache if needed
   sudo sync && sudo echo 3 > /proc/sys/vm/drop_caches
   ```

3. **Database Performance:**
   ```sql
   -- Check slow queries
   SHOW VARIABLES LIKE 'slow_query_log';
   SET GLOBAL slow_query_log = 'ON';
   SET GLOBAL long_query_time = 2;
   
   -- Optimize tables
   OPTIMIZE TABLE users, user_usage, active_sessions;
   
   -- Check indexes
   SHOW INDEX FROM users;
   ```

#### Issue: High Memory Usage
**Symptoms:**
- System running out of memory
- Application crashes with OOM errors
- Swap usage increasing

**Diagnosis:**
```bash
# Check memory usage by process
ps aux --sort=-%mem | head

# Monitor memory over time
watch -n 5 'free -h'

# Check for memory leaks
sudo pmap -d $(pgrep node)
```

**Solutions:**
1. **Node.js Memory Limit:**
   ```bash
   # Increase Node.js heap size
   export NODE_OPTIONS="--max-old-space-size=4096"
   
   # Update systemd service
   sudo systemctl edit wifi-capping
   ```
   Add:
   ```ini
   [Service]
   Environment=NODE_OPTIONS=--max-old-space-size=4096
   ```

2. **Database Connection Pool:**
   ```javascript
   // Adjust connection pool settings
   const sequelize = new Sequelize(database, username, password, {
     pool: {
       max: 10,      // Reduce from default
       min: 1,
       idle: 10000,
       acquire: 60000
     }
   });
   ```

### Database Issues

#### Issue: Database Connection Failures
**Symptoms:**
- "Cannot connect to database" errors
- Application startup failures
- Intermittent connection drops

**Diagnosis:**
```bash
# Test database connectivity
mysql -h localhost -u wifi_user -p wifi_capping

# Check database server status
sudo systemctl status mysql

# Monitor database connections
mysql -u root -p -e "SHOW PROCESSLIST"

# Check database logs
sudo tail -f /var/log/mysql/error.log
```

**Solutions:**
1. **Connection Limits:**
   ```sql
   -- Check current connections
   SHOW STATUS LIKE 'Threads_connected';
   SHOW VARIABLES LIKE 'max_connections';
   
   -- Increase connection limit
   SET GLOBAL max_connections = 200;
   ```

2. **Authentication Issues:**
   ```sql
   -- Verify user permissions
   SHOW GRANTS FOR 'wifi_user'@'localhost';
   
   -- Reset user password
   ALTER USER 'wifi_user'@'localhost' IDENTIFIED BY 'new_password';
   FLUSH PRIVILEGES;
   ```

#### Issue: Database Performance Degradation
**Symptoms:**
- Slow query execution
- High database CPU usage
- Timeouts on complex queries

**Diagnosis:**
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

-- Check table sizes
SELECT 
    table_name AS 'Table',
    round(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'wifi_capping'
ORDER BY (data_length + index_length) DESC;

-- Analyze query performance
EXPLAIN SELECT * FROM users WHERE username = 'test';
```

**Solutions:**
1. **Index Optimization:**
   ```sql
   -- Add missing indexes
   CREATE INDEX idx_users_status_role ON users(status, role);
   CREATE INDEX idx_usage_user_date ON user_usage(user_id, date);
   
   -- Remove unused indexes
   DROP INDEX unused_index_name ON table_name;
   ```

2. **Query Optimization:**
   ```sql
   -- Optimize pagination queries
   SELECT * FROM users 
   WHERE id > last_seen_id 
   ORDER BY id 
   LIMIT 20;
   
   -- Use covering indexes
   CREATE INDEX idx_users_covering ON users(status, username, email, created_at);
   ```

### Network Issues

#### Issue: RADIUS Server Not Responding
**Symptoms:**
- NAS cannot reach RADIUS server
- Authentication requests timeout
- RADIUS logs show no incoming requests

**Diagnosis:**
```bash
# Test RADIUS port connectivity
sudo netstat -ulpn | grep :1812
sudo netstat -ulpn | grep :1813

# Test from NAS device
radtest username password radius-server 1812 shared-secret

# Check firewall rules
sudo iptables -L -n | grep 1812
sudo ufw status numbered
```

**Solutions:**
1. **Firewall Configuration:**
   ```bash
   # Open RADIUS ports
   sudo ufw allow 1812/udp
   sudo ufw allow 1813/udp
   
   # Allow specific NAS devices
   sudo ufw allow from 192.168.1.0/24 to any port 1812
   ```

2. **RADIUS Service:**
   ```bash
   # Restart RADIUS service
   sudo systemctl restart freeradius
   
   # Check configuration
   sudo freeradius -CX
   ```

#### Issue: NAS Communication Problems
**Symptoms:**
- Inconsistent authentication results
- Accounting data not received
- Users randomly disconnected

**Diagnosis:**
```bash
# Check NAS configuration
ssh admin@nas-device
show radius-server status

# Verify shared secrets match
sudo grep -A 5 "client nas" /etc/freeradius/3.0/clients.conf

# Monitor RADIUS traffic
sudo tcpdump -i eth0 port 1812 or port 1813
```

**Solutions:**
1. **Shared Secret Mismatch:**
   ```bash
   # Update RADIUS client configuration
   sudo nano /etc/freeradius/3.0/clients.conf
   
   # Restart RADIUS after changes
   sudo systemctl restart freeradius
   ```

2. **Network Connectivity:**
   ```bash
   # Test connectivity to NAS
   ping nas-ip-address
   traceroute nas-ip-address
   
   # Check for packet loss
   mtr -c 100 nas-ip-address
   ```

## 🔧 Diagnostic Tools

### Log Analysis Scripts

#### Application Log Parser
```bash
#!/bin/bash
# analyze-logs.sh

LOG_FILE="/opt/wifi-capping/logs/app.log"
TIMEFRAME="1h"

echo "=== Error Analysis (Last $TIMEFRAME) ==="
grep -E "(ERROR|CRITICAL)" "$LOG_FILE" | \
  grep "$(date -d "1 hour ago" '+%Y-%m-%d %H')" | \
  awk '{print $4}' | sort | uniq -c | sort -rn

echo "=== Top API Endpoints (Last $TIMEFRAME) ==="
grep "API Request" "$LOG_FILE" | \
  grep "$(date -d "1 hour ago" '+%Y-%m-%d %H')" | \
  awk '{print $6}' | sort | uniq -c | sort -rn | head -10

echo "=== Failed Authentication Attempts ==="
grep "Authentication failed" "$LOG_FILE" | \
  tail -20
```

#### Database Health Check
```bash
#!/bin/bash
# db-health-check.sh

echo "=== Database Connection Test ==="
mysql -u wifi_user -p"$DB_PASS" wifi_capping -e "SELECT 1 as test" 2>/dev/null && echo "✓ Database connection OK" || echo "✗ Database connection failed"

echo "=== Table Row Counts ==="
mysql -u wifi_user -p"$DB_PASS" wifi_capping -e "
SELECT 
    table_name,
    table_rows
FROM information_schema.tables 
WHERE table_schema = 'wifi_capping'
ORDER BY table_rows DESC;"

echo "=== Active Sessions Count ==="
mysql -u wifi_user -p"$DB_PASS" wifi_capping -e "
SELECT COUNT(*) as active_sessions 
FROM active_sessions 
WHERE last_update > DATE_SUB(NOW(), INTERVAL 30 MINUTE);"
```

#### System Resource Monitor
```bash
#!/bin/bash
# system-monitor.sh

echo "=== System Resources ==="
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')"
echo "Memory Usage: $(free | grep Mem | awk '{printf "%.1f%%", ($3/$2) * 100.0}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{print $5}')"

echo "=== Network Connections ==="
echo "Total connections: $(netstat -an | wc -l)"
echo "ESTABLISHED: $(netstat -an | grep ESTABLISHED | wc -l)"
echo "TIME_WAIT: $(netstat -an | grep TIME_WAIT | wc -l)"

echo "=== Application Processes ==="
ps aux | grep -E "(node|mysql|freeradius)" | grep -v grep
```

### Performance Testing

#### Load Testing Script
```bash
#!/bin/bash
# load-test.sh

BASE_URL="http://localhost:3000"
CONCURRENT_USERS=10
DURATION=60

echo "=== Running Load Test ==="
echo "URL: $BASE_URL"
echo "Concurrent Users: $CONCURRENT_USERS"
echo "Duration: ${DURATION}s"

# Install apache bench if not available
which ab > /dev/null || sudo apt install apache2-utils

# Test login endpoint
ab -n 1000 -c "$CONCURRENT_USERS" -T 'application/json' \
   -p login-data.json "$BASE_URL/api/v1/auth/login"

# Test users endpoint (requires auth token)
TOKEN=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | \
  jq -r '.data.token')

ab -n 500 -c "$CONCURRENT_USERS" \
   -H "Authorization: Bearer $TOKEN" \
   "$BASE_URL/api/v1/users"
```

## 📞 Getting Help

### Log Locations
- **Application Logs:** `/opt/wifi-capping/logs/`
- **RADIUS Logs:** `/var/log/freeradius/`
- **System Logs:** `/var/log/syslog`
- **Database Logs:** `/var/log/mysql/`
- **Nginx Logs:** `/var/log/nginx/`

### Configuration Files
- **Application Config:** `/opt/wifi-capping/.env`
- **RADIUS Config:** `/etc/freeradius/3.0/`
- **Nginx Config:** `/etc/nginx/sites-available/wifi-capping`
- **Database Config:** `/etc/mysql/mysql.conf.d/`

### Emergency Contacts
- **Technical Support:** support@ncuk.ac.uk
- **Security Issues:** security@ncuk.ac.uk
- **24/7 Hotline:** +44-XXX-XXX-XXXX

### Useful Commands
```bash
# Service management
sudo systemctl status wifi-capping
sudo systemctl restart wifi-capping
sudo systemctl stop wifi-capping

# Log monitoring
sudo journalctl -u wifi-capping -f
tail -f /opt/wifi-capping/logs/app.log

# Database access
mysql -u wifi_user -p wifi_capping

# System monitoring
htop
iotop
nethogs
```

---

If issues persist after following this guide, please collect relevant log files and contact technical support with detailed information about the problem, including timestamps and specific error messages.