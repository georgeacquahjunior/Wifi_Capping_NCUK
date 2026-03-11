#!/bin/bash

# WiFi Capping System - Startup Script

echo "Starting WiFi Capping System for NCUK..."
echo "========================================="

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the application
echo ""
echo "Starting Flask application..."
echo "Access the application at: http://localhost:5001"
echo ""
echo "Default Admin Credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================="

python app.py