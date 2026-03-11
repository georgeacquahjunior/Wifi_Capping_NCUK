import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AdminLogin from '../pages/AdminLogin';

// Mock React Router
jest.mock('react-router-dom', () => ({
  Navigate: ({ to }: { to: string }) => <div data-testid="navigate">Navigate to {to}</div>,
  useLocation: () => ({ 
    state: null,
    pathname: '/login' 
  }),
}));

// Mock AuthContext
const mockLogin = jest.fn();
const mockAuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
};

jest.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    state: mockAuthState,
    login: mockLogin,
    logout: jest.fn(),
  }),
}));

describe('AdminLogin Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login form with username and password fields', () => {
    render(<AdminLogin />);
    
    expect(screen.getByText('WiFi Capping NCUK')).toBeInTheDocument();
    expect(screen.getByText('Admin Login')).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('shows demo credentials', () => {
    render(<AdminLogin />);
    
    expect(screen.getByText('Demo Credentials:')).toBeInTheDocument();
    expect(screen.getByText(/Username: admin/)).toBeInTheDocument();
    expect(screen.getByText(/Password: admin123/)).toBeInTheDocument();
  });

  test('shows error message for empty fields', async () => {
    render(<AdminLogin />);
    
    const signInButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(signInButton);

    await waitFor(() => {
      expect(screen.getByText('Please enter both username and password')).toBeInTheDocument();
    });
  });

  test('calls login function when form is submitted with valid data', async () => {
    mockLogin.mockResolvedValue(true);
    
    render(<AdminLogin />);
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const signInButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(usernameInput, { target: { value: 'admin' } });
    fireEvent.change(passwordInput, { target: { value: 'admin123' } });
    fireEvent.click(signInButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('admin', 'admin123');
    });
  });
});