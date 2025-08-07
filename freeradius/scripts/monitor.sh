#!/bin/bash

#
# FreeRADIUS Monitoring Script for NCUK WiFi System
# This script monitors FreeRADIUS service and provides usage statistics
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
RADIUS_LOG="/var/log/freeradius/radius.log"
ACCOUNTING_DIR="/var/log/freeradius/radacct"
SERVICE_NAME="freeradius"

print_header() {
    echo -e "${CYAN}================================${NC}"
    echo -e "${CYAN} NCUK WiFi RADIUS Monitor${NC}"
    echo -e "${CYAN}================================${NC}"
    echo
}

print_section() {
    echo -e "${BLUE}$1${NC}"
    echo "$(printf '%.0s-' {1..40})"
}

check_service_status() {
    print_section "Service Status"
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo -e "${GREEN}✓ FreeRADIUS service is running${NC}"
        
        # Get service uptime
        uptime=$(systemctl show $SERVICE_NAME --property=ActiveEnterTimestamp --value)
        echo -e "Started: $uptime"
        
        # Get memory usage
        memory=$(systemctl show $SERVICE_NAME --property=MemoryCurrent --value)
        if [ "$memory" != "[not set]" ] && [ -n "$memory" ]; then
            memory_mb=$((memory / 1024 / 1024))
            echo -e "Memory usage: ${memory_mb}MB"
        fi
        
    else
        echo -e "${RED}✗ FreeRADIUS service is not running${NC}"
    fi
    echo
}

check_ports() {
    print_section "Port Status"
    
    # Check authentication port
    if netstat -ulnp 2>/dev/null | grep -q ":1812 "; then
        echo -e "${GREEN}✓ Authentication port 1812 is listening${NC}"
    else
        echo -e "${RED}✗ Authentication port 1812 is not listening${NC}"
    fi
    
    # Check accounting port
    if netstat -ulnp 2>/dev/null | grep -q ":1813 "; then
        echo -e "${GREEN}✓ Accounting port 1813 is listening${NC}"
    else
        echo -e "${RED}✗ Accounting port 1813 is not listening${NC}"
    fi
    echo
}

show_recent_activity() {
    print_section "Recent Activity (Last 10 entries)"
    
    if [ -f "$RADIUS_LOG" ]; then
        tail -n 10 "$RADIUS_LOG" | while read -r line; do
            if echo "$line" | grep -q "Access-Accept"; then
                echo -e "${GREEN}$line${NC}"
            elif echo "$line" | grep -q "Access-Reject"; then
                echo -e "${RED}$line${NC}"
            elif echo "$line" | grep -q "Access-Request"; then
                echo -e "${YELLOW}$line${NC}"
            else
                echo "$line"
            fi
        done
    else
        echo -e "${YELLOW}Log file not found: $RADIUS_LOG${NC}"
    fi
    echo
}

show_authentication_stats() {
    print_section "Authentication Statistics (Last 100 entries)"
    
    if [ -f "$RADIUS_LOG" ]; then
        local total=$(tail -n 100 "$RADIUS_LOG" | grep -c "Access-Request" 2>/dev/null || echo "0")
        local accepted=$(tail -n 100 "$RADIUS_LOG" | grep -c "Access-Accept" 2>/dev/null || echo "0")
        local rejected=$(tail -n 100 "$RADIUS_LOG" | grep -c "Access-Reject" 2>/dev/null || echo "0")
        
        echo "Total requests: $total"
        echo -e "${GREEN}Accepted: $accepted${NC}"
        echo -e "${RED}Rejected: $rejected${NC}"
        
        if [ $total -gt 0 ]; then
            local success_rate=$((accepted * 100 / total))
            echo "Success rate: ${success_rate}%"
        fi
    else
        echo -e "${YELLOW}Log file not available${NC}"
    fi
    echo
}

show_active_sessions() {
    print_section "Active Sessions"
    
    local radutmp_file="/var/log/freeradius/radutmp"
    if [ -f "$radutmp_file" ]; then
        local session_count=$(radwho 2>/dev/null | wc -l)
        echo "Active sessions: $session_count"
        
        if [ $session_count -gt 0 ]; then
            echo
            echo "Current users:"
            radwho 2>/dev/null | head -10
        fi
    else
        echo -e "${YELLOW}Session tracking file not found${NC}"
    fi
    echo
}

show_top_users() {
    print_section "Top Users (Last 100 log entries)"
    
    if [ -f "$RADIUS_LOG" ]; then
        echo "Most active users:"
        tail -n 100 "$RADIUS_LOG" | grep "User-Name" | \
        sed -n 's/.*User-Name = "\([^"]*\)".*/\1/p' | \
        sort | uniq -c | sort -nr | head -5 | \
        while read count user; do
            echo "  $user: $count requests"
        done
    else
        echo -e "${YELLOW}Log file not available${NC}"
    fi
    echo
}

show_disk_usage() {
    print_section "Disk Usage"
    
    echo "Log directory usage:"
    if [ -d "/var/log/freeradius" ]; then
        du -sh /var/log/freeradius/* 2>/dev/null | sort -hr | head -5
    else
        echo -e "${YELLOW}Log directory not found${NC}"
    fi
    
    echo
    echo "Available disk space:"
    df -h /var/log/freeradius 2>/dev/null | tail -1 | awk '{print "  Used: " $3 " / Available: " $4 " (" $5 " used)"}'
    echo
}

tail_logs() {
    print_section "Live Log Monitoring"
    echo "Press Ctrl+C to stop monitoring..."
    echo
    
    if [ -f "$RADIUS_LOG" ]; then
        tail -f "$RADIUS_LOG" | while read -r line; do
            if echo "$line" | grep -q "Access-Accept"; then
                echo -e "${GREEN}$line${NC}"
            elif echo "$line" | grep -q "Access-Reject"; then
                echo -e "${RED}$line${NC}"
            elif echo "$line" | grep -q "Access-Request"; then
                echo -e "${YELLOW}$line${NC}"
            else
                echo "$line"
            fi
        done
    else
        echo -e "${RED}Log file not found: $RADIUS_LOG${NC}"
    fi
}

show_help() {
    echo "NCUK WiFi RADIUS Monitor"
    echo
    echo "Usage: $0 [option]"
    echo
    echo "Options:"
    echo "  status    Show service status and summary"
    echo "  stats     Show detailed statistics"
    echo "  sessions  Show active sessions"
    echo "  users     Show top users"
    echo "  logs      Show recent log entries"
    echo "  tail      Monitor logs in real-time"
    echo "  help      Show this help message"
    echo
    echo "Default (no options): Show complete status overview"
}

# Main script
case "${1:-status}" in
    "status")
        print_header
        check_service_status
        check_ports
        show_authentication_stats
        show_active_sessions
        ;;
    "stats")
        print_header
        show_authentication_stats
        show_top_users
        show_disk_usage
        ;;
    "sessions")
        print_header
        show_active_sessions
        ;;
    "users")
        print_header
        show_top_users
        ;;
    "logs")
        print_header
        show_recent_activity
        ;;
    "tail")
        print_header
        tail_logs
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_header
        check_service_status
        check_ports
        show_authentication_stats
        show_active_sessions
        ;;
esac