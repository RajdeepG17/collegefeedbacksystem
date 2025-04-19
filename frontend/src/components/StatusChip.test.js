import React from 'react';
import { render, screen } from '@testing-library/react';
import StatusChip from './StatusChip';

describe('StatusChip Component', () => {
  const statuses = ['pending', 'in_progress', 'resolved', 'rejected'];
  const colorMap = {
    pending: 'Warning',
    in_progress: 'Info',
    resolved: 'Success',
    rejected: 'Error',
  };

  it('renders with different statuses', () => {
    statuses.forEach((status) => {
      const { unmount } = render(<StatusChip status={status} />);
      const chip = screen.getByText(status.toUpperCase());
      expect(chip).toBeInTheDocument();
      expect(chip.closest('.MuiChip-root')).toHaveClass(`MuiChip-color${colorMap[status]}`);
      unmount();
    });
  });

  it('applies custom className when provided', () => {
    const customClass = 'custom-class';
    render(<StatusChip status="pending" className={customClass} />);
    const chip = screen.getByText('PENDING');
    expect(chip.closest('.MuiChip-root')).toHaveClass(customClass);
  });
}); 