#!/bin/bash

# Test script for FreeRADIUS CoA configuration
# This script validates the FreeRADIUS configuration and tests basic functionality

echo "=== FreeRADIUS CoA Configuration Test Suite ==="
echo "Testing WiFi Capping NCUK configuration..."
echo ""

# Configuration directory
CONFIG_DIR="$(dirname "$0")"
TEST_RESULTS=()

# Function to log test results
log_test() {
    local test_name="$1"
    local result="$2"
    local message="$3"
    
    if [ "$result" = "PASS" ]; then
        echo "✓ $test_name: PASS"
    else
        echo "✗ $test_name: FAIL - $message"
    fi
    
    TEST_RESULTS+=("$test_name:$result:$message")
}

# Test 1: Check if all required configuration files exist
echo "Test 1: Configuration File Existence"
echo "------------------------------------"

required_files=(
    "radiusd.conf"
    "clients.conf"
    "proxy.conf"
    "users"
    "dictionary.ncuk"
    "sites-available/default"
    "sites-available/coa_disconnect"
    "policy.d/wifi_capping"
    "mods-enabled/modules.conf"
    "scripts/coa_disconnect.sh"
)

all_files_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$CONFIG_DIR/$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = true ]; then
    log_test "File Existence" "PASS" ""
else
    log_test "File Existence" "FAIL" "One or more required files missing"
fi

echo ""

# Test 2: Validate configuration syntax
echo "Test 2: Configuration Syntax Validation"
echo "---------------------------------------"

syntax_errors=""

# Check radiusd.conf syntax (basic checks)
if grep -A5 "listen {" "$CONFIG_DIR/radiusd.conf" | grep -q "type = coa"; then
    echo "  ✓ CoA listener configured"
else
    echo "  ✗ CoA listener not found"
    syntax_errors="${syntax_errors}CoA listener missing; "
fi

if grep -q "port.*3799" "$CONFIG_DIR/radiusd.conf"; then
    echo "  ✓ CoA port 3799 configured"
else
    echo "  ✗ CoA port 3799 not configured"
    syntax_errors="${syntax_errors}CoA port not configured; "
fi

# Check clients.conf
if grep -q "coa_server" "$CONFIG_DIR/clients.conf"; then
    echo "  ✓ CoA server configuration found"
else
    echo "  ✗ CoA server configuration missing"
    syntax_errors="${syntax_errors}CoA server config missing; "
fi

# Check if sites are properly configured
if grep -q "recv-coa" "$CONFIG_DIR/sites-available/coa_disconnect"; then
    echo "  ✓ CoA disconnect server configured"
else
    echo "  ✗ CoA disconnect server not configured"
    syntax_errors="${syntax_errors}CoA disconnect server missing; "
fi

if [ -z "$syntax_errors" ]; then
    log_test "Configuration Syntax" "PASS" ""
else
    log_test "Configuration Syntax" "FAIL" "$syntax_errors"
fi

echo ""

# Test 3: Check user definitions
echo "Test 3: User Configuration Validation"
echo "-------------------------------------"

user_errors=""
test_users=("testuser" "student" "ncuk_staff" "guest" "admin")

for user in "${test_users[@]}"; do
    if grep -q "^$user" "$CONFIG_DIR/users"; then
        echo "  ✓ User '$user' defined"
        
        # Check if user has required attributes
        user_line=$(grep -A3 "^$user" "$CONFIG_DIR/users")
        if echo "$user_line" | grep -q "Filter-Id"; then
            echo "    ✓ Has bandwidth filter"
        else
            echo "    ✗ Missing bandwidth filter"
            user_errors="${user_errors}$user missing filter; "
        fi
        
        if echo "$user_line" | grep -q "Session-Timeout"; then
            echo "    ✓ Has session timeout"
        else
            echo "    ✗ Missing session timeout"
            user_errors="${user_errors}$user missing timeout; "
        fi
    else
        echo "  ✗ User '$user' not found"
        user_errors="${user_errors}$user not defined; "
    fi
done

if [ -z "$user_errors" ]; then
    log_test "User Configuration" "PASS" ""
else
    log_test "User Configuration" "FAIL" "$user_errors"
fi

echo ""

# Test 4: Validate CoA disconnect script
echo "Test 4: CoA Disconnect Script Validation"
echo "----------------------------------------"

script_errors=""

if [ -x "$CONFIG_DIR/scripts/coa_disconnect.sh" ]; then
    echo "  ✓ CoA disconnect script is executable"
    
    # Test script help function
    if "$CONFIG_DIR/scripts/coa_disconnect.sh" -h >/dev/null 2>&1; then
        echo "  ✓ Script help function works"
    else
        echo "  ✗ Script help function failed"
        script_errors="${script_errors}Help function broken; "
    fi
    
    # Check for required dependencies (without actually running)
    if grep -q "radclient" "$CONFIG_DIR/scripts/coa_disconnect.sh"; then
        echo "  ✓ Script uses radclient command"
    else
        echo "  ✗ Script missing radclient dependency"
        script_errors="${script_errors}Missing radclient; "
    fi
    
