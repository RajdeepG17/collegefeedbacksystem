import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip,
  Button,
} from '@mui/material';
import {
  Feedback as FeedbackIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useFeedback } from '../context/FeedbackContext';

// Debug component to help identify context issues
const ContextDebug = () => {
  const contextValue = useFeedback();
  
  console.log('FeedbackContext value:', contextValue);
  
  return null; // This component doesn't render anything
};

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

const Dashboard = () => {
  // Add ContextDebug before accessing the hook values
  return (
    <>
      <ContextDebug />
      <DashboardContent />
    </>
  );
};

const DashboardContent = () => {
  const { stats, loading, error, fetchDashboardStats } = useFeedback();
  const [localError, setLocalError] = useState('');

  useEffect(() => {
    handleFetchStats();
  }, []);

  const handleFetchStats = async () => {
    try {
      setLocalError('');
      await fetchDashboardStats();
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setLocalError('Unable to load dashboard data. Please try again.');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  const displayError = error || localError;
  
  if (displayError) {
    return (
      <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" minHeight="60vh" gap={2}>
        <Typography color="error">{displayError}</Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<RefreshIcon />}
          onClick={handleFetchStats}
        >
          Retry
        </Button>
      </Box>
    );
  }

  // Safely access stats with default empty values
  const statusCounts = stats?.status_counts || {};
  const categoryCounts = stats?.category_counts || [];
  const recentFeedback = stats?.recent || [];
  const urgentFeedback = stats?.urgent || [];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Button 
          variant="outlined" 
          startIcon={<RefreshIcon />}
          onClick={handleFetchStats}
        >
          Refresh
        </Button>
      </Box>
      
      <Grid container spacing={3}>
        {/* Status Summary */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Feedback Status
            </Typography>
            {Object.keys(statusCounts).length > 0 ? (
              <Grid container spacing={2}>
                {Object.entries(statusCounts).map(([status, count]) => (
                  <Grid item xs={6} key={status}>
                    <Card>
                      <CardContent>
                        <Typography variant="h4" component="div">
                          {count}
                        </Typography>
                        <StatusChip status={status} />
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Typography variant="body1" color="text.secondary">
                No status data available
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* Category Summary */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Feedback by Category
            </Typography>
            {categoryCounts.length > 0 ? (
              <List>
                {categoryCounts.map((category) => (
                  <ListItem key={category.category__name || 'unknown'}>
                    <ListItemText
                      primary={category.category__name || 'Uncategorized'}
                      secondary={`${category.count} feedbacks`}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body1" color="text.secondary">
                No category data available
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* Recent Feedback */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Feedback
            </Typography>
            {recentFeedback.length > 0 ? (
              <List>
                {recentFeedback.map((feedback) => (
                  <ListItem key={feedback.id}>
                    <ListItemText
                      primary={feedback.title}
                      secondary={
                        <Box component="span" sx={{ display: 'flex', gap: 1 }}>
                          <StatusChip status={feedback.status} />
                          <Typography variant="body2" color="text.secondary">
                            {new Date(feedback.created_at).toLocaleDateString()}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body1" color="text.secondary">
                No recent feedback available
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* Urgent Feedback */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Urgent Feedback
            </Typography>
            {urgentFeedback.length > 0 ? (
              <List>
                {urgentFeedback.map((feedback) => (
                  <ListItem key={feedback.id}>
                    <ListItemText
                      primary={feedback.title}
                      secondary={
                        <Box component="span" sx={{ display: 'flex', gap: 1 }}>
                          <StatusChip status={feedback.status} />
                          <Typography variant="body2" color="text.secondary">
                            {new Date(feedback.created_at).toLocaleDateString()}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body1" color="text.secondary">
                No urgent feedback available
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 