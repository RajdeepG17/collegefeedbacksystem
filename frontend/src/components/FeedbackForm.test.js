import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import FeedbackForm from './FeedbackForm';
import axios from 'axios';

// Mock axios
jest.mock('axios');

describe('FeedbackForm Component', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders all form fields', () => {
    render(<FeedbackForm onSubmit={mockOnSubmit} />);
    
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  });

  test('handles form submission successfully', async () => {
    const mockResponse = {
      data: {
        id: 1,
        title: 'Test Feedback',
        description: 'Test Description',
        category: 'general',
        status: 'pending'
      }
    };

    axios.post.mockResolvedValueOnce(mockResponse);

    render(<FeedbackForm onSubmit={mockOnSubmit} />);

    // Fill in the form
    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'Test Feedback' }
    });
    fireEvent.change(screen.getByLabelText(/description/i), {
      target: { value: 'Test Description' }
    });
    fireEvent.change(screen.getByLabelText(/category/i), {
      target: { value: 'general' }
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    // Check if axios was called with correct data
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/feedback'),
        {
          title: 'Test Feedback',
          description: 'Test Description',
          category: 'general'
        }
      );
    });

    // Check if onSubmit was called
    expect(mockOnSubmit).toHaveBeenCalledWith(mockResponse.data);
  });

  test('handles form validation', async () => {
    render(<FeedbackForm onSubmit={mockOnSubmit} />);

    // Try to submit empty form
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    // Check for validation messages
    expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    expect(screen.getByText(/description is required/i)).toBeInTheDocument();
    expect(screen.getByText(/category is required/i)).toBeInTheDocument();

    // Check that onSubmit was not called
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  test('handles form submission with error', async () => {
    const errorMessage = 'Failed to submit feedback';
    axios.post.mockRejectedValueOnce({
      response: {
        data: { message: errorMessage }
      }
    });

    render(<FeedbackForm onSubmit={mockOnSubmit} />);

    // Fill in the form
    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'Test Feedback' }
    });
    fireEvent.change(screen.getByLabelText(/description/i), {
      target: { value: 'Test Description' }
    });
    fireEvent.change(screen.getByLabelText(/category/i), {
      target: { value: 'general' }
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    // Check if error message is displayed
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });
}); 