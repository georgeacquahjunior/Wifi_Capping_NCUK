#!/bin/bash
# WiFi Capping NCUK - Quick Start Script
# This script sets up and runs the WiFi capping system

set -e

echo "WiFi Capping NCUK - Quick Start"
echo "==============================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "Error: pip is required but not installed."
    exit 1
fi

echo "1. Installing dependencies..."
python3 -m pip install -r requirements.txt --user

echo "2. Creating configuration file..."
if [ ! -f .env ]; then
    python3 main.py create-config
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file with your settings:"
    echo "   - Set RADIUS_SECRET to your RADIUS server secret"
    echo "   - Set FLASK_SECRET_KEY to a secure random key"
    echo "   - Configure RADIUS server host and ports"
    echo ""
    read -p "Press Enter after editing the configuration file..."
fi

echo "3. Testing RADIUS connection..."
python3 main.py test-radius

echo "4. Showing system status..."
python3 main.py status

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the service:"
echo "  python3 main.py start"
echo ""
echo "To authenticate a user:"
echo "  python3 main.py authenticate"
echo ""
echo "Web interface will be available at: http://localhost:5000"