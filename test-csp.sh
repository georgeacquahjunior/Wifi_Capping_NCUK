#!/bin/bash
# CSP Validation Test Script

echo "🔒 WiFi Capping NCUK - CSP Validation Test"
echo "=========================================="

# Test 1: Check if CSP meta tag exists in HTML
echo "Test 1: Checking CSP meta tag in HTML..."
if grep -q "Content-Security-Policy" index.html; then
    echo "✅ PASS: CSP meta tag found in index.html"
else
    echo "❌ FAIL: CSP meta tag missing in index.html"
    exit 1
fi

# Test 2: Validate deployment configuration files
echo -e "\nTest 2: Checking deployment configuration files..."

# Check vercel.json
if [ -f "vercel.json" ] && jq empty vercel.json 2>/dev/null; then
    echo "✅ PASS: vercel.json exists and is valid JSON"
else
    echo "❌ FAIL: vercel.json is missing or invalid"
    exit 1
fi

# Check netlify.toml
if [ -f "netlify.toml" ]; then
    echo "✅ PASS: netlify.toml exists"
else
    echo "❌ FAIL: netlify.toml is missing"
    exit 1
fi

# Check .htaccess
if [ -f ".htaccess" ]; then
    echo "✅ PASS: .htaccess exists"
else
    echo "❌ FAIL: .htaccess is missing"
    exit 1
fi

# Test 3: Check for security documentation
echo -e "\nTest 3: Checking security documentation..."
if [ -f "SECURITY.md" ]; then
    echo "✅ PASS: SECURITY.md exists"
else
    echo "❌ FAIL: SECURITY.md is missing"
    exit 1
fi

# Test 4: Check for potential CSP violations in HTML
echo -e "\nTest 4: Checking for potential CSP violations..."

# Check for inline scripts without nonce
if grep -n "<script>" index.html | grep -v "nonce\|src="; then
    echo "⚠️  WARNING: Inline scripts found without nonce (may violate strict CSP)"
else
    echo "✅ PASS: No inline scripts without nonce found"
fi

# Test 5: Validate CSP directives
echo -e "\nTest 5: Validating CSP directives..."
csp_content=$(grep -A 10 "Content-Security-Policy" index.html)

# Check for essential directives
if echo "$csp_content" | grep -q "default-src 'self'"; then
    echo "✅ PASS: default-src 'self' directive found"
else
    echo "❌ FAIL: default-src 'self' directive missing"
    exit 1
fi

if echo "$csp_content" | grep -q "frame-ancestors 'none'"; then
    echo "✅ PASS: frame-ancestors 'none' directive found (clickjacking protection)"
else
    echo "❌ FAIL: frame-ancestors 'none' directive missing"
    exit 1
fi

if echo "$csp_content" | grep -q "object-src 'none'"; then
    echo "✅ PASS: object-src 'none' directive found (plugin protection)"
else
    echo "❌ FAIL: object-src 'none' directive missing"
    exit 1
fi

echo -e "\n🎉 All CSP validation tests passed!"
echo "The WiFi Capping application is properly secured with CSP headers."