// src/components/StatusBadge.js
import React from 'react';
import { Badge } from 'react-bootstrap';

const StatusBadge = ({ status }) => {
  const getVariant = (status) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'in_progress': return 'info';
      case 'resolved': return 'success';
      case 'closed': return 'secondary';
      case 'rejected': return 'danger';
      default: return 'primary';
    }
  };
  
  return (
    <Badge bg={getVariant(status)}>
      {status.replace(/_/g, ' ').toUpperCase()}
    </Badge>
  );
};

export default StatusBadge;