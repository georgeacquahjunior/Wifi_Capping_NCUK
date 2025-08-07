# WiFi Capping NCUK - Admin Dashboard

A React-based admin dashboard for managing WiFi bandwidth capping in educational institutions. This application provides secure admin authentication with protected routes for system management.

## Features

### 🔐 Authentication & Security
- **Admin Login Interface**: Secure login form with validation
- **Protected Routes**: Route-based access control using `ProtectedRoute` component
- **Session Persistence**: Maintains login state across browser sessions
- **Role-based Access**: Supports admin role verification

### 🎛️ Admin Dashboard
- **System Status Monitoring**: Real-time WiFi capping system status
- **User Management**: View connected users and active connections
- **Data Usage Tracking**: Monitor daily bandwidth consumption
- **Bandwidth Control**: Current bandwidth limit display
- **Quick Actions**: Easy access to system management functions
- **Activity Logs**: Recent system activity and events

### 💻 Technical Features
- **Responsive Design**: Mobile-friendly interface
- **TypeScript**: Full type safety and better development experience
- **React Router**: Client-side routing with protection
- **Context API**: Centralized authentication state management
- **Modern React**: Hooks and functional components
- **Testing**: Comprehensive test suite with Jest and React Testing Library

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git
   cd Wifi_Capping_NCUK
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000` to access the admin login interface.

### Demo Credentials
For testing purposes, use these credentials:
- **Username**: `admin`
- **Password**: `admin123`

## Available Scripts

- **`npm start`** - Runs the app in development mode
- **`npm test`** - Launches the test runner
- **`npm run build`** - Builds the app for production
- **`npm run eject`** - Ejects from Create React App (one-way operation)

## Project Structure

```
src/
├── components/
│   ├── ProtectedRoute.tsx      # Route protection component
│   └── ProtectedRoute.test.tsx # Tests for protected routes
├── contexts/
│   └── AuthContext.tsx         # Authentication context and logic
├── pages/
│   ├── AdminLogin.tsx          # Admin login page
│   ├── AdminLogin.css          # Login page styles
│   ├── AdminLogin.test.tsx     # Login page tests
│   ├── AdminDashboard.tsx      # Main admin dashboard
│   └── AdminDashboard.css      # Dashboard styles
├── types/
│   └── auth.ts                 # TypeScript type definitions
├── App.tsx                     # Main app component with routing
├── App.css                     # Global app styles
├── index.tsx                   # App entry point
└── index.css                   # Global styles
```

## Authentication Flow

1. **Unauthenticated Access**: Users are redirected to `/login` when accessing protected routes
2. **Login Process**: Users enter credentials on the admin login page
3. **Validation**: Credentials are validated (currently demo credentials)
4. **Session Creation**: Successful login creates a session stored in localStorage
5. **Protected Access**: Authenticated users can access admin dashboard
6. **Logout**: Users can logout, clearing the session and redirecting to login

## Component Details

### ProtectedRoute Component
- Checks authentication status before rendering protected content
- Redirects unauthenticated users to login page
- Supports role-based access control
- Shows loading state during authentication checks
- Displays access denied for insufficient permissions

### AuthContext
- Manages global authentication state
- Provides login/logout functionality
- Handles session persistence
- Uses React useReducer for state management
- Simulates API authentication (ready for backend integration)

### Admin Dashboard
- Displays system status and metrics
- Shows connected users and data usage
- Provides quick action buttons for system management
- Displays recent activity log
- Responsive grid layout

## Customization

### Adding New Protected Routes
```typescript
<Route
  path="/new-admin-page"
  element={
    <ProtectedRoute requiredRole="admin">
      <NewAdminPage />
    </ProtectedRoute>
  }
/>
```

### Integrating with Backend
Replace the demo authentication in `AuthContext.tsx` with actual API calls:

```typescript
const login = async (username: string, password: string): Promise<boolean> => {
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    
    if (response.ok) {
      const user = await response.json();
      localStorage.setItem('auth_user', JSON.stringify(user));
      dispatch({ type: 'LOGIN_SUCCESS', payload: user });
      return true;
    }
    return false;
  } catch (error) {
    return false;
  }
};
```

## Security Considerations

- Currently uses demo credentials for development
- Session data stored in localStorage (consider httpOnly cookies for production)
- No password encryption (implement proper authentication for production)
- No CSRF protection (add for production use)
- No rate limiting on login attempts (implement for production)

## Future Enhancements

- [ ] Backend API integration
- [ ] Real user management system
- [ ] Advanced bandwidth controls
- [ ] Detailed reporting and analytics
- [ ] Email notifications
- [ ] User registration system
- [ ] Multi-factor authentication
- [ ] Audit logging
- [ ] API documentation
- [ ] Docker containerization

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions, please open an issue on the GitHub repository.