import React from 'react';
import { render } from '@testing-library/react';
import LoadingSpinner from './LoadingSpinner';

describe('LoadingSpinner Component', () => {
  it('renders with default size', () => {
    const { container } = render(<LoadingSpinner />);
    const spinner = container.querySelector('.spinner');
    expect(spinner).toBeInTheDocument();
  });

  it('applies correct size class', () => {
    const sizes = ['small', 'medium', 'large'];
    sizes.forEach((size) => {
      const { container, unmount } = render(<LoadingSpinner size={size} />);
      const spinner = container.querySelector('.spinner');
      expect(spinner).toHaveClass(`spinner-${size}`);
      unmount();
    });
  });
}); 