import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import Login from '../pages/auth/Login';
import Register from '../pages/auth/Register';

const renderWithAuth = (component) => {
  return render(
    <MemoryRouter>
      <AuthProvider>
        {component}
      </AuthProvider>
    </MemoryRouter>
  );
};

describe('Authentication Flow', () => {
  test('renders login form', () => {
    renderWithAuth(<Login />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('handles successful login', async () => {
    renderWithAuth(<Login />);
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'test123' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(window.location.pathname).toBe('/');
    });
  });

  test('handles failed login', async () => {
    renderWithAuth(<Login />);
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'wrong@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrong' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });

  test('renders registration form', () => {
    renderWithAuth(<Register />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
  });

  test('handles successful registration', async () => {
    renderWithAuth(<Register />);
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'new@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'newuser' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'test123' }
    });
    fireEvent.change(screen.getByLabelText(/confirm password/i), {
      target: { value: 'test123' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /register/i }));
    
    await waitFor(() => {
      expect(window.location.pathname).toBe('/login');
    });
  });
}); 