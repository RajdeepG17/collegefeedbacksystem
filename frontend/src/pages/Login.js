import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Paper,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const Login = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { login, error: authError, clearError, isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [formErrors, setFormErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [localError, setLocalError] = useState('');
  
  // Check for redirects
  const from = location.state?.from?.pathname || '/dashboard';
  const isNewRegistration = location.state?.newRegistration;

  // Set up form with credentials from registration if available
  useEffect(() => {
    // Check if coming from registration and session storage has credentials
    const newUserEmail = sessionStorage.getItem('newUserEmail');
    const newUserPassword = sessionStorage.getItem('newUserPassword');
    
    if (isNewRegistration && newUserEmail && newUserPassword) {
      console.log('New registration detected, auto-filling credentials');
      setFormData({
        email: newUserEmail,
        password: newUserPassword
      });
      
      // Clear stored credentials after using them
      sessionStorage.removeItem('newUserEmail');
      sessionStorage.removeItem('newUserPassword');
      
      // Auto-submit the form if we have the credentials
      const timer = setTimeout(() => {
        console.log('Auto-submitting login after registration');
        handleLogin(newUserEmail, newUserPassword);
      }, 500);
      
      return () => clearTimeout(timer);
    } else if (location.state?.email) {
      // If email was passed via state but no auto-login
      setFormData(prev => ({
        ...prev,
        email: location.state.email
      }));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state, isNewRegistration]);

  // Redirect if already authenticated
  useEffect(() => {
    console.log('Authentication state:', isAuthenticated);
    if (isAuthenticated) {
      console.log('User is authenticated, redirecting to:', from);
      navigate(from, { replace: true });
    }
    
    // Clear any previous auth errors when component mounts
    return () => {
      if (clearError) clearError();
    };
  }, [isAuthenticated, navigate, from, clearError]);

  const validateForm = () => {
    const errors = {};
    if (!formData.email) {
      errors.email = 'Email is required';
    }
    
    if (!formData.password) {
      errors.password = 'Password is required';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    
    // Clear error when user starts typing
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: '',
      });
    }
  };

  // Function to handle login with provided credentials
  const handleLogin = async (email, password) => {
    setLocalError('');
    
    try {
      setIsSubmitting(true);
      console.log('Attempting login with provided credentials');
      
      await login(email, password);
      
      // The redirect will happen in the useEffect when isAuthenticated changes
      console.log('Login successful');
    } catch (err) {
      console.error('Login error:', err);
      
      // Special handling for new registration login failures
      if (sessionStorage.getItem('newUserEmail') === email) {
        setLocalError("Your account was created successfully but we couldn't log you in automatically. Please try logging in manually.");
        
        // Clear stored credentials to prevent further auto-login attempts
        sessionStorage.removeItem('newUserEmail');
        sessionStorage.removeItem('newUserPassword');
      } else {
        setLocalError(err.message || 'Login failed. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');
    
    if (!validateForm()) {
      return;
    }
    
    await handleLogin(formData.email, formData.password);
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
            College Feedback System
          </Typography>
          
          <Typography component="h2" variant="h6">
            Sign In
          </Typography>
          
          {(authError || localError) && (
            <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
              {authError || localError}
            </Alert>
          )}
          
          {location.state?.newRegistration && (
            <Alert severity="success" sx={{ mt: 2, width: '100%' }}>
              Registration successful for {location.state.email}! {sessionStorage.getItem('newUserEmail') ? 'Attempting to log in automatically...' : 'Please log in with your credentials.'}
            </Alert>
          )}
          
          {location.state?.from && (
            <Alert severity="info" sx={{ mt: 2, width: '100%' }}>
              Please login to continue
            </Alert>
          )}
          
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1, width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={formData.email}
              onChange={handleChange}
              error={!!formErrors.email}
              helperText={formErrors.email}
              disabled={isSubmitting}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleChange}
              error={!!formErrors.password}
              helperText={formErrors.password}
              disabled={isSubmitting}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isSubmitting}
            >
              {isSubmitting ? <CircularProgress size={24} /> : 'Sign In'}
            </Button>
            
            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Typography variant="body2">
                Don't have an account?{' '}
                <Link to="/register">
                  Sign Up
                </Link>
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login; 