import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from './Login';
import axios from 'axios';

// Mock axios
jest.mock('axios');

describe('Login Component', () => {
  const renderLogin = () => {
    return render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
  };

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('renders login form', () => {
    renderLogin();
    
    // Check if form elements are present
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('handles form submission successfully', async () => {
    const mockResponse = {
      data: {
        token: 'mock-token',
        user: {
          id: 1,
          email: 'test@example.com',
          role: 'student'
        }
      }
    };

    axios.post.mockResolvedValueOnce(mockResponse);

    renderLogin();

    // Fill in the form
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    // Check if axios was called with correct data
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/login'),
        {
          email: 'test@example.com',
          password: 'password123'
        }
      );
    });

    // Check if token was stored
    expect(localStorage.setItem).toHaveBeenCalledWith('token', 'mock-token');
  });

  test('handles form submission with error', async () => {
    const errorMessage = 'Invalid credentials';
    axios.post.mockRejectedValueOnce({
      response: {
        data: { message: errorMessage }
      }
    });

    renderLogin();

    // Fill in the form
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpassword' }
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    // Check if error message is displayed
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });
}); 