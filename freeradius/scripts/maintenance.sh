#!/bin/bash

#
# FreeRADIUS Maintenance Script for NCUK WiFi System
# This script handles backup, log rotation, and maintenance tasks
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="/var/backups/freeradius"
CONFIG_DIR="/etc/freeradius/3.0"
LOG_DIR="/var/log/freeradius"
MAX_BACKUPS=7
MAX_LOG_DAYS=30

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

backup_configuration() {
    print_status "Creating configuration backup..."
    
    # Create backup directory
    sudo mkdir -p "$BACKUP_DIR"
    
    # Create timestamped backup
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/freeradius_config_$timestamp.tar.gz"
    
    sudo tar -czf "$backup_file" -C "$(dirname $CONFIG_DIR)" "$(basename $CONFIG_DIR)"
    
    print_status "Configuration backed up to: $backup_file"
    
    # Remove old backups
    local backup_count=$(sudo find "$BACKUP_DIR" -name "freeradius_config_*.tar.gz" | wc -l)
    if [ $backup_count -gt $MAX_BACKUPS ]; then
        print_status "Removing old backups (keeping $MAX_BACKUPS most recent)..."
        sudo find "$BACKUP_DIR" -name "freeradius_config_*.tar.gz" -type f | \
        sort | head -n -$MAX_BACKUPS | sudo xargs rm -f
    fi
}

rotate_logs() {
    print_status "Rotating log files..."
    
    # Compress old log files
    sudo find "$LOG_DIR" -name "*.log" -type f -mtime +1 -exec gzip {} \;
    
    # Remove old compressed logs
    sudo find "$LOG_DIR" -name "*.log.gz" -type f -mtime +$MAX_LOG_DAYS -delete
    
    # Clean up old accounting files
    if [ -d "$LOG_DIR/radacct" ]; then
        sudo find "$LOG_DIR/radacct" -name "detail-*" -type f -mtime +$MAX_LOG_DAYS -delete
    fi
    
    print_status "Log rotation completed"
}

cleanup_sessions() {
    print_status "Cleaning up stale sessions..."
    
    # Clean up radutmp file
    local radutmp_file="$LOG_DIR/radutmp"
    if [ -f "$radutmp_file" ]; then
        # Remove sessions older than 24 hours
        sudo find "$LOG_DIR" -name "radutmp*" -type f -mtime +1 -delete
    fi
    
    print_status "Session cleanup completed"
}

check_disk_space() {
    print_status "Checking disk space..."
    
    local log_usage=$(df "$LOG_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ $log_usage -gt 80 ]; then
        print_warning "Log directory is $log_usage% full"
        print_warning "Consider increasing log retention cleanup frequency"
    else
        print_status "Disk usage: $log_usage% (OK)"
    fi
}

update_statistics() {
    print_status "Updating usage statistics..."
    
    # Create statistics file
    local stats_file="$LOG_DIR/daily_stats.log"
    local today=$(date +%Y-%m-%d)
    
    # Count authentications for today
    local auth_requests=0
    local auth_accepts=0
    local auth_rejects=0
    
    if [ -f "$LOG_DIR/radius.log" ]; then
        auth_requests=$(grep "$today" "$LOG_DIR/radius.log" | grep -c "Access-Request" 2>/dev/null || echo "0")
        auth_accepts=$(grep "$today" "$LOG_DIR/radius.log" | grep -c "Access-Accept" 2>/dev/null || echo "0")
        auth_rejects=$(grep "$today" "$LOG_DIR/radius.log" | grep -c "Access-Reject" 2>/dev/null || echo "0")
    fi
    
    # Append to statistics file
    echo "$today,$auth_requests,$auth_accepts,$auth_rejects" | sudo tee -a "$stats_file" > /dev/null
    
    print_status "Statistics updated: $auth_requests requests, $auth_accepts accepts, $auth_rejects rejects"
}

optimize_database() {
    print_status "Optimizing user database..."
    
    # Check file permissions
    if [ -f "$CONFIG_DIR/users/users" ]; then
        sudo chmod 600 "$CONFIG_DIR/users/users"
        sudo chown freerad:freerad "$CONFIG_DIR/users/users"
    fi
    
    # Validate configuration
    if sudo freeradius -C > /dev/null 2>&1; then
        print_status "Configuration validation passed"
    else
        print_error "Configuration validation failed"
        return 1
    fi
}

restart_service() {
    print_status "Restarting FreeRADIUS service..."
    
    if sudo systemctl restart freeradius; then
        sleep 3
        if sudo systemctl is-active --quiet freeradius; then
            print_status "Service restarted successfully"
        else
            print_error "Service failed to start after restart"
            return 1
        fi
    else
        print_error "Failed to restart service"
        return 1
    fi
}

generate_report() {
    print_status "Generating maintenance report..."
    
    local report_file="/tmp/freeradius_maintenance_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
FreeRADIUS Maintenance Report
============================
Date: $(date)
Host: $(hostname)

Service Status:
$(systemctl status freeradius --no-pager -l)

Disk Usage:
$(df -h $LOG_DIR)

Active Sessions:
$(radwho 2>/dev/null | wc -l) active sessions

Recent Activity (last 24 hours):
$(grep "$(date -d yesterday +%Y-%m-%d)" $LOG_DIR/radius.log | wc -l 2>/dev/null || echo "0") log entries

Configuration Files:
$(find $CONFIG_DIR -name "*.conf" -o -name "users" | wc -l) configuration files

Backup Status:
$(ls -la $BACKUP_DIR/freeradius_config_*.tar.gz 2>/dev/null | tail -5 || echo "No backups found")

EOF

    echo "Report generated: $report_file"
    cat "$report_file"
}

show_help() {
    echo "FreeRADIUS Maintenance Script"
    echo
    echo "Usage: $0 [option]"
    echo
    echo "Options:"
    echo "  backup       Create configuration backup"
    echo "  rotate       Rotate and clean log files"
    echo "  cleanup      Clean up stale sessions"
    echo "  check        Check disk space and health"
    echo "  optimize     Optimize database and permissions"
    echo "  restart      Restart FreeRADIUS service"
    echo "  report       Generate maintenance report"
    echo "  all          Run all maintenance tasks"
    echo "  help         Show this help message"
    echo
    echo "Scheduled maintenance should run 'all' option daily"
}

# Main script
case "${1:-help}" in
    "backup")
        backup_configuration
        ;;
    "rotate")
        rotate_logs
        ;;
    "cleanup")
        cleanup_sessions
        ;;
    "check")
        check_disk_space
        ;;
    "optimize")
        optimize_database
        ;;
    "restart")
        restart_service
        ;;
    "report")
        generate_report
        ;;
    "all")
        print_status "Starting full maintenance routine..."
        backup_configuration
        rotate_logs
        cleanup_sessions
        update_statistics
        check_disk_space
        optimize_database
        restart_service
        generate_report
        print_status "Maintenance completed successfully"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac