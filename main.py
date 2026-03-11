#!/usr/bin/env python3
"""
WiFi Capping NCUK - Main Application
Command-line interface for the WiFi capping system with freeRADIUS integration
"""

import sys
import signal
import logging
import click
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.wifi_capping.utils.config import Config, setup_logging
from src.wifi_capping.capping import WifiCappingService
from src.wifi_capping.web import run_web_server


logger = logging.getLogger(__name__)


@click.group()
@click.option('--config', '-c', help='Path to configuration file (.env)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, verbose):
    """WiFi Capping NCUK - Secure freeRADIUS Integration System"""
    
    # Initialize configuration
    ctx.ensure_object(dict)
    
    try:
        ctx.obj['config'] = Config(config)
        
        # Override log level if verbose
        if verbose:
            ctx.obj['config'].log_level = 'DEBUG'
            
        setup_logging(ctx.obj['config'])
        logger.info("WiFi Capping NCUK system initialized")
        
    except Exception as e:
        click.echo(f"Configuration error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def start(ctx):
    """Start the WiFi capping service with web interface"""
    
    config = ctx.obj['config']
    
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        sys.exit(0)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("Starting WiFi capping service...")
        click.echo("Starting WiFi Capping NCUK service...")
        click.echo(f"Web interface will be available at http://{config.flask_host}:{config.flask_port}")
        
        # Start web server (this will also start the WiFi service)
        run_web_server(config)
        
    except Exception as e:
        logger.error(f"Service start error: {str(e)}")
        click.echo(f"Error starting service: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def test_radius(ctx):
    """Test connection to freeRADIUS server"""
    
    config = ctx.obj['config']
    
    try:
        from src.wifi_capping.radius import RadiusClient
        
        click.echo("Testing RADIUS server connection...")
        
        radius_client = RadiusClient(config)
        
        if radius_client.test_connection():
            click.echo("✓ RADIUS server connection successful", fg='green')
            
            # Test authentication with dummy credentials
            click.echo("Testing authentication with test credentials...")
            success, attrs = radius_client.authenticate_user("test", "test")
            
            if success:
                click.echo("✓ Test authentication successful", fg='green')
                click.echo(f"Attributes received: {attrs}")
            else:
                click.echo("ℹ Test authentication failed (expected with dummy credentials)", fg='yellow')
                
        else:
            click.echo("✗ RADIUS server connection failed", fg='red')
            click.echo("Please check your RADIUS server configuration")
            
    except Exception as e:
        click.echo(f"✗ RADIUS test error: {str(e)}", fg='red')


@cli.command()
@click.option('--username', '-u', prompt=True, help='Username to authenticate')
@click.option('--password', '-p', prompt=True, hide_input=True, help='Password')
@click.option('--user-ip', prompt=True, help='User IP address')
@click.option('--nas-ip', prompt=True, help='NAS IP address')
@click.option('--nas-port', type=int, default=0, help='NAS port number')
@click.option('--bandwidth-limit', type=int, help='Bandwidth limit in MB')
@click.pass_context
def authenticate(ctx, username, password, user_ip, nas_ip, nas_port, bandwidth_limit):
    """Authenticate a user and start a session"""
    
    config = ctx.obj['config']
    
    try:
        service = WifiCappingService(config)
        service.start()
        
        click.echo(f"Authenticating user '{username}'...")
        
        success, session_id = service.authenticate_and_start_session(
            username, password, user_ip, nas_ip, nas_port, bandwidth_limit
        )
        
        if success:
            click.echo(f"✓ Authentication successful!", fg='green')
            click.echo(f"Session ID: {session_id}")
            click.echo(f"Bandwidth limit: {bandwidth_limit or config.default_bandwidth_limit_mb} MB")
        else:
            click.echo("✗ Authentication failed", fg='red')
            
        service.stop()
        
    except Exception as e:
        click.echo(f"✗ Authentication error: {str(e)}", fg='red')


@cli.command()
@click.pass_context
def status(ctx):
    """Show system status and configuration"""
    
    config = ctx.obj['config']
    
    click.echo("WiFi Capping NCUK - System Status")
    click.echo("=" * 40)
    click.echo(f"RADIUS Server: {config.radius_host}:{config.radius_auth_port}")
    click.echo(f"Default Bandwidth Limit: {config.default_bandwidth_limit_mb} MB")
    click.echo(f"Monitoring Interval: {config.monitoring_interval_seconds} seconds")
    click.echo(f"Max Session Time: {config.max_session_time_hours} hours")
    click.echo(f"Web Interface: {config.flask_host}:{config.flask_port}")
    click.echo(f"Log Level: {config.log_level}")
    
    # Test RADIUS connection
    try:
        from src.wifi_capping.radius import RadiusClient
        radius_client = RadiusClient(config)
        radius_status = "✓ Connected" if radius_client.test_connection() else "✗ Not Connected"
        click.echo(f"RADIUS Status: {radius_status}")
    except Exception as e:
        click.echo(f"RADIUS Status: ✗ Error - {str(e)}")


@cli.command()
@click.pass_context
def create_config(ctx):
    """Create a sample configuration file"""
    
    config_path = Path(".env")
    
    if config_path.exists():
        if not click.confirm(f"Configuration file {config_path} already exists. Overwrite?"):
            return
    
    # Copy example config
    example_path = Path(__file__).parent / ".env.example"
    
    try:
        if example_path.exists():
            import shutil
            shutil.copy(example_path, config_path)
            click.echo(f"✓ Configuration file created: {config_path}")
            click.echo("Please edit the configuration file with your settings:")
            click.echo("- Set RADIUS_SECRET to your RADIUS server secret")
            click.echo("- Set FLASK_SECRET_KEY to a secure random key")
            click.echo("- Configure RADIUS server host and ports")
        else:
            # Create basic config if example doesn't exist
            config_content = """# freeRADIUS Server Configuration
RADIUS_HOST=127.0.0.1
RADIUS_AUTH_PORT=1812
RADIUS_ACCT_PORT=1813
RADIUS_SECRET=your_radius_secret_here

# WiFi Capping Configuration
DEFAULT_BANDWIDTH_LIMIT_MB=1000
MONITORING_INTERVAL_SECONDS=60
MAX_SESSION_TIME_HOURS=24

# Web Interface Configuration
FLASK_SECRET_KEY=your_flask_secret_key_here
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=wifi_capping.log
"""
            config_path.write_text(config_content)
            click.echo(f"✓ Basic configuration file created: {config_path}")
            
    except Exception as e:
        click.echo(f"✗ Error creating configuration file: {str(e)}", err=True)


if __name__ == "__main__":
    cli()
