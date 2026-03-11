# API Documentation

This document provides comprehensive documentation for the WiFi Capping System REST API endpoints.

## 📋 Overview

The WiFi Capping System provides a RESTful API for managing users, monitoring bandwidth usage, and administering the system. All API endpoints require authentication except for the health check endpoint.

### Base URL
```
Production: https://your-domain.com/api
Development: http://localhost:3000/api
```

### API Version
Current version: `v1`

All endpoints are prefixed with `/api/v1/`

## 🔐 Authentication

### JWT Authentication
The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your-password",
  "mfa_code": "123456"  // Optional, required if MFA is enabled
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "admin",
      "role": "administrator",
      "permissions": ["user:read", "user:write", "system:admin"]
    }
  }
}
```

### Token Refresh
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

## 📊 Standard Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "meta": {
    "timestamp": "2025-08-17T20:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "username",
      "reason": "Username is required"
    }
  },
  "meta": {
    "timestamp": "2025-08-17T20:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### Pagination
For paginated endpoints:
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "pages": 8,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

## 🚀 Health Check

### GET /health
Check system health and status.

**Authentication:** None required

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-08-17T20:30:00Z",
    "version": "1.0.0",
    "uptime": 3600,
    "services": {
      "database": "healthy",
      "radius": "healthy",
      "cache": "healthy"
    }
  }
}
```

## 👤 Authentication Endpoints

### POST /api/v1/auth/login
Authenticate user and obtain access token.

**Request Body:**
```json
{
  "username": "string (required)",
  "password": "string (required)",
  "mfa_code": "string (optional)"
}
```

### POST /api/v1/auth/logout
Invalidate current session token.

**Headers:** `Authorization: Bearer <token>`

### POST /api/v1/auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "string (required)"
}
```

### POST /api/v1/auth/change-password
Change user password.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "current_password": "string (required)",
  "new_password": "string (required)",
  "confirm_password": "string (required)"
}
```

## 👥 User Management

### GET /api/v1/users
Retrieve list of users with optional filtering.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)
- `search` (string): Search by username or email
- `status` (string): Filter by status (active, inactive, suspended)
- `role` (string): Filter by role
- `sort` (string): Sort field (username, created_at, last_login)
- `order` (string): Sort order (asc, desc)

**Example Request:**
```http
GET /api/v1/users?page=1&limit=20&search=john&status=active&sort=username&order=asc
```

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 123,
        "username": "john.doe",
        "email": "john.doe@university.ac.uk",
        "first_name": "John",
        "last_name": "Doe",
        "role": "student",
        "status": "active",
        "bandwidth_limit": "20GB",
        "bandwidth_used": "15.5GB",
        "last_login": "2025-08-17T18:30:00Z",
        "created_at": "2025-08-01T10:00:00Z",
        "updated_at": "2025-08-17T18:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1500,
      "pages": 75,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### GET /api/v1/users/:id
Retrieve specific user details.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `id` (integer): User ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "username": "john.doe",
    "email": "john.doe@university.ac.uk",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "status": "active",
    "bandwidth_limit": "20GB",
    "bandwidth_used": "15.5GB",
    "mac_addresses": ["aa:bb:cc:dd:ee:ff"],
    "groups": ["students", "engineering"],
    "last_login": "2025-08-17T18:30:00Z",
    "login_count": 45,
    "created_at": "2025-08-01T10:00:00Z",
    "updated_at": "2025-08-17T18:30:00Z",
    "usage_history": [
      {
        "date": "2025-08-17",
        "bytes_in": 1073741824,
        "bytes_out": 536870912,
        "session_time": 7200
      }
    ]
  }
}
```

### POST /api/v1/users
Create a new user.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "username": "string (required, 3-50 chars)",
  "email": "string (required, valid email)",
  "password": "string (required, min 8 chars)",
  "first_name": "string (required)",
  "last_name": "string (required)",
  "role": "string (required: student, staff, admin)",
  "bandwidth_limit": "string (optional, default: 20GB)",
  "groups": ["array of strings (optional)"],
  "expires_at": "ISO date string (optional)"
}
```

