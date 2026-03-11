#!/bin/bash

# CoA disconnect script for WiFi capping
# This script sends CoA Disconnect-Request packets to terminate user sessions

# Configuration
RADIUS_SECRET="testing123"
NAS_IP="127.0.0.1"
COA_PORT="3799"
RADIUS_CLIENT="radclient"

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Send CoA Disconnect-Request to terminate user sessions"
    echo ""
    echo "Options:"
    echo "  -u, --username USERNAME    Username to disconnect"
    echo "  -s, --session-id ID        Session ID to disconnect" 
    echo "  -n, --nas-ip IP           NAS IP address (default: $NAS_IP)"
    echo "  -p, --port PORT           CoA port (default: $COA_PORT)"
    echo "  -S, --secret SECRET       RADIUS shared secret (default: $RADIUS_SECRET)"
    echo "  -r, --reason REASON       Disconnect reason"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -u testuser -r \"Data limit exceeded\""
    echo "  $0 -s 12345 -u testuser -n 192.168.1.10"
    echo "  $0 -u student -r \"Session timeout\""
}

# Function to send CoA disconnect
send_coa_disconnect() {
    local username="$1"
    local session_id="$2" 
    local nas_ip="$3"
    local reason="$4"
    
    # Create temporary file for CoA packet
    local coa_file=$(mktemp)
    
    # Build CoA packet attributes
    echo "Packet-Type = Disconnect-Request" > "$coa_file"
    
    if [ -n "$username" ]; then
        echo "User-Name = \"$username\"" >> "$coa_file"
    fi
    
    if [ -n "$session_id" ]; then
        echo "Acct-Session-Id = \"$session_id\"" >> "$coa_file"
    fi
    
    if [ -n "$nas_ip" ]; then
        echo "NAS-IP-Address = $nas_ip" >> "$coa_file"
    fi
    
    if [ -n "$reason" ]; then
        echo "Reply-Message = \"$reason\"" >> "$coa_file"
    fi
    
    # Add Event-Timestamp
    echo "Event-Timestamp = $(date +%s)" >> "$coa_file"
    
    echo "Sending CoA Disconnect-Request..."
    echo "Target: ${NAS_IP}:${COA_PORT}"
    echo "Username: ${username:-'Not specified'}"
    echo "Session-ID: ${session_id:-'Not specified'}"
    echo "Reason: ${reason:-'Administrative disconnect'}"
    echo ""
    
    # Send the CoA packet
    if command -v $RADIUS_CLIENT >/dev/null 2>&1; then
        echo "CoA packet contents:"
        cat "$coa_file"
        echo ""
        
        $RADIUS_CLIENT -x "$NAS_IP:$COA_PORT" coa "$RADIUS_SECRET" < "$coa_file"
        local result=$?
        
        if [ $result -eq 0 ]; then
            echo "CoA Disconnect-Request sent successfully"
        else
            echo "Failed to send CoA Disconnect-Request (exit code: $result)"
        fi
    else
        echo "Error: radclient not found. Please install FreeRADIUS client tools."
        echo "CoA packet that would be sent:"
        cat "$coa_file"
        local result=1
    fi
    
    # Clean up
    rm -f "$coa_file"
    
    return $result
}

# Function to test CoA connectivity
test_coa() {
    echo "Testing CoA connectivity to ${NAS_IP}:${COA_PORT}..."
    
    local test_file=$(mktemp)
    echo "Packet-Type = Status-Server" > "$test_file"
    echo "Message-Authenticator = 0x00" >> "$test_file"
    
    if command -v $RADIUS_CLIENT >/dev/null 2>&1; then
        $RADIUS_CLIENT -x "$NAS_IP:$COA_PORT" status "$RADIUS_SECRET" < "$test_file"
        local result=$?
        
        if [ $result -eq 0 ]; then
            echo "CoA server is reachable"
        else
            echo "CoA server is not reachable or not responding"
        fi
    else
        echo "Error: radclient not found"
        result=1
    fi
    
    rm -f "$test_file"
    return $result
}

# Parse command line arguments
USERNAME=""
SESSION_ID=""
DISCONNECT_REASON=""
TEST_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--username)
            USERNAME="$2"
            shift 2
            ;;
        -s|--session-id)
            SESSION_ID="$2"
            shift 2
            ;;
        -n|--nas-ip)
            NAS_IP="$2"
            shift 2
            ;;
        -p|--port)
            COA_PORT="$2"
            shift 2
            ;;
        -S|--secret)
            RADIUS_SECRET="$2"
            shift 2
            ;;
        -r|--reason)
            DISCONNECT_REASON="$2"
            shift 2
            ;;
        -t|--test)
            TEST_MODE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main execution
if [ "$TEST_MODE" = true ]; then
    test_coa
    exit $?
fi

# Validate required parameters
if [ -z "$USERNAME" ] && [ -z "$SESSION_ID" ]; then
    echo "Error: Either username (-u) or session-id (-s) must be specified"
    usage
    exit 1
fi

# Send CoA disconnect
send_coa_disconnect "$USERNAME" "$SESSION_ID" "$NAS_IP" "$DISCONNECT_REASON"
exit $?