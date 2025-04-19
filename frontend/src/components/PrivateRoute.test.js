import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PrivateRoute from './PrivateRoute';

// Mock components for testing
const PublicComponent = () => <div>Public Component</div>;
const PrivateComponent = () => <div>Private Component</div>;

describe('PrivateRoute Component', () => {
  test('redirects to login when not authenticated', () => {
    // Clear any existing token
    localStorage.clear();

    render(
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<PublicComponent />} />
          <Route
            path="/private"
            element={
              <PrivateRoute>
                <PrivateComponent />
              </PrivateRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    );

    // Should redirect to login page
    expect(window.location.pathname).toBe('/login');
  });

  test('renders private component when authenticated', () => {
    // Set authentication token
    localStorage.setItem('token', 'test-token');

    render(
      <BrowserRouter>
        <Routes>
          <Route
            path="/private"
            element={
              <PrivateRoute>
                <PrivateComponent />
              </PrivateRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    );

    expect(screen.getByText('Private Component')).toBeInTheDocument();
  });
}); 