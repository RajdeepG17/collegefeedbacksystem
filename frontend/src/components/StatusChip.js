import React from 'react';
import { Chip } from '@mui/material';
import {
  Feedback as FeedbackIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

const StatusChip = ({ status }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'in_progress':
        return 'info';
      case 'resolved':
        return 'success';
      case 'closed':
        return 'default';
      case 'rejected':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'pending':
        return <WarningIcon />;
      case 'in_progress':
        return <FeedbackIcon />;
      case 'resolved':
        return <CheckCircleIcon />;
      case 'rejected':
        return <ErrorIcon />;
      default:
        return null;
    }
  };

  return (
    <Chip
      icon={getStatusIcon()}
      label={status.replace('_', ' ').toUpperCase()}
      color={getStatusColor()}
      size="small"
    />
  );
};

export default StatusChip; 