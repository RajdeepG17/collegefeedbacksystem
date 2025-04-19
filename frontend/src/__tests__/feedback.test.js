import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import { FeedbackProvider } from '../contexts/FeedbackContext';
import FeedbackForm from '../components/feedback/FeedbackForm';
import FeedbackList from '../pages/feedback/FeedbackList';

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

describe('Feedback Functionality', () => {
  test('renders feedback form', () => {
    renderWithProviders(<FeedbackForm onSubmit={() => {}} />);
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
  });

  test('validates feedback form inputs', async () => {
    renderWithProviders(<FeedbackForm onSubmit={() => {}} />);
    
    fireEvent.click(screen.getByRole('button', { name: /submit feedback/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
      expect(screen.getByText(/description is required/i)).toBeInTheDocument();
      expect(screen.getByText(/category is required/i)).toBeInTheDocument();
      expect(screen.getByText(/priority is required/i)).toBeInTheDocument();
    });
  });

  test('submits feedback successfully', async () => {
    const mockSubmit = jest.fn();
    renderWithProviders(<FeedbackForm onSubmit={mockSubmit} />);
    
    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'Test Feedback' }
    });
    fireEvent.change(screen.getByLabelText(/description/i), {
      target: { value: 'This is a test feedback description' }
    });
    fireEvent.change(screen.getByLabelText(/category/i), {
      target: { value: '1' }
    });
    fireEvent.change(screen.getByLabelText(/priority/i), {
      target: { value: 'medium' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /submit feedback/i }));
    
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        title: 'Test Feedback',
        description: 'This is a test feedback description',
        category: '1',
        priority: 'medium'
      });
    });
  });

  test('displays feedback list', async () => {
    renderWithProviders(<FeedbackList />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Feedback')).toBeInTheDocument();
      expect(screen.getByText('This is a test feedback')).toBeInTheDocument();
    });
  });

  test('handles file upload', async () => {
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    renderWithProviders(<FeedbackForm onSubmit={() => {}} />);
    
    const fileInput = screen.getByLabelText(/attachment/i);
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(fileInput.files[0]).toBe(file);
    });
  });
}); 