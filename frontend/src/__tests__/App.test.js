import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';
import { AuthProvider } from '../contexts/AuthContext';
import { FeedbackProvider } from '../contexts/FeedbackContext';

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = mockLocalStorage;

// Mock navigation
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderApp = (isAuthenticated = false) => {
    mockLocalStorage.getItem.mockImplementation((key) => {
      if (key === 'token') return isAuthenticated ? 'test-token' : null;
      if (key === 'user_type') return isAuthenticated ? 'student' : null;
      return null;
    });

    return render(
      <BrowserRouter>
        <AuthProvider>
          <FeedbackProvider>
            <App />
          </FeedbackProvider>
        </AuthProvider>
      </BrowserRouter>
    );
  };

  test('renders loading state initially', () => {
    renderApp();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('redirects to login when not authenticated', async () => {
    renderApp(false);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login', { replace: true });
    });
  });

  test('redirects to dashboard when authenticated', async () => {
    renderApp(true);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true });
    });
  });

  test('handles logout correctly', async () => {
    renderApp(true);
    
    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByText('College Feedback System')).toBeInTheDocument();
    });

    // Click logout button
    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);

    // Check localStorage calls
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('token');
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('refresh_token');
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('user_type');

    // Check navigation
    expect(window.location.href).toBe('http://localhost/login');
  });

  test('displays error message on logout failure', async () => {
    // Mock localStorage.removeItem to throw an error
    mockLocalStorage.removeItem.mockImplementation(() => {
      throw new Error('Storage error');
    });

    renderApp(true);
    
    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByText('College Feedback System')).toBeInTheDocument();
    });

    // Click logout button
    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);

    // Check error message
    await waitFor(() => {
      expect(screen.getByText('Error during logout. Please try again.')).toBeInTheDocument();
    });
  });

  test('renders navigation menu when authenticated', async () => {
    renderApp(true);
    
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Submit Feedback')).toBeInTheDocument();
      expect(screen.getByText('View Feedback')).toBeInTheDocument();
      expect(screen.getByText('Logout')).toBeInTheDocument();
    });
  });

  test('handles error boundary', async () => {
    // Mock a component to throw an error
    const ErrorComponent = () => {
      throw new Error('Test error');
    };

    const { container } = render(
      <BrowserRouter>
        <AuthProvider>
          <FeedbackProvider>
            <ErrorComponent />
          </FeedbackProvider>
        </AuthProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(container.querySelector('.MuiAlert-root')).toBeInTheDocument();
      expect(screen.getByText('Something went wrong. Please try refreshing the page.')).toBeInTheDocument();
    });
  });
}); 