**Example:**
```json
{
  "username": "jane.smith",
  "email": "jane.smith@university.ac.uk",
  "password": "SecurePass123!",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "student",
  "bandwidth_limit": "20GB",
  "groups": ["students", "computer_science"],
  "expires_at": "2026-08-01T00:00:00Z"
}
```

### PUT /api/v1/users/:id
Update existing user.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `id` (integer): User ID

**Request Body:** (All fields optional)
```json
{
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "string",
  "status": "string (active, inactive, suspended)",
  "bandwidth_limit": "string",
  "groups": ["array of strings"],
  "expires_at": "ISO date string"
}
```

### DELETE /api/v1/users/:id
Delete user account.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `id` (integer): User ID

**Query Parameters:**
- `force` (boolean): Force deletion even if user has active sessions

## 📊 Bandwidth Usage

### GET /api/v1/usage/users/:id
Get bandwidth usage for specific user.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `id` (integer): User ID

**Query Parameters:**
- `period` (string): Time period (day, week, month, year)
- `start_date` (ISO date): Start date for custom period
- `end_date` (ISO date): End date for custom period

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 123,
    "current_usage": {
      "bytes_in": 10737418240,
      "bytes_out": 5368709120,
      "total_bytes": 16106127360,
      "percentage_used": 75.5,
      "remaining_bytes": 5242880000
    },
    "daily_usage": [
      {
        "date": "2025-08-17",
        "bytes_in": 1073741824,
        "bytes_out": 536870912,
        "session_time": 7200,
        "sessions": 3
      }
    ],
    "limit": "20GB",
    "reset_date": "2025-09-01T00:00:00Z"
  }
}
```

### GET /api/v1/usage/summary
Get system-wide usage summary.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `period` (string): Time period (day, week, month)

**Response:**
```json
{
  "success": true,
  "data": {
    "total_users": 1500,
    "active_users": 450,
    "total_bandwidth": "30TB",
    "used_bandwidth": "22.5TB",
    "top_users": [
      {
        "user_id": 123,
        "username": "john.doe",
        "usage": "19.8GB",
        "percentage": 99
      }
    ],
    "usage_by_group": [
      {
        "group": "students",
        "total_usage": "15TB",
        "user_count": 1200
      }
    ]
  }
}
```

### POST /api/v1/usage/reset/:id
Reset user's bandwidth usage counter.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `id` (integer): User ID

**Request Body:**
```json
{
  "reason": "string (required)"
}
```

## 🔄 Session Management

### GET /api/v1/sessions
Get active user sessions.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `user_id` (integer): Filter by user ID
- `status` (string): Filter by status (active, inactive)
- `page` (integer): Page number
- `limit` (integer): Items per page

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "session_id": "sess_123456789",
        "user_id": 123,
        "username": "john.doe",
        "nas_ip": "192.168.1.10",
        "nas_port": 1,
        "calling_station_id": "aa:bb:cc:dd:ee:ff",
        "start_time": "2025-08-17T18:00:00Z",
        "session_time": 1800,
        "bytes_in": 104857600,
        "bytes_out": 52428800,
        "status": "active"
      }
    ],
    "pagination": {...}
  }
}
```

### DELETE /api/v1/sessions/:session_id
Disconnect user session.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `session_id` (string): Session ID

**Request Body:**
```json
{
  "reason": "string (optional)"
}
```

### POST /api/v1/sessions/disconnect-user/:id
Disconnect all sessions for a user.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `id` (integer): User ID

## 📈 Reports and Analytics

### GET /api/v1/reports/usage
Generate usage reports.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `type` (string): Report type (daily, weekly, monthly)
- `format` (string): Output format (json, csv, pdf)
- `start_date` (ISO date): Report start date
- `end_date` (ISO date): Report end date
- `group_by` (string): Group by field (user, group, nas)

