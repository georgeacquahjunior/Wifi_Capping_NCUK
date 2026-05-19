#!/bin/bash
# Setup script for WiFi Capping NCUK FreeRADIUS-NAS-Backend system

set -e

echo "Setting up WiFi Capping NCUK FreeRADIUS-NAS-Backend system..."

# Check if running as root for system configurations
if [[ $EUID -eq 0 ]]; then
    INSTALL_SYSTEM=true
    echo "Running as root - will install system packages and configure FreeRADIUS"
else
    INSTALL_SYSTEM=false
    echo "Running as user - will only setup Python environment and database"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p {logs,data,backup}

# Install Python dependencies
echo "Installing Python dependencies..."
if command -v python3 &> /dev/null; then
    if command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt
    else
        echo "pip3 not found. Please install pip3 manually."
        exit 1
    fi
else
    echo "Python3 not found. Please install Python3 manually."
    exit 1
fi

# Copy environment configuration
echo "Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template. Please review and update the configuration."
fi

# Database setup
echo "Setting up database..."
if command -v mysql &> /dev/null; then
    echo "MySQL found. To setup the database, run:"
    echo "mysql -u root -p < database/schema.sql"
else
    echo "MySQL not found. Please install MySQL/MariaDB and run:"
    echo "mysql -u root -p < database/schema.sql"
fi

# FreeRADIUS installation and configuration (if running as root)
if [ "$INSTALL_SYSTEM" = true ]; then
    echo "Installing FreeRADIUS..."
    
    # Detect package manager and install FreeRADIUS
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y freeradius freeradius-mysql freeradius-utils
    elif command -v yum &> /dev/null; then
        yum install -y freeradius freeradius-mysql freeradius-utils
    elif command -v dnf &> /dev/null; then
        dnf install -y freeradius freeradius-mysql freeradius-utils
    else
        echo "Package manager not detected. Please install FreeRADIUS manually."
        exit 1
    fi
    
    echo "Configuring FreeRADIUS..."
    
    # Backup original configurations
    RADIUS_DIR="/etc/freeradius/3.0"
    if [ -d "$RADIUS_DIR" ]; then
        cp -r "$RADIUS_DIR" "${RADIUS_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Copy our configurations
    cp config/freeradius/radiusd.conf "$RADIUS_DIR/" 2>/dev/null || echo "Could not copy radiusd.conf"
    cp config/freeradius/clients.conf "$RADIUS_DIR/" 2>/dev/null || echo "Could not copy clients.conf"
    cp config/freeradius/mods-available/rest "$RADIUS_DIR/mods-available/" 2>/dev/null || echo "Could not copy rest module"
    cp config/freeradius/sites-available/wifi-capping "$RADIUS_DIR/sites-available/" 2>/dev/null || echo "Could not copy wifi-capping site"
    
    # Enable the site and modules
    ln -sf "$RADIUS_DIR/sites-available/wifi-capping" "$RADIUS_DIR/sites-enabled/" 2>/dev/null || echo "Could not enable wifi-capping site"
    ln -sf "$RADIUS_DIR/mods-available/rest" "$RADIUS_DIR/mods-enabled/" 2>/dev/null || echo "Could not enable rest module"
    
    # Set proper permissions
    chown -R freerad:freerad "$RADIUS_DIR" 2>/dev/null || echo "Could not set FreeRADIUS permissions"
    
    echo "FreeRADIUS configuration completed."
else
    echo "Skipping FreeRADIUS installation (not running as root)."
    echo "To install FreeRADIUS, run this script as root or install manually."
fi

# Create startup scripts
echo "Creating startup scripts..."

# Backend startup script
cat > scripts/start_backend.sh << 'EOF'
#!/bin/bash
# Start the NAS backend API server

echo "Starting WiFi Capping NAS Backend..."
cd "$(dirname "$0")/.."

# Load environment
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Start the backend
python3 backend/nas/radius_backend.py
EOF

# Admin tool script
cat > scripts/admin_validate.sh << 'EOF'
#!/bin/bash
# Run the admin validation tool

echo "Running WiFi Capping Admin Validation..."
cd "$(dirname "$0")/.."

# Load environment
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Run validation
python3 admin_tools/validation_tool.py "$@"
EOF

# Test script
cat > scripts/run_tests.sh << 'EOF'
#!/bin/bash
# Run test suite

echo "Running WiFi Capping Test Suite..."
cd "$(dirname "$0")/.."

# Load environment
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Run tests
python3 tests/test_radius_flow.py
EOF

# Make scripts executable
chmod +x scripts/*.sh

echo "Setup completed!"
echo ""
echo "Next steps:"
echo "1. Review and update the .env file with your configuration"
echo "2. Set up your MySQL database:"
echo "   mysql -u root -p < database/schema.sql"
echo "3. Start the backend API server:"
echo "   ./scripts/start_backend.sh"
echo "4. Run validation tests:"
echo "   ./scripts/admin_validate.sh --report"
echo ""
if [ "$INSTALL_SYSTEM" = true ]; then
    echo "5. Start FreeRADIUS service:"
    echo "   systemctl start freeradius"
    echo "   systemctl enable freeradius"
else
    echo "5. Install and configure FreeRADIUS (requires root access)"
fi
echo ""
echo "For troubleshooting, check the logs in the logs/ directory."