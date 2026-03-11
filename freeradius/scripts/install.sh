#!/bin/bash

#
# FreeRADIUS Installation Script for NCUK WiFi Capping System
# This script installs and configures FreeRADIUS on Ubuntu/Debian systems
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

print_status "Starting FreeRADIUS installation for NCUK WiFi Capping System..."

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install FreeRADIUS
print_status "Installing FreeRADIUS..."
sudo apt install -y freeradius freeradius-utils freeradius-common

# Install additional dependencies
print_status "Installing additional dependencies..."
sudo apt install -y openssl ssl-cert

# Create backup of original configuration
print_status "Backing up original FreeRADIUS configuration..."
sudo cp -r /etc/freeradius/3.0 /etc/freeradius/3.0.backup.$(date +%Y%m%d_%H%M%S)

# Copy our configuration files
print_status "Installing NCUK FreeRADIUS configuration..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONFIG_DIR="$SCRIPT_DIR/../config"
USERS_DIR="$SCRIPT_DIR/../users"

# Copy main configuration
sudo cp "$CONFIG_DIR/radiusd.conf" /etc/freeradius/3.0/
sudo cp "$CONFIG_DIR/clients.conf" /etc/freeradius/3.0/

# Copy users file
sudo mkdir -p /etc/freeradius/3.0/users
sudo cp "$USERS_DIR/users" /etc/freeradius/3.0/users/

# Copy sites
sudo cp "$CONFIG_DIR/sites-available/ncuk_wifi" /etc/freeradius/3.0/sites-available/
sudo ln -sf /etc/freeradius/3.0/sites-available/ncuk_wifi /etc/freeradius/3.0/sites-enabled/

# Copy modules
sudo cp "$CONFIG_DIR/mods-available/"* /etc/freeradius/3.0/mods-available/
sudo ln -sf /etc/freeradius/3.0/mods-available/files /etc/freeradius/3.0/mods-enabled/
sudo ln -sf /etc/freeradius/3.0/mods-available/pap /etc/freeradius/3.0/mods-enabled/
sudo ln -sf /etc/freeradius/3.0/mods-available/detail /etc/freeradius/3.0/mods-enabled/

# Copy policies
sudo cp "$CONFIG_DIR/policy.d/"* /etc/freeradius/3.0/policy.d/

# Set proper permissions
print_status "Setting proper file permissions..."
sudo chown -R freerad:freerad /etc/freeradius/3.0/
sudo chmod -R 640 /etc/freeradius/3.0/
sudo chmod -R 750 /etc/freeradius/3.0/sites-available/
sudo chmod -R 750 /etc/freeradius/3.0/sites-enabled/
sudo chmod 600 /etc/freeradius/3.0/users/users

# Create log directories
print_status "Creating log directories..."
sudo mkdir -p /var/log/freeradius
sudo chown freerad:freerad /var/log/freeradius

# Test configuration
print_status "Testing FreeRADIUS configuration..."
if sudo freeradius -C; then
    print_status "Configuration test passed!"
else
    print_error "Configuration test failed. Please check the logs."
    exit 1
fi

# Enable and start FreeRADIUS service
print_status "Enabling and starting FreeRADIUS service..."
sudo systemctl enable freeradius
sudo systemctl restart freeradius

# Check service status
if sudo systemctl is-active --quiet freeradius; then
    print_status "FreeRADIUS service is running successfully!"
else
    print_error "FreeRADIUS service failed to start. Check logs with: sudo journalctl -u freeradius"
    exit 1
fi

# Configure firewall
print_status "Configuring firewall rules..."
sudo ufw allow 1812/udp comment "RADIUS Authentication"
sudo ufw allow 1813/udp comment "RADIUS Accounting"

print_status "Installation completed successfully!"
echo
print_status "Next steps:"
echo "1. Update client shared secrets in /etc/freeradius/3.0/clients.conf"
echo "2. Configure your access points to use this RADIUS server"
echo "3. Test authentication using: radtest username password localhost 0 shared_secret"
echo "4. Monitor logs at: tail -f /var/log/freeradius/radius.log"
echo
print_warning "Remember to change default passwords and secrets before production use!"