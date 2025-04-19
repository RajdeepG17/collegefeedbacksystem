import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import { FeedbackProvider } from '../contexts/FeedbackContext';
import AdminDashboard from '../pages/admin/AdminDashboard';
import FeedbackManagement from '../pages/admin/FeedbackManagement';

const renderWithProviders = (component) => {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <FeedbackProvider>
          {component}
        </FeedbackProvider>
      </AuthProvider>
    </MemoryRouter>
  );
};

describe('Admin Functionality', () => {
  test('renders admin dashboard', async () => {
    renderWithProviders(<AdminDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
      expect(screen.getByText(/feedback statistics/i)).toBeInTheDocument();
    });
  });

  test('displays feedback management interface', async () => {
    renderWithProviders(<FeedbackManagement />);
    
    await waitFor(() => {
      expect(screen.getByText(/manage feedback/i)).toBeInTheDocument();
      expect(screen.getByText(/filter/i)).toBeInTheDocument();
      expect(screen.getByText(/status/i)).toBeInTheDocument();
    });
  });

  test('updates feedback status', async () => {
    renderWithProviders(<FeedbackManagement />);
    
    await waitFor(() => {
      const statusSelect = screen.getByLabelText(/status/i);
      fireEvent.change(statusSelect, { target: { value: 'in_progress' } });
      
      expect(screen.getByText(/in progress/i)).toBeInTheDocument();
    });
  });

  test('assigns feedback to admin', async () => {
    renderWithProviders(<FeedbackManagement />);
    
    await waitFor(() => {
      const assignSelect = screen.getByLabelText(/assign to/i);
      fireEvent.change(assignSelect, { target: { value: '2' } });
      
      expect(screen.getByText(/admin/i)).toBeInTheDocument();
    });
  });

  test('filters feedback by category', async () => {
    renderWithProviders(<FeedbackManagement />);
    
    await waitFor(() => {
      const categoryFilter = screen.getByLabelText(/category/i);
      fireEvent.change(categoryFilter, { target: { value: 'academic' } });
      
      expect(screen.getByText(/academic/i)).toBeInTheDocument();
    });
  });

  test('displays notification for new feedback', async () => {
    renderWithProviders(<AdminDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/new feedback submitted/i)).toBeInTheDocument();
    });
  });
}); 