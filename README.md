# Wi-Fi Usage Capping System for NCUK

A robust Python-based system that monitors Wi-Fi data usage and automatically disconnects the connection when usage exceeds 20GB to help manage bandwidth consumption.

## Features

- **Automatic Monitoring**: Continuously tracks network data usage in the background
- **20GB Usage Limit**: Automatically disconnects Wi-Fi when usage reaches 20GB
- **Persistent Storage**: Maintains usage data across system restarts
- **Configurable Settings**: Customizable data limits, monitoring intervals, and reset periods
- **Multiple Disconnect Methods**: Uses multiple techniques to ensure reliable Wi-Fi disconnection
- **Logging System**: Comprehensive logging for monitoring and debugging
- **Status Reporting**: Real-time usage status and statistics
- **Manual Controls**: Commands for status checking, resetting usage, and reconnecting

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git
cd Wifi_Capping_NCUK
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. For system-wide installation (recommended):
```bash
sudo ./install.sh
```

### Basic Usage

**Check current usage status:**
```bash
python3 wifi_capping.py --status
```

**Start monitoring (runs continuously):**
```bash
python3 wifi_capping.py --monitor
```

**Reset usage data:**
```bash
python3 wifi_capping.py --reset
```

**Reconnect Wi-Fi after disconnection:**
```bash
python3 wifi_capping.py --reconnect
```

## System Service (Automatic Startup)

After running the installation script, the system can be managed as a service:

```bash
# Start the service
sudo systemctl start wifi-capping

# Enable automatic startup
sudo systemctl enable wifi-capping

# Check service status
sudo systemctl status wifi-capping

# View logs
sudo journalctl -u wifi-capping -f

# Stop the service
sudo systemctl stop wifi-capping
```

## Configuration

The system uses a `config.json` file for configuration:

```json
{
  "data_limit_gb": 20,
  "reset_period_days": 30,
  "check_interval_seconds": 60,
  "wifi_interface": "wlan0",
  "log_level": "INFO"
}
```

### Configuration Options

- **data_limit_gb**: Data usage limit in gigabytes (default: 20)
- **reset_period_days**: Days after which usage data resets (default: 30)
- **check_interval_seconds**: How often to check usage in seconds (default: 60)
- **wifi_interface**: Wi-Fi interface name (default: "wlan0", auto-detected)
- **log_level**: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## How It Works

1. **Network Monitoring**: Uses `psutil` to monitor network interface statistics
2. **Usage Tracking**: Calculates data usage by tracking bytes sent/received
3. **Persistent Storage**: Saves usage data to `usage_data.json`
4. **Limit Enforcement**: When 20GB limit is reached, automatically disconnects Wi-Fi using:
   - NetworkManager (`nmcli`)
   - ifconfig commands
   - ip commands
5. **Automatic Reset**: Usage data resets after the configured period (default: 30 days)

## Files and Directories

- `wifi_capping.py`: Main application script
- `config.json`: Configuration file
- `usage_data.json`: Usage data storage (created automatically)
- `wifi_capping.log`: Log file
- `requirements.txt`: Python dependencies
- `install.sh`: System installation script
- `wifi-capping.service`: Systemd service file
- `test_wifi_capping.py`: Test suite

## Testing

Run the test suite to verify functionality:

```bash
python3 test_wifi_capping.py
```

The test suite includes:
- Unit tests for core functionality
- Integration tests for configuration and data persistence
- Mock testing for network interface interactions

## Security and Permissions

The system requires elevated privileges to:
- Monitor network interfaces
- Disconnect Wi-Fi connections
- Access system network configuration

When running as a service, it operates with root privileges to ensure reliable network control.

## Troubleshooting

### Common Issues

**Wi-Fi won't disconnect:**
- Check if the correct Wi-Fi interface is detected
- Verify the system has NetworkManager or network tools installed
- Check logs for specific error messages

**Usage not tracking correctly:**
- Ensure the system has proper permissions to read network statistics
- Check if the network interface name is correct in configuration

**Service won't start:**
- Verify Python 3 and psutil are installed
- Check service logs: `sudo journalctl -u wifi-capping`
- Ensure configuration file is valid JSON

### Log Analysis

Check the log file for detailed information:
```bash
tail -f wifi_capping.log
```

Common log messages:
- `Starting Wi-Fi usage monitoring...`: System started successfully
- `Current usage: X.XXgb / 20GB`: Regular status updates
- `Data limit exceeded! Disconnecting Wi-Fi...`: Limit reached
- `Wi-Fi disconnected`: Successful disconnection

## Requirements

- **Operating System**: Linux (tested on Ubuntu, Debian, CentOS)
- **Python**: 3.6 or higher
- **Dependencies**: psutil (automatically installed)
- **Network Tools**: NetworkManager, ifconfig, or ip commands
- **Permissions**: Root access for Wi-Fi control

## Use Cases

- **Educational Institutions**: Manage student internet usage
- **Shared Networks**: Control bandwidth consumption in shared environments
- **Data Plan Management**: Prevent exceeding mobile hotspot limits
- **Network Administration**: Automated bandwidth enforcement

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is open source. Please check the repository for license details.

## Support

For issues, questions, or contributions, please use the GitHub issue tracker.
