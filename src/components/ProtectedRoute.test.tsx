import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProtectedRoute from '../components/ProtectedRoute';

// Mock React Router
jest.mock('react-router-dom', () => ({
  Navigate: ({ to }: { to: string }) => <div data-testid="navigate">Navigate to {to}</div>,
  useLocation: () => ({ pathname: '/admin' }),
}));

// Mock AuthContext
jest.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    state: {
      user: null,
      isAuthenticated: false,
      isLoading: false,
    },
  }),
}));

const MockComponent = () => <div>Protected Content</div>;

describe('ProtectedRoute Component', () => {
  test('renders component structure correctly', () => {
    render(
      <ProtectedRoute>
        <MockComponent />
      </ProtectedRoute>
    );

    // Component renders without errors
    expect(screen.getByTestId('navigate')).toBeInTheDocument();
    expect(screen.getByText('Navigate to /login')).toBeInTheDocument();
  });

  test('accepts required role prop', () => {
    render(
      <ProtectedRoute requiredRole="admin">
        <MockComponent />
      </ProtectedRoute>
    );

    // Component accepts props and renders without errors
    expect(screen.getByTestId('navigate')).toBeInTheDocument();
  });
});