import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Navbar from './Navbar';

describe('Navbar Component', () => {
  const renderNavbar = (isAuthenticated = false) => {
    return render(
      <BrowserRouter>
        <Navbar isAuthenticated={isAuthenticated} />
      </BrowserRouter>
    );
  };

  test('renders navigation links for unauthenticated users', () => {
    renderNavbar(false);
    
    expect(screen.getByText(/home/i)).toBeInTheDocument();
    expect(screen.getByText(/login/i)).toBeInTheDocument();
    expect(screen.getByText(/register/i)).toBeInTheDocument();
    expect(screen.queryByText(/dashboard/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/logout/i)).not.toBeInTheDocument();
  });

  test('renders navigation links for authenticated users', () => {
    renderNavbar(true);
    
    expect(screen.getByText(/home/i)).toBeInTheDocument();
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/logout/i)).toBeInTheDocument();
    expect(screen.queryByText(/login/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/register/i)).not.toBeInTheDocument();
  });

  test('handles logout when authenticated', () => {
    const mockLogout = jest.fn();
    render(
      <BrowserRouter>
        <Navbar isAuthenticated={true} onLogout={mockLogout} />
      </BrowserRouter>
    );

    fireEvent.click(screen.getByText(/logout/i));
    expect(mockLogout).toHaveBeenCalled();
  });

  test('applies active class to current route', () => {
    renderNavbar(true);
    
    const homeLink = screen.getByText(/home/i);
    expect(homeLink).toHaveClass('active');
  });
}); 