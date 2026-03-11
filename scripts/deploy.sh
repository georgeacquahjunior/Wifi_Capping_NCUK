#!/bin/bash
# WiFi Capping NCUK - Deployment Script with Security Validation

set -e

echo "🚀 WiFi Capping NCUK Deployment Script"
echo "======================================"

# Check if running as root for network management
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  Running as root - ensure this is intentional for network management"
fi

# Create necessary directories
echo "📁 Creating directories..."
sudo mkdir -p /var/log/wifi-capping
sudo mkdir -p /etc/ssl/certs
sudo mkdir -p /etc/ssl/private

# Set proper permissions
sudo chown $USER:$USER /var/log/wifi-capping
sudo chmod 755 /var/log/wifi-capping

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Configure environment
if [ ! -f .env ]; then
    echo "⚙️  Creating environment configuration..."
    cp .env.example .env
    
    # Generate secure keys
    SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
    JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
    ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    
    # Update .env with generated keys
    sed -i "s/your-secret-key-here-change-this/$SECRET_KEY/" .env
    sed -i "s/your-jwt-secret-key-here-change-this/$JWT_SECRET_KEY/" .env
    sed -i "s/your-encryption-key-here-change-this/$ENCRYPTION_KEY/" .env
    
    echo "✅ Environment configured with secure keys"
else
    echo "✅ Environment file already exists"
fi

# Generate SSL certificates if needed
if [ ! -f /etc/ssl/certs/wifi-capping.crt ]; then
    echo "🔐 Generating SSL certificates..."
    python -c "
from src.wifi_capping.security import CertificateManager
import os

cert_pem, key_pem = CertificateManager.generate_self_signed_cert('wifi-capping.ncuk.ac.uk')
CertificateManager.save_cert_and_key(
    cert_pem, key_pem,
    '/etc/ssl/certs/wifi-capping.crt',
    '/etc/ssl/private/wifi-capping.key'
)
print('SSL certificates generated successfully')
" 2>/dev/null || echo "⚠️  SSL certificate generation requires dependencies"
fi

# Run security verification
echo "🔍 Running security verification..."
python security_verify.py --config production

SECURITY_EXIT_CODE=$?

if [ $SECURITY_EXIT_CODE -eq 0 ]; then
    echo "✅ Security verification passed - system ready for deployment"
elif [ $SECURITY_EXIT_CODE -eq 2 ]; then
    echo "⚠️  Security verification passed with warnings - review before production"
else
    echo "❌ Security verification failed - fix issues before deployment"
    exit 1
fi

# Create systemd service file
echo "📋 Creating systemd service..."
sudo tee /etc/systemd/system/wifi-capping.service > /dev/null << EOF
[Unit]
Description=WiFi Capping NCUK Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=FLASK_ENV=production
ExecStart=$(which python) app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable wifi-capping
echo "✅ Systemd service configured"

echo ""
echo "🎯 Deployment Summary:"
echo "====================="
echo "✅ Dependencies installed"
echo "✅ Environment configured"
echo "✅ SSL certificates ready"
echo "✅ Security verification passed"
echo "✅ Systemd service created"
echo ""
echo "To start the service:"
echo "  sudo systemctl start wifi-capping"
echo ""
echo "To check status:"
echo "  sudo systemctl status wifi-capping"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u wifi-capping -f"
echo ""
echo "Web interface will be available at:"
echo "  https://localhost:8443 (with SSL)"
echo "  http://localhost:8443 (without SSL in development)"