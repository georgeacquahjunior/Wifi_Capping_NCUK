# Contributing to WiFi Capping System

Thank you for your interest in contributing to the WiFi Capping System for NCUK! This document provides guidelines and information for contributors.

## 🌟 How to Contribute

We welcome contributions in many forms:
- 🐛 Bug reports and fixes
- 🚀 Feature requests and implementations
- 📚 Documentation improvements
- 🧪 Tests and test improvements
- 🔍 Code reviews
- 💡 Ideas and suggestions

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:
- Node.js 16+ installed
- Git configured with your name and email
- A GitHub account
- Basic understanding of JavaScript/Node.js
- Familiarity with RADIUS and networking concepts (for network-related contributions)

### Development Environment Setup

1. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub
   # Then clone your fork
   git clone https://github.com/your-username/Wifi_Capping_NCUK.git
   cd Wifi_Capping_NCUK
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Set Up Environment**
   ```bash
   cp .env.example .env.development
   # Edit .env.development with your local configuration
   ```

4. **Set Up Development Database**
   ```bash
   # Using Docker (recommended)
   docker-compose up -d db
   
   # Or install MySQL/PostgreSQL locally
   npm run db:setup:dev
   ```

5. **Run Tests**
   ```bash
   npm test
   ```

6. **Start Development Server**
   ```bash
   npm run dev
   ```

## 🔄 Development Workflow

### Branching Strategy

We use GitFlow branching model:

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical production fixes
- `release/*`: Release preparation

### Creating a Feature Branch

```bash
# Start from develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ...

# Commit your changes
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name
```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(auth): add multi-factor authentication support
fix(radius): resolve connection timeout issues
docs(api): update endpoint documentation
test(users): add integration tests for user management
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
├── fixtures/      # Test data
└── helpers/       # Test utilities
```

### Writing Tests

#### Unit Tests
```javascript
// tests/unit/services/userService.test.js
const { expect } = require('chai');
const UserService = require('../../../src/services/UserService');

describe('UserService', () => {
  describe('createUser', () => {
    it('should create a new user with valid data', async () => {
      const userData = {
        username: 'testuser',
        email: 'test@example.com',
        password: 'SecurePass123!'
      };
      
      const user = await UserService.createUser(userData);
      
      expect(user).to.have.property('id');
      expect(user.username).to.equal('testuser');
      expect(user.email).to.equal('test@example.com');
    });
    
    it('should throw error for invalid email', async () => {
      const userData = {
        username: 'testuser',
        email: 'invalid-email',
        password: 'SecurePass123!'
      };
      
      await expect(UserService.createUser(userData))
        .to.be.rejectedWith('Invalid email format');
    });
  });
});
```

#### Integration Tests
```javascript
// tests/integration/api/users.test.js
const request = require('supertest');
const app = require('../../../src/app');

describe('Users API', () => {
  let authToken;
  
  before(async () => {
    // Setup test database
    await setupTestDatabase();
    
    // Get auth token
    const response = await request(app)
      .post('/api/v1/auth/login')
      .send({
        username: 'admin',
        password: 'admin123'
      });
    
    authToken = response.body.data.token;
  });
  
  describe('GET /api/v1/users', () => {
    it('should return list of users', async () => {
      const response = await request(app)
        .get('/api/v1/users')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);
      
      expect(response.body.success).to.be.true;
      expect(response.body.data.items).to.be.an('array');
    });
  });
});
```

### Running Tests

```bash
# Run all tests
npm test

# Run specific test suites
npm run test:unit
npm run test:integration
npm run test:e2e

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

### Test Coverage

Maintain minimum test coverage:
- **Unit tests**: 90% coverage
- **Integration tests**: 80% coverage
- **Critical paths**: 100% coverage

## 📝 Code Style Guidelines

### JavaScript Style

We use ESLint and Prettier for code formatting:

```bash
# Check code style
npm run lint

# Fix auto-fixable issues
npm run lint:fix

# Format code
npm run format
```

### Code Standards

#### Variables and Functions
```javascript
// Use camelCase
const userName = 'john.doe';
const calculateBandwidthUsage = () => { /* ... */ };

// Use descriptive names
const userBandwidthLimit = '20GB'; // Good
const limit = '20GB'; // Avoid

// Use const for immutable values
const MAX_RETRY_ATTEMPTS = 3;
const API_BASE_URL = 'https://api.example.com';
```

#### Error Handling
```javascript
// Use try-catch for async operations
try {
  const user = await UserService.getUser(userId);
  return user;
} catch (error) {
  logger.error('Failed to get user', { userId, error: error.message });
  throw new AppError('User not found', 404);
}

// Use custom error classes
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
  }
}
```

#### Async/Await
```javascript
// Prefer async/await over promises
const getUser = async (userId) => {
  try {
    const user = await User.findById(userId);
    return user;
  } catch (error) {
    throw new Error(`Failed to get user: ${error.message}`);
  }
};

// Handle multiple async operations
const getUserWithUsage = async (userId) => {
  const [user, usage] = await Promise.all([
    User.findById(userId),
    UsageService.getUserUsage(userId)
  ]);
  
  return { user, usage };
};
```

### Documentation

