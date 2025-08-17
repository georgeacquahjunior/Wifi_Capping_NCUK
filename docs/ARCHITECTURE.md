# System Architecture

This document provides a detailed overview of the WiFi Capping System architecture, components, and design decisions.

## 🏗️ Overview

The WiFi Capping System is built using a microservices-inspired architecture with clear separation of concerns. The system consists of several key components that work together to provide bandwidth management and user authentication services.

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet                                  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    Firewall                                      │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                Load Balancer (Nginx)                             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                Application Layer                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │               Web Frontend                                  │ │
│  │          (Admin Dashboard)                                  │ │
│  └─────────────────────┬───────────────────────────────────────┘ │
│                        │                                         │
│  ┌─────────────────────▼───────────────────────────────────────┐ │
│  │               REST API                                      │ │
│  │             (Node.js)                                       │ │
│  └─────────────────────┬───────────────────────────────────────┘ │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────┐
│                    Service Layer                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   User      │  │  Bandwidth  │  │   RADIUS    │  │   Session   │ │
│  │  Service    │  │   Service   │  │   Service   │  │   Service   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────┐
│                   Data Layer                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │   MySQL/    │  │ FreeRADIUS  │  │    Redis    │                  │
│  │ PostgreSQL  │  │  Database   │  │   (Cache)   │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────┐
│                Network Infrastructure                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │ FreeRADIUS  │  │     NAS     │  │   Access    │                  │
│  │   Server    │  │  (Network   │  │   Points    │                  │
│  │             │  │   Access    │  │  (WiFi APs) │                  │
│  │             │  │  Server)    │  │             │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
```

## 🧱 Component Details

### Web Frontend (Admin Dashboard)

**Technology Stack:**
- HTML5, CSS3, JavaScript (ES6+)
- Bootstrap 5 for responsive design
- Chart.js for data visualization
- WebSocket for real-time updates

**Responsibilities:**
- User interface for system administration
- Real-time dashboard with usage statistics
- User management interface
- System configuration panels
- Reports and analytics visualization

### REST API (Node.js Backend)

**Technology Stack:**
- Node.js 16+ with Express.js framework
- JWT for authentication
- Bcrypt for password hashing
- Joi for input validation
- Winston for logging

**Responsibilities:**
- HTTP API endpoints for frontend
- Authentication and authorization
- Business logic coordination
- Input validation and sanitization
- Logging and monitoring

## 🔄 Data Flow Diagrams

### User Authentication Flow

1. Client device connects to WiFi
2. Access Point forwards to NAS
3. NAS sends RADIUS Access-Request
4. RADIUS server queries database
5. API validates user status and bandwidth
6. RADIUS responds with Access-Accept/Reject
7. User is granted or denied access

### Bandwidth Monitoring Flow

1. NAS sends periodic accounting updates
2. RADIUS server processes usage data
3. API updates real-time counters
4. System checks against bandwidth limits
5. Automatic disconnection if limit exceeded

## 🔒 Security Architecture

### Authentication Layer
- JWT token-based authentication
- Role-based access control (RBAC)
- Multi-factor authentication support
- Session management and timeout

### Data Protection
- Encryption at rest and in transit
- Password hashing with bcrypt
- SQL injection prevention
- XSS and CSRF protection

## 📊 Performance Considerations

### Scalability Patterns
- Horizontal scaling with load balancers
- Database connection pooling
- Redis caching for session data
- CDN for static assets

### Database Optimization
- Proper indexing strategy
- Query optimization
- Connection pooling
- Read replicas for reporting

## 📈 Monitoring and Observability

### Logging Strategy
- Structured logging with Winston
- Centralized log aggregation
- Error tracking and alerting
- Performance metrics collection

### Health Checks
- Application health endpoints
- Database connectivity checks
- External service monitoring
- Real-time status dashboard

---

This architecture ensures the system is scalable, maintainable, and secure while meeting NCUK's specific requirements for WiFi bandwidth management.