### GET /api/v1/reports/security
Generate security reports.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `type` (string): Report type (failed_logins, suspicious_activity)
- `severity` (string): Filter by severity (low, medium, high, critical)

## ⚙️ System Administration

### GET /api/v1/admin/stats
Get system statistics.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "system": {
      "uptime": 604800,
      "cpu_usage": 25.5,
      "memory_usage": 68.2,
      "disk_usage": 45.8
    },
    "radius": {
      "status": "healthy",
      "auth_requests": 15420,
      "acct_requests": 8750,
      "response_time": 12
    },
    "database": {
      "status": "healthy",
      "connections": 15,
      "query_time": 2.5
    }
  }
}
```

### GET /api/v1/admin/logs
Retrieve system logs.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `level` (string): Log level (debug, info, warn, error)
- `component` (string): Component (app, radius, database)
- `start_date` (ISO date): Start date
- `end_date` (ISO date): End date
- `page` (integer): Page number
- `limit` (integer): Items per page

### POST /api/v1/admin/backup
Initiate system backup.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "type": "string (full, incremental)",
  "components": ["database", "config", "logs"]
}
```

## 🔧 Configuration

### GET /api/v1/config
Get system configuration.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "bandwidth": {
      "default_limit": "20GB",
      "check_interval": 300,
      "grace_period": 60
    },
    "security": {
      "password_min_length": 8,
      "session_timeout": 1800,
      "max_login_attempts": 5
    },
    "radius": {
      "auth_port": 1812,
      "acct_port": 1813,
      "timeout": 5
    }
  }
}
```

### PUT /api/v1/config
Update system configuration.

**Headers:** `Authorization: Bearer <token>`

**Request Body:** (Partial configuration object)

## 📝 Error Codes

| Code | Description |
|------|-------------|
| `AUTH_REQUIRED` | Authentication required |
| `AUTH_INVALID` | Invalid credentials |
| `AUTH_EXPIRED` | Token expired |
| `PERMISSION_DENIED` | Insufficient permissions |
| `VALIDATION_ERROR` | Input validation failed |
| `NOT_FOUND` | Resource not found |
| `CONFLICT` | Resource conflict |
| `RATE_LIMITED` | Too many requests |
| `SERVER_ERROR` | Internal server error |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable |

## 📚 SDK and Libraries

### JavaScript/Node.js
```javascript
const WifiCappingAPI = require('wifi-capping-sdk');

const client = new WifiCappingAPI({
  baseURL: 'https://your-domain.com/api/v1',
  apiKey: 'your-api-key'
});

// Get user
const user = await client.users.get(123);

// Create user
const newUser = await client.users.create({
  username: 'jane.doe',
  email: 'jane@university.ac.uk',
  password: 'SecurePass123!',
  role: 'student'
});
```

### Python
```python
from wifi_capping import WifiCappingClient

client = WifiCappingClient(
    base_url='https://your-domain.com/api/v1',
    api_key='your-api-key'
)

# Get user
user = client.users.get(123)

# Create user
new_user = client.users.create({
    'username': 'jane.doe',
    'email': 'jane@university.ac.uk',
    'password': 'SecurePass123!',
    'role': 'student'
})
```

## 🔗 Webhooks

### User Events
Configure webhooks for user-related events:

```json
{
  "url": "https://your-app.com/webhooks/wifi-capping",
  "events": ["user.created", "user.updated", "user.deleted"],
  "secret": "webhook-secret"
}
```

### Usage Events
```json
{
  "url": "https://your-app.com/webhooks/usage",
  "events": ["usage.limit_reached", "usage.limit_exceeded"],
  "secret": "webhook-secret"
}
```

---

**API Version**: v1  
**Last Updated**: August 2025  
**Rate Limits**: 1000 requests per hour per API key