#### JSDoc Comments
```javascript
/**
 * Create a new user account
 * @param {Object} userData - User data object
 * @param {string} userData.username - Username (3-50 characters)
 * @param {string} userData.email - Email address
 * @param {string} userData.password - Password (minimum 8 characters)
 * @param {string} [userData.role='student'] - User role
 * @returns {Promise<Object>} Created user object
 * @throws {ValidationError} When validation fails
 * @throws {ConflictError} When username/email already exists
 * 
 * @example
 * const user = await createUser({
 *   username: 'john.doe',
 *   email: 'john@university.ac.uk',
 *   password: 'SecurePass123!',
 *   role: 'student'
 * });
 */
const createUser = async (userData) => {
  // Implementation...
};
```

## 🔍 Code Review Process

### Submitting Pull Requests

1. **Ensure tests pass**
   ```bash
   npm test
   npm run lint
   ```

2. **Update documentation** if needed

3. **Create pull request** with:
   - Clear title and description
   - Link to related issues
   - Screenshots for UI changes
   - Test results

4. **Request review** from maintainers

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added and passing
- [ ] No merge conflicts
```

### Review Criteria

**Code Quality:**
- Follows coding standards
- Proper error handling
- Adequate test coverage
- Clear, readable code

**Security:**
- No security vulnerabilities
- Input validation
- Proper authentication/authorization
- Sensitive data protection

**Performance:**
- Efficient algorithms
- Database query optimization
- Memory usage considerations
- Network request optimization

## 🏗️ Architecture Guidelines

### Project Structure
```
src/
├── controllers/    # Route handlers
├── services/      # Business logic
├── models/        # Data models
├── middleware/    # Express middleware
├── utils/         # Utility functions
├── config/        # Configuration files
├── validators/    # Input validation
└── routes/        # Route definitions

docs/              # Documentation
tests/             # Test files
scripts/           # Build and deployment scripts
```

### Design Patterns

#### Service Layer Pattern
```javascript
// controllers/userController.js
const UserService = require('../services/UserService');

const createUser = async (req, res, next) => {
  try {
    const user = await UserService.createUser(req.body);
    res.status(201).json({
      success: true,
      data: user
    });
  } catch (error) {
    next(error);
  }
};

// services/UserService.js
class UserService {
  static async createUser(userData) {
    // Validation
    const validatedData = await UserValidator.validate(userData);
    
    // Business logic
    const hashedPassword = await bcrypt.hash(validatedData.password, 12);
    
    // Database operation
    const user = await User.create({
      ...validatedData,
      password: hashedPassword
    });
    
    return user;
  }
}
```

#### Repository Pattern
```javascript
// repositories/UserRepository.js
class UserRepository {
  static async findById(id) {
    return await User.findByPk(id);
  }
  
  static async findByUsername(username) {
    return await User.findOne({ where: { username } });
  }
  
  static async create(userData) {
    return await User.create(userData);
  }
}
```

## 🐛 Bug Reports

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Test with latest version**
3. **Check documentation** for known limitations
4. **Reproduce the bug** consistently

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug.

## Steps to Reproduce
1. Step one
2. Step two
3. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g. Ubuntu 20.04]
- Node.js version: [e.g. 16.14.0]
- npm version: [e.g. 8.3.1]
- App version: [e.g. 1.2.3]

## Additional Context
- Error logs
- Screenshots
- Configuration details
```

## 💡 Feature Requests

### Before Requesting

1. **Check existing issues** and roadmap
2. **Consider alternatives** and workarounds
3. **Think about implementation** complexity

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature.

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other solutions you've considered.

## Additional Context
- Mockups or diagrams
- Related issues
- Implementation ideas
```

## 📚 Documentation Guidelines

### Writing Documentation

1. **Clear and concise** language
2. **Step-by-step instructions**
3. **Code examples** where applicable
4. **Screenshots** for UI elements
5. **Cross-references** to related documentation

### Documentation Types

- **API Documentation**: Complete endpoint documentation
- **User Guides**: How-to guides for end users
- **Developer Guides**: Technical implementation details
- **Troubleshooting**: Common issues and solutions

## 🏷️ Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature or request |
| `documentation` | Improvements or additions to documentation |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention is needed |
| `question` | Further information is requested |
| `wontfix` | This will not be worked on |
| `duplicate` | This issue or pull request already exists |
| `priority:high` | High priority issue |
| `priority:low` | Low priority issue |

## 👥 Community Guidelines

### Code of Conduct

- **Be respectful** and inclusive
- **Be constructive** in feedback
- **Be patient** with new contributors
- **Focus on the code**, not the person
- **Help others learn** and grow

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: security@ncuk.ac.uk for security issues

## 🎯 Roadmap

### Current Priorities

1. **Performance optimization**
2. **Enhanced security features**
3. **Mobile app development**
4. **API v2 development**
5. **Multi-tenancy support**

### How to Get Involved

1. **Check open issues** for areas needing help
2. **Join discussions** on proposed features
3. **Review pull requests** from other contributors
4. **Improve documentation** and examples
5. **Share your ideas** for the project

## 📞 Getting Help

If you need help with contributing:

1. **Check documentation** first
2. **Search existing issues** and discussions
3. **Ask in GitHub Discussions**
4. **Contact maintainers** if needed

## 🙏 Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **Annual contributor awards**

Thank you for contributing to the WiFi Capping System! 🚀

---

**Last Updated**: August 2025  
**Version**: 1.0