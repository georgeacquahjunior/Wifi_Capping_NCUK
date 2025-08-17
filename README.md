# WiFi Capping NCUK - Secure freeRADIUS Integration

A comprehensive WiFi bandwidth capping system with secure freeRADIUS integration for authentication and accounting. This system provides real-time monitoring, bandwidth enforcement, and detailed usage tracking for WiFi networks.

## Features

### 🔐 Secure freeRADIUS Integration
- **Authentication**: Secure user authentication against freeRADIUS server
- **Accounting**: Real-time accounting (start/stop/update) with detailed usage tracking
- **Security**: Encrypted communication and secure credential handling
- **Standards Compliance**: Full RADIUS RFC compliance

### 📊 Bandwidth Management
- **Real-time Monitoring**: Continuous bandwidth usage tracking
- **Flexible Limits**: Configurable per-user bandwidth limits
- **Traffic Shaping**: Automatic bandwidth capping when limits exceeded
- **Session Management**: Complete session lifecycle management

### 🌐 Web Interface
- **Dashboard**: Real-time monitoring dashboard with live statistics
- **User Management**: Easy user authentication and session management
- **REST API**: Complete RESTful API for integration
- **Mobile Responsive**: Works on desktop and mobile devices

### 🛡️ Security Features
- **Credential Validation**: Strong password and username validation
- **Session Security**: Cryptographically secure session IDs
- **Input Sanitization**: Protection against injection attacks
- **Message Integrity**: HMAC signatures for message authenticity

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git
cd Wifi_Capping_NCUK

# Install dependencies
pip install -r requirements.txt

# Create configuration file
python main.py create-config
```

### 2. Configuration

Edit the `.env` file with your settings:

```bash
# freeRADIUS Server Configuration
RADIUS_HOST=your_radius_server_ip
RADIUS_AUTH_PORT=1812
RADIUS_ACCT_PORT=1813
RADIUS_SECRET=your_radius_secret

# WiFi Capping Configuration
DEFAULT_BANDWIDTH_LIMIT_MB=1000
MONITORING_INTERVAL_SECONDS=60
MAX_SESSION_TIME_HOURS=24

# Web Interface Configuration
FLASK_SECRET_KEY=your_secure_secret_key
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### 3. Test RADIUS Connection

```bash
python main.py test-radius
```

### 4. Start the Service

```bash
python main.py start
```

The web interface will be available at `http://localhost:5000`

## Usage

### Web Dashboard

1. **Access Dashboard**: Open your browser to `http://localhost:5000`
2. **Authenticate Users**: Use the authentication form to start user sessions
3. **Monitor Usage**: View real-time bandwidth usage and session status
4. **Manage Sessions**: End sessions or view detailed statistics

### Command Line Interface

```bash
# Show system status
python main.py status

# Test RADIUS server
python main.py test-radius

# Authenticate a user (interactive)
python main.py authenticate

# Start the service
python main.py start
```

### REST API

#### Authentication
```bash
curl -X POST http://localhost:5000/api/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user123",
    "password": "password",
    "user_ip": "192.168.1.100",
    "nas_ip": "192.168.1.1",
    "nas_port": 0,
    "bandwidth_limit_mb": 500
  }'
```

#### Session Management
```bash
# Get all sessions
curl http://localhost:5000/api/sessions

# Get specific session
curl http://localhost:5000/api/sessions/{session_id}

# End session
curl -X POST http://localhost:5000/api/sessions/{session_id}/end

# Check service status
curl http://localhost:5000/api/status
```

## Architecture

### Components

1. **RADIUS Client**: Handles authentication and accounting with freeRADIUS
2. **Bandwidth Monitor**: Tracks usage and enforces limits
3. **Session Manager**: Manages user sessions and lifecycle
4. **Web Interface**: Provides dashboard and REST API
5. **Security Layer**: Handles encryption and validation

### Data Flow

```
User Request → Authentication → RADIUS Server → Session Creation → 
Bandwidth Monitoring → Usage Tracking → Accounting Updates → 
Limit Enforcement → Session Termination
```

## Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `RADIUS_HOST` | freeRADIUS server IP | 127.0.0.1 |
| `RADIUS_AUTH_PORT` | Authentication port | 1812 |
| `RADIUS_ACCT_PORT` | Accounting port | 1813 |
| `RADIUS_SECRET` | RADIUS shared secret | testing123 |
| `DEFAULT_BANDWIDTH_LIMIT_MB` | Default bandwidth limit | 1000 |
| `MONITORING_INTERVAL_SECONDS` | Monitoring frequency | 60 |
| `MAX_SESSION_TIME_HOURS` | Maximum session duration | 24 |
| `FLASK_HOST` | Web interface host | 0.0.0.0 |
| `FLASK_PORT` | Web interface port | 5000 |

## Security Considerations

### Production Deployment

1. **Change Default Secrets**: Always change default RADIUS and Flask secrets
2. **Use HTTPS**: Deploy behind HTTPS proxy (nginx, Apache)
3. **Firewall Rules**: Restrict access to RADIUS and web ports
4. **Regular Updates**: Keep dependencies updated
5. **Monitor Logs**: Set up log monitoring and alerting

### RADIUS Security

- Use strong shared secrets (minimum 16 characters)
- Enable RADIUS over TLS if supported
- Regularly rotate shared secrets
- Monitor authentication failures

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Run specific tests:

```bash
python tests/test_radius_integration.py
```

## Requirements

- Python 3.7+
- freeRADIUS server (configured separately)
- Network access to RADIUS server
- Linux/Unix environment (for network monitoring)

### Python Dependencies

- `pyrad` - RADIUS client library
- `flask` - Web framework
- `pycryptodome` - Cryptographic functions
- `python-dotenv` - Environment configuration
- `psutil` - System monitoring
- `requests` - HTTP client
- `click` - CLI framework

## Troubleshooting

### Common Issues

1. **RADIUS Connection Failed**
   - Check RADIUS server is running
   - Verify host and port configuration
   - Check firewall rules
   - Validate shared secret

2. **Authentication Failures**
   - Verify user exists in RADIUS database
   - Check password requirements
   - Review RADIUS server logs

3. **Bandwidth Monitoring Issues**
   - Ensure running with appropriate permissions
   - Check network interface access
   - Verify system statistics availability

### Logs

Check the application logs:

```bash
tail -f wifi_capping.log
```

Enable debug logging:

```bash
LOG_LEVEL=DEBUG python main.py start
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details

## Acknowledgments

- freeRADIUS community for the excellent RADIUS server
- pyrad library developers
- Flask framework team