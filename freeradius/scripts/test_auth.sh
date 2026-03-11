#!/bin/bash

#
# FreeRADIUS Test Script for NCUK WiFi Capping System
# This script tests authentication for all configured test users
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_failure() {
    echo -e "${RED}[FAILURE]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Test users array (username:password:description)
test_users=(
    "student1:password123:Student with 5GB limit"
    "student2:student2pass:Student with 2GB limit"
    "faculty1:faculty123:Faculty with 20GB limit"
    "guest1:guest2024:Guest with 500MB limit"
    "admin1:admin_ncuk_2024:Administrator account"
    "testuser:testpass:Test user with no limits"
)

# RADIUS server details
RADIUS_SERVER="localhost"
RADIUS_PORT="1812"
SHARED_SECRET="testing123"

print_info "Starting FreeRADIUS authentication tests..."
print_info "Server: $RADIUS_SERVER:$RADIUS_PORT"
echo

# Check if radtest is available
if ! command -v radtest &> /dev/null; then
    print_failure "radtest command not found. Please install freeradius-utils package."
    exit 1
fi

# Test each user
passed_tests=0
failed_tests=0
total_tests=${#test_users[@]}

for user_info in "${test_users[@]}"; do
    IFS=':' read -r username password description <<< "$user_info"
    
    print_info "Testing: $username ($description)"
    
    # Run radtest command
    if radtest "$username" "$password" "$RADIUS_SERVER" "$RADIUS_PORT" "$SHARED_SECRET" &>/dev/null; then
        print_success "Authentication successful for $username"
        ((passed_tests++))
    else
        print_failure "Authentication failed for $username"
        ((failed_tests++))
    fi
    
    echo
done

# Test invalid user
print_info "Testing invalid user (should fail)"
if radtest "invaliduser" "wrongpass" "$RADIUS_SERVER" "$RADIUS_PORT" "$SHARED_SECRET" &>/dev/null; then
    print_failure "Invalid user authentication should have failed but succeeded"
    ((failed_tests++))
else
    print_success "Invalid user correctly rejected"
    ((passed_tests++))
fi

echo
print_info "Test Summary:"
echo "============="
print_info "Total tests: $((total_tests + 1))"
print_success "Passed: $passed_tests"
print_failure "Failed: $failed_tests"

if [ $failed_tests -eq 0 ]; then
    echo
    print_success "All tests passed! FreeRADIUS is working correctly."
    exit 0
else
    echo
    print_failure "Some tests failed. Please check FreeRADIUS configuration and logs."
    print_info "Check logs with: sudo tail -f /var/log/freeradius/radius.log"
    exit 1
fi