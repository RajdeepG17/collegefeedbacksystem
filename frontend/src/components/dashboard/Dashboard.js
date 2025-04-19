import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress,
} from '@mui/material';

const Dashboard = () => {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const userType = localStorage.getItem('user_type');

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await axios.get('/api/auth/profile/');
        setUserData(response.data);
      } catch (error) {
        console.error('Error fetching user data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="80vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography component="h1" variant="h4" gutterBottom>
              Welcome, {userData?.first_name}!
            </Typography>
            <Typography variant="subtitle1" gutterBottom>
              User Type: {userData?.user_type}
            </Typography>
            {userData?.department && (
              <Typography variant="subtitle1" gutterBottom>
                Department: {userData.department}
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* Add more dashboard widgets based on user type */}
        {userType === 'admin' && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
              <Typography component="h2" variant="h6" gutterBottom>
                Admin Controls
              </Typography>
              {/* Add admin-specific controls */}
            </Paper>
          </Grid>
        )}

        {userType === 'student' && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
              <Typography component="h2" variant="h6" gutterBottom>
                My Feedback
              </Typography>
              {/* Add student feedback components */}
            </Paper>
          </Grid>
        )}

        {(userType === 'faculty' || userType === 'staff') && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
              <Typography component="h2" variant="h6" gutterBottom>
                Department Feedback
              </Typography>
              {/* Add faculty/staff feedback components */}
            </Paper>
          </Grid>
        )}
      </Grid>
    </Container>
  );
};

export default Dashboard; 