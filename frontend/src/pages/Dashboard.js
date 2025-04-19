import React, { useEffect } from 'react';
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
} from '@mui/material';
import {
  Feedback as FeedbackIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useFeedback } from '../context/FeedbackContext';

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
  const { stats, loading, error, fetchDashboardStats } = useFeedback();

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        {/* Status Summary */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Feedback Status
            </Typography>
            <Grid container spacing={2}>
              {stats?.status_counts &&
                Object.entries(stats.status_counts).map(([status, count]) => (
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
          </Paper>
        </Grid>

        {/* Category Summary */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Feedback by Category
            </Typography>
            <List>
              {stats?.category_counts?.map((category) => (
                <ListItem key={category.category__name}>
                  <ListItemText
                    primary={category.category__name}
                    secondary={`${category.count} feedbacks`}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Recent Feedback */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Feedback
            </Typography>
            <List>
              {stats?.recent?.map((feedback) => (
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
          </Paper>
        </Grid>

        {/* Urgent Feedback */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Urgent Feedback
            </Typography>
            <List>
              {stats?.urgent?.map((feedback) => (
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
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 