else
    echo "  ✗ CoA disconnect script not executable"
    script_errors="${script_errors}Script not executable; "
fi

if [ -z "$script_errors" ]; then
    log_test "CoA Script Validation" "PASS" ""
else
    log_test "CoA Script Validation" "FAIL" "$script_errors"
fi

echo ""

# Test 5: Check dictionary definitions
echo "Test 5: Custom Dictionary Validation"
echo "------------------------------------"

dict_errors=""

if grep -q "VENDOR.*NCUK-WiFi" "$CONFIG_DIR/dictionary.ncuk"; then
    echo "  ✓ NCUK-WiFi vendor defined"
else
    echo "  ✗ NCUK-WiFi vendor not defined"
    dict_errors="${dict_errors}Vendor missing; "
fi

if grep -q "ATTRIBUTE.*NCUK-Bandwidth" "$CONFIG_DIR/dictionary.ncuk"; then
    echo "  ✓ Bandwidth attributes defined"
else
    echo "  ✗ Bandwidth attributes missing"
    dict_errors="${dict_errors}Bandwidth attrs missing; "
fi

if grep -q "Error-Cause" "$CONFIG_DIR/dictionary.ncuk"; then
    echo "  ✓ CoA error codes defined"
else
    echo "  ✗ CoA error codes missing"
    dict_errors="${dict_errors}Error codes missing; "
fi

if [ -z "$dict_errors" ]; then
    log_test "Dictionary Validation" "PASS" ""
else
    log_test "Dictionary Validation" "FAIL" "$dict_errors"
fi

echo ""

# Test 6: Policy validation
echo "Test 6: WiFi Capping Policy Validation"
echo "--------------------------------------"

policy_errors=""

if grep -q "bandwidth_policy" "$CONFIG_DIR/policy.d/wifi_capping"; then
    echo "  ✓ Bandwidth policy defined"
else
    echo "  ✗ Bandwidth policy missing"
    policy_errors="${policy_errors}Bandwidth policy missing; "
fi

if grep -q "data_usage_policy" "$CONFIG_DIR/policy.d/wifi_capping"; then
    echo "  ✓ Data usage policy defined"
else
    echo "  ✗ Data usage policy missing"
    policy_errors="${policy_errors}Data usage policy missing; "
fi

if grep -q "coa_disconnect_trigger" "$CONFIG_DIR/policy.d/wifi_capping"; then
    echo "  ✓ CoA disconnect policy defined"
else
    echo "  ✗ CoA disconnect policy missing"
    policy_errors="${policy_errors}CoA disconnect policy missing; "
fi

if [ -z "$policy_errors" ]; then
    log_test "Policy Validation" "PASS" ""
else
    log_test "Policy Validation" "FAIL" "$policy_errors"
fi

echo ""

# Test 7: Check for FreeRADIUS installation (optional)
echo "Test 7: FreeRADIUS Installation Check (Optional)"
echo "------------------------------------------------"

if command -v radiusd >/dev/null 2>&1; then
    echo "  ✓ FreeRADIUS server installed"
    radiusd_version=$(radiusd -v 2>&1 | head -1)
    echo "    Version: $radiusd_version"
else
    echo "  ! FreeRADIUS server not installed (optional for config validation)"
fi

if command -v radclient >/dev/null 2>&1; then
    echo "  ✓ FreeRADIUS client tools installed"
else
    echo "  ! FreeRADIUS client tools not installed (required for testing)"
fi

log_test "FreeRADIUS Installation" "PASS" "Installation check completed"

echo ""

# Summary
echo "=== Test Summary ==="
echo "===================="

total_tests=0
passed_tests=0

for result in "${TEST_RESULTS[@]}"; do
    IFS=':' read -r test_name test_result test_message <<< "$result"
    total_tests=$((total_tests + 1))
    if [ "$test_result" = "PASS" ]; then
        passed_tests=$((passed_tests + 1))
    fi
done

echo "Total tests: $total_tests"
echo "Passed: $passed_tests"
echo "Failed: $((total_tests - passed_tests))"

if [ $passed_tests -eq $total_tests ]; then
    echo ""
    echo "🎉 All tests passed! Configuration appears to be valid."
    echo ""
    echo "Next steps:"
    echo "1. Copy configuration files to FreeRADIUS directory"
    echo "2. Test with 'sudo radiusd -X' for syntax validation"
    echo "3. Test authentication and CoA functionality"
    exit 0
else
    echo ""
    echo "⚠️  Some tests failed. Please review the configuration."
    echo ""
    echo "Failed tests:"
    for result in "${TEST_RESULTS[@]}"; do
        IFS=':' read -r test_name test_result test_message <<< "$result"
        if [ "$test_result" = "FAIL" ]; then
            echo "  - $test_name: $test_message"
        fi
    done
    exit 1
fi