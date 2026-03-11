# WiFi Capping System for NCUK

A robust WiFi usage management system with comprehensive error handling and JWT token authentication with expiry.

## Features

- 🔐 **JWT Token Authentication** with configurable expiry (30 minutes default)
- 🛡️ **Robust Error Handling** with proper HTTP status codes and detailed error messages
- 📊 **WiFi Usage Tracking** for monitoring data consumption
- 🎯 **Data Quota Management** with daily and monthly limits
- 📝 **Comprehensive Logging** for debugging and monitoring
- 🚀 **FastAPI** framework for high performance and automatic API documentation
- 🐳 **Docker** support for easy deployment
- ✅ **Comprehensive Test Suite** for validation

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git
cd Wifi_Capping_NCUK
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## API Documentation

Once the application is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## Authentication

The system uses JWT tokens for authentication:

1. **Login** to get an access token:
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "secret"}'
```

2. **Use the token** in subsequent requests:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/auth/me"
```

### Token Expiry

- Access tokens expire after **30 minutes** by default
- Expired tokens return a `401 Unauthorized` with error code `TOKEN_EXPIRED`
- Invalid tokens return a `401 Unauthorized` with error code `INVALID_TOKEN`

## Error Handling

The system provides robust error handling with consistent error response format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "timestamp": "2025-08-17T20:54:14.271414+00:00"
}
```

### Error Codes

- `TOKEN_EXPIRED` (401): Access token has expired
- `INVALID_TOKEN` (401): Invalid or malformed token
- `USER_NOT_FOUND` (404): User does not exist
- `QUOTA_EXCEEDED` (429): WiFi usage quota exceeded
- `VALIDATION_ERROR` (422): Request validation failed
- `INTERNAL_SERVER_ERROR` (500): Unexpected server error

## Demo

Run the comprehensive demo to see all features in action:

```bash
python demo.py
```

This will test:
- ✅ Health checks
- ✅ Authentication flows
- ✅ Token validation
- ✅ Token expiry handling
- ✅ WiFi usage tracking
- ✅ Error handling scenarios

## Testing

Run the test suite:

```bash
pytest test_main.py -v
```

## Configuration

Key configuration options in `.env`:

```env
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
LOG_LEVEL=INFO
```

## Production Deployment

1. **Security**: Change the `SECRET_KEY` to a strong, random value
2. **HTTPS**: Use a reverse proxy (nginx) with SSL certificates
3. **Database**: Replace the mock database with a real database (PostgreSQL, MySQL)
4. **Monitoring**: Set up proper logging and monitoring
5. **Environment**: Use environment-specific configuration

## Default Test User

For testing purposes, a default user is available:
- **Username**: `testuser`
- **Password**: `secret`
- **Daily limit**: 1024 MB
- **Monthly limit**: 10240 MB

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.
