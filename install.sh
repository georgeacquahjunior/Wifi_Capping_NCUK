#!/bin/bash
# Installation script for Wi-Fi Usage Capping System

set -e

echo "Installing Wi-Fi Usage Capping System for NCUK..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root (use sudo)"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Create installation directory
INSTALL_DIR="/opt/wifi-capping-ncuk"
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy files
echo "Copying files..."
cp wifi_capping.py "$INSTALL_DIR/"
cp config.json "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"

# Make executable
chmod +x "$INSTALL_DIR/wifi_capping.py"

# Install systemd service
echo "Installing systemd service..."
cp wifi-capping.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable wifi-capping.service

echo "Installation complete!"
echo ""
echo "Usage:"
echo "  Start service: sudo systemctl start wifi-capping"
echo "  Stop service:  sudo systemctl stop wifi-capping"
echo "  Check status:  sudo systemctl status wifi-capping"
echo "  View logs:     sudo journalctl -u wifi-capping -f"
echo ""
echo "Manual commands:"
echo "  Check usage:   sudo python3 $INSTALL_DIR/wifi_capping.py --status"
echo "  Reset usage:   sudo python3 $INSTALL_DIR/wifi_capping.py --reset"
echo "  Reconnect:     sudo python3 $INSTALL_DIR/wifi_capping.py --reconnect"
echo ""
echo "Configuration file: $INSTALL_DIR/config.json"
echo "Log file: $INSTALL_DIR/wifi_capping.log"