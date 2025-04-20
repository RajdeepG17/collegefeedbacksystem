import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const Register = () => {
  const navigate = useNavigate();
  const { register, isAuthenticated, error: authError, clearError } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
    role: '', // Start with empty role to force selection
    user_type: '', // For backward compatibility
    phone_number: '',
    // Fields for students
    student_id: '',
    department: '',
    year_of_study: 1,
  });
  const [formErrors, setFormErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [localError, setLocalError] = useState('');
  const [success, setSuccess] = useState('');
  const [showStudentFields, setShowStudentFields] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }

    // Clear any previous auth errors when component mounts
    return () => {
      if (clearError) clearError();
    };
  }, [isAuthenticated, navigate, clearError]);

  // Toggle student fields when role changes
  useEffect(() => {
    setShowStudentFields(formData.role === 'student');
  }, [formData.role]);

  const validatePassword = (password) => {
    const errors = [];
    
    if (password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }
    
    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }
    
    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }
    
    if (!/[0-9]/.test(password)) {
      errors.push('Password must contain at least one number');
    }
    
    if (!/[^A-Za-z0-9]/.test(password)) {
      errors.push('Password must contain at least one special character');
    }
    
    return errors;
  };

  const validateForm = () => {
    const errors = {};
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
    }

    if (!formData.role) {
      errors.role = 'Role is required';
    }

    if (!formData.password) {
      errors.password = 'Password is required';
    } else {
      const passwordErrors = validatePassword(formData.password);
      if (passwordErrors.length > 0) {
        errors.password = passwordErrors.join('. ');
      }
    }

    if (!formData.password2) {
      errors.password2 = 'Please confirm your password';
    } else if (formData.password !== formData.password2) {
      errors.password2 = 'Passwords do not match';
    }

    if (!formData.first_name) {
      errors.first_name = 'First name is required';
    }

    if (!formData.last_name) {
      errors.last_name = 'Last name is required';
    }

    if (formData.role === 'student') {
      if (!formData.student_id) {
        errors.student_id = 'Student ID is required for student accounts';
      }
      
      if (!formData.department) {
        errors.department = 'Department is required for student accounts';
      }
      
      if (!formData.year_of_study) {
        errors.year_of_study = 'Year of study is required for student accounts';
      }
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    setFormData((prev) => ({
      ...prev,
      [name]: value,
      // Keep role and user_type in sync (role is the one expected by backend)
      ...(name === 'role' ? { user_type: value } : {}),
    }));

    // Clear error when user starts typing
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: '',
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');
    setSuccess('');

    if (!validateForm()) {
      return;
    }

    try {
      setIsSubmitting(true);
      console.log('Attempting registration with:', formData);
      
      // Create proper registration payload
      const userData = {
        email: formData.email,
        password: formData.password,
        password2: formData.password2,
        first_name: formData.first_name,
        last_name: formData.last_name,
        role: formData.role,
        user_type: formData.role, // Set user_type to match role
        phone_number: formData.phone_number || '',
      };
      
      // Add student-specific fields if role is student
      if (formData.role === 'student') {
        userData.student_id = formData.student_id;
        userData.department = formData.department;
        userData.year_of_study = parseInt(formData.year_of_study, 10);
      }
      
      try {
        const result = await register(userData);
        console.log('Registration result:', result);
        
        if (result && (result.access || result.user)) {
          setSuccess('Registration successful! Redirecting to login...');
          
          // Store credentials temporarily to help with first login
          sessionStorage.setItem('newUserEmail', formData.email);
          sessionStorage.setItem('newUserPassword', formData.password);
          
          // Redirect to login after successful registration
          setTimeout(() => {
            navigate('/login', { 
              state: { 
                newRegistration: true,
                email: formData.email
              } 
            });
          }, 2000);
        } else {
          // Something went wrong but no error was thrown
          console.warn('Registration returned unexpected result:', result);
          setLocalError('Registration completed but with an unexpected response. Please try logging in.');
        }
      } catch (regError) {
        console.error('Registration function error:', regError);
        
        // Check if the error is because user already exists but was actually created
        if (regError.response?.status === 400 && 
            regError.response?.data?.email?.[0]?.includes('already exists')) {
          
          // Try to check if the user can actually log in with these credentials
          try {
            const loginCheck = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000/api'}/auth/login/`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                email: formData.email,
                password: formData.password,
              }),
            });
            
            // If login is successful, the user was actually created
            if (loginCheck.ok) {
              setSuccess('Your account was successfully created! Redirecting to login...');
              
              // Store credentials temporarily to help with first login
              sessionStorage.setItem('newUserEmail', formData.email);
              sessionStorage.setItem('newUserPassword', formData.password);
              
              // Redirect to login after successful registration
              setTimeout(() => {
                navigate('/login', { 
                  state: { 
                    newRegistration: true,
                    email: formData.email
                  } 
                });
              }, 2000);
              return;
            }
          } catch (loginError) {
            console.error('Login check failed:', loginError);
          }
        }
        
        throw regError; // Rethrow to be caught by outer catch
      }
    } catch (err) {
      console.error('Registration error:', err);
      
      // Extract error details from API response
      let errorMessage = 'Registration failed. Please try again.';
      
      if (err.response?.data) {
        // Format error response into readable message
        const errorData = err.response.data;
        
        if (typeof errorData === 'object') {
          const errorMessages = [];
          
          Object.entries(errorData).forEach(([field, messages]) => {
            if (Array.isArray(messages)) {
              errorMessages.push(`${field}: ${messages.join(', ')}`);
            } else if (typeof messages === 'string') {
              errorMessages.push(`${field}: ${messages}`);
            }
          });
          
          if (errorMessages.length > 0) {
            errorMessage = errorMessages.join('\n');
          }
        } else if (typeof errorData === 'string') {
          errorMessage = errorData;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setLocalError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
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
            Create Account
        </Typography>

          {(authError || localError) && (
            <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
              {authError || localError}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mt: 2, width: '100%' }}>
              {success}
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
              id="first_name"
              label="First Name"
              name="first_name"
              autoComplete="given-name"
              value={formData.first_name}
              onChange={handleChange}
              error={!!formErrors.first_name}
              helperText={formErrors.first_name}
              disabled={isSubmitting}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              id="last_name"
              label="Last Name"
              name="last_name"
              autoComplete="family-name"
              value={formData.last_name}
              onChange={handleChange}
              error={!!formErrors.last_name}
              helperText={formErrors.last_name}
              disabled={isSubmitting}
            />
            
            <FormControl fullWidth margin="normal" required error={!!formErrors.role}>
              <InputLabel id="role-label">Role</InputLabel>
              <Select
                labelId="role-label"
                id="role"
                name="role"
                value={formData.role}
                label="Role"
                onChange={handleChange}
                disabled={isSubmitting}
              >
                <MenuItem value="student">Student</MenuItem>
                <MenuItem value="teacher">Teacher</MenuItem>
                <MenuItem value="admin">Admin</MenuItem>
              </Select>
              {formErrors.role && <FormHelperText>{formErrors.role}</FormHelperText>}
            </FormControl>
            
            <TextField
              margin="normal"
              fullWidth
              id="phone_number"
              label="Phone Number"
              name="phone_number"
              autoComplete="tel"
              value={formData.phone_number}
              onChange={handleChange}
              error={!!formErrors.phone_number}
              helperText={formErrors.phone_number}
              disabled={isSubmitting}
            />
            
            {/* Student-specific fields */}
            {showStudentFields && (
              <>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="student_id"
                  label="Student ID"
                  name="student_id"
                  value={formData.student_id}
                  onChange={handleChange}
                  error={!!formErrors.student_id}
                  helperText={formErrors.student_id}
                  disabled={isSubmitting}
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="department"
                  label="Department"
                  name="department"
                  value={formData.department}
                  onChange={handleChange}
                  error={!!formErrors.department}
                  helperText={formErrors.department}
                  disabled={isSubmitting}
                />
                <FormControl fullWidth margin="normal" required error={!!formErrors.year_of_study}>
                  <InputLabel id="year-label">Year of Study</InputLabel>
                  <Select
                    labelId="year-label"
                    id="year_of_study"
                    name="year_of_study"
                    value={formData.year_of_study}
                    label="Year of Study"
                    onChange={handleChange}
                    disabled={isSubmitting}
                  >
                    <MenuItem value={1}>First Year</MenuItem>
                    <MenuItem value={2}>Second Year</MenuItem>
                    <MenuItem value={3}>Third Year</MenuItem>
                    <MenuItem value={4}>Fourth Year</MenuItem>
                    <MenuItem value={5}>Fifth Year</MenuItem>
                  </Select>
                  {formErrors.year_of_study && <FormHelperText>{formErrors.year_of_study}</FormHelperText>}
                </FormControl>
              </>
            )}
            
              <TextField
              margin="normal"
                required
                fullWidth
                name="password"
              label="Password"
                type="password"
                id="password"
                autoComplete="new-password"
                value={formData.password}
                onChange={handleChange}
              error={!!formErrors.password}
              helperText={formErrors.password || "Password must be at least 8 characters with uppercase, lowercase, numbers and special characters"}
              disabled={isSubmitting}
              />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, mb: 1, display: 'block' }}>
              Password must be at least 8 characters with uppercase, lowercase, numbers and special characters
            </Typography>
              <TextField
              margin="normal"
                required
                fullWidth
              name="password2"
              label="Confirm Password"
                type="password"
              id="password2"
              autoComplete="new-password"
              value={formData.password2}
                onChange={handleChange}
              error={!!formErrors.password2}
              helperText={formErrors.password2}
              disabled={isSubmitting}
              />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
              disabled={isSubmitting}
          >
              {isSubmitting ? <CircularProgress size={24} /> : 'Sign Up'}
          </Button>

            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Typography variant="body2">
                Already have an account?{' '}
                <Link to="/login">
                  Sign In
              </Link>
              </Typography>
            </Box>
        </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Register; 