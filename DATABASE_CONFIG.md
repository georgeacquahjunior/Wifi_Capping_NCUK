# Enhanced Database Configuration

This document explains the refactored database configuration system that provides flexible, environment-based database settings for the WiFi Capping NCUK application.

## Key Features

### 1. Environment-Based Configuration
- **Development**: Uses SQLite with flexible file paths
- **Testing**: Uses in-memory SQLite for fast, isolated tests
- **Production**: Supports PostgreSQL with fallback to SQLite

### 2. Multiple Database Backends
- **SQLite**: Default for development and testing
- **PostgreSQL**: Primary choice for production
- **MySQL**: Supported via connection string validation

### 3. Flexible Database Paths
Configure database file paths using environment variables:

```bash
# Custom development database path
export DEV_DATABASE_PATH="data/my_app.db"

# Custom production database path (when using SQLite)
export PROD_DATABASE_PATH="/var/lib/myapp/production.db"
```

### 4. Production Database Configuration
For PostgreSQL in production:

```bash
export DB_HOST="your-db-host.com"
export DB_PORT="5432"
export DB_NAME="wifi_capping_prod"
export DB_USER="your_db_user"
export DB_PASSWORD="your_secure_password"
```

### 5. Database URL Override
Override any configuration with a complete database URL:

```bash
export DATABASE_URL="postgresql://user:pass@host:port/dbname"
```

## Usage Examples

### Basic Usage (Backward Compatible)
```python
from app import create_app

# Uses default development configuration
app = create_app()
```

### Environment-Specific Configuration
```python
from app import create_app

# Create app for different environments
dev_app = create_app('development')
test_app = create_app('testing')
prod_app = create_app('production')
```

### Custom Database Path
```python
import os
from app import create_app

# Set custom database path
os.environ['DEV_DATABASE_PATH'] = 'custom/path/mydb.db'
app = create_app('development')
```

## Migration from Previous Version

The refactored configuration maintains full backward compatibility. Existing code will continue to work without any changes.

### What Changed
- **Enhanced**: Environment-based configuration classes
- **Added**: Support for PostgreSQL and MySQL
- **Added**: Environment variable configuration
- **Added**: Database URL validation
- **Fixed**: SQLAlchemy 2.0 deprecation warnings
- **Added**: Application factory pattern

### What Stayed the Same
- Default database file location (`students.db`)
- All existing route handlers and models
- Database schema and initialization process

## Configuration Classes

### `DatabaseConfig`
Helper class that provides database URI generation based on environment and configuration.

### `Config` (Base)
Base configuration class with common settings.

### `DevelopmentConfig`
- Debug mode enabled
- SQLite database with configurable path
- Default path: `students.db`

### `TestingConfig`
- Testing mode enabled
- In-memory SQLite database
- URI: `sqlite:///:memory:`

### `ProductionConfig`
- Debug mode disabled
- PostgreSQL preferred, SQLite fallback
- Connection pooling enabled
- Configurable via environment variables

## Testing the Configuration

Run the included test script to verify all configuration options:

```bash
python test_config.py
```

Run the demonstration script to see configuration examples:

```bash
python demo_config.py
```

## Security Considerations

- Database passwords should be set via environment variables, never hardcoded
- Use secure connection strings in production
- The SQLite fallback in production should only be used for development/testing
- Consider using connection pooling for production PostgreSQL deployments

## Directory Structure

The configuration automatically creates necessary directories:
- Development: Current directory or custom path
- Production: `/var/lib/wifi-capping/` (with fallback to current directory)
- Testing: In-memory (no files created)