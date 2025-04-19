import React from 'react';
import { render, screen } from '@testing-library/react';
import ErrorBoundary from './ErrorBoundary';

// A component that throws an error
const ErrorComponent = () => {
  throw new Error('Test error');
};

describe('ErrorBoundary Component', () => {
  test('renders children when there is no error', () => {
    const { getByText } = render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    );
    expect(getByText('Test content')).toBeInTheDocument();
  });

  test('renders error message when child component throws error', () => {
    // Suppress console error for this test
    const originalError = console.error;
    console.error = jest.fn();

    render(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    );

    // Check for error message in heading
    expect(screen.getByRole('heading', { name: /something went wrong/i })).toBeInTheDocument();
    // Check for error details
    expect(screen.getByText(/test error/i)).toBeInTheDocument();

    // Restore console.error
    console.error = originalError;
  });
}); 