import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  TextField, 
  Button, 
  Container, 
  Typography, 
  Box, 
  Alert, 
  Snackbar, 
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    role: 'student',
    student_id: '',
    department: 'PGDCA',
    year_of_study: 1,
    phone_number: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [localError, setLocalError] = useState('');
  const [showError, setShowError] = useState(false);
  const [formErrors, setFormErrors] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    student_id: '',
    department: '',
    year_of_study: '',
    phone_number: ''
  });
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const validateForm = () => {
    let isValid = true;
    const errors = {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      firstName: '',
      lastName: '',
      student_id: '',
      department: '',
      year_of_study: '',
      phone_number: ''
    };

    // Username is automatically set from email, so no need to validate separately

    // Email validation
    if (!formData.email) {
      errors.email = 'Email is required';
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
      isValid = false;
    }

    // First name validation
    if (!formData.firstName) {
      errors.firstName = 'First name is required';
      isValid = false;
    }

    // Last name validation
    if (!formData.lastName) {
      errors.lastName = 'Last name is required';
      isValid = false;
    }

    // Password validation
    if (!formData.password) {
      errors.password = 'Password is required';
      isValid = false;
    } else if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
      isValid = false;
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
      isValid = false;
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
      isValid = false;
    }

    // Student ID validation if role is student
    if (formData.role === 'student' && !formData.student_id) {
      errors.student_id = 'Student ID is required';
      isValid = false;
    }

    setFormErrors(errors);
    return isValid;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // Clear errors for this field when user types
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: '',
      });
    }
    
    // Update form data
    const updatedData = {
      ...formData,
      [name]: value
    };
    
    // If email is changed, update username to match email
    if (name === 'email') {
      updatedData.username = value;
    }
    
    setFormData(updatedData);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');
    setIsLoading(true);

    if (!validateForm()) {
      setIsLoading(false);
      return;
    }

    try {
      // Pass the entire formData object instead of individual fields
      await register(formData);
      navigate('/login');
    } catch (error) {
      console.error('Registration failed:', error);
      
      // Handle backend validation errors
      if (error.response && error.response.data) {
        const errorData = error.response.data;
        
        // Update form errors with backend validation errors
        const newFormErrors = { ...formErrors };
        let hasSetError = false;
        
        // Map backend error fields to form fields
        const fieldMapping = {
          email: 'email',
          username: 'username',
          password: 'password',
          password2: 'confirmPassword',
          first_name: 'firstName',
          last_name: 'lastName',
          role: 'role',
          student_id: 'student_id',
          department: 'department',
          year_of_study: 'year_of_study',
          phone_number: 'phone_number'
        };
        
        // Process each error field
        Object.keys(errorData).forEach(field => {
          const formField = fieldMapping[field] || field;
          if (formField in newFormErrors) {
            newFormErrors[formField] = Array.isArray(errorData[field]) 
              ? errorData[field][0] 
              : errorData[field].toString();
            hasSetError = true;
          } else if (field === 'non_field_errors' || field === 'detail') {
            setLocalError(Array.isArray(errorData[field]) 
              ? errorData[field][0] 
              : errorData[field].toString());
            hasSetError = true;
          }
        });
        
        if (hasSetError) {
          setFormErrors(newFormErrors);
        } else {
          // If we couldn't map errors to specific fields, show generic error
          setLocalError('Registration failed. Please check your information and try again.');
        }
      } else {
        setLocalError('Registration failed. Please try again.');
      }
      
      setShowError(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseError = () => {
    setShowError(false);
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography component="h1" variant="h5">
          Create Account
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1, width: '100%' }}>
          <TextField
            margin="normal"
            required
            fullWidth
            label="Email Address"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            error={!!formErrors.email}
            helperText={formErrors.email}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            label="First Name"
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            error={!!formErrors.firstName}
            helperText={formErrors.firstName}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            label="Last Name"
            name="lastName"
            value={formData.lastName}
            onChange={handleChange}
            error={!!formErrors.lastName}
            helperText={formErrors.lastName}
          />
          
          <FormControl fullWidth margin="normal" required>
            <InputLabel id="role-label">Role</InputLabel>
            <Select
              labelId="role-label"
              name="role"
              value={formData.role}
              label="Role"
              onChange={handleChange}
            >
              <MenuItem value="student">Student</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
              <MenuItem value="super_admin">Super Admin</MenuItem>
            </Select>
          </FormControl>

          <TextField
            margin="normal"
            fullWidth
            label="Phone Number"
            name="phone_number"
            value={formData.phone_number}
            onChange={handleChange}
            error={!!formErrors.phone_number}
            helperText={formErrors.phone_number}
          />

          {formData.role === 'student' && (
            <>
              <TextField
                margin="normal"
                required
                fullWidth
                label="Student ID"
                name="student_id"
                value={formData.student_id}
                onChange={handleChange}
                error={!!formErrors.student_id}
                helperText={formErrors.student_id}
              />
              
              <FormControl fullWidth margin="normal" required>
                <InputLabel id="department-label">Department</InputLabel>
                <Select
                  labelId="department-label"
                  name="department"
                  value={formData.department}
                  label="Department"
                  onChange={handleChange}
                >
                  <MenuItem value="PGDCA">PGDCA</MenuItem>
                  <MenuItem value="Computer Science">Computer Science</MenuItem>
                  <MenuItem value="Engineering">Engineering</MenuItem>
                  <MenuItem value="Business">Business</MenuItem>
                </Select>
              </FormControl>
              
              <FormControl fullWidth margin="normal" required>
                <InputLabel id="year-label">Year of Study</InputLabel>
                <Select
                  labelId="year-label"
                  name="year_of_study"
                  value={formData.year_of_study}
                  label="Year of Study"
                  onChange={handleChange}
                >
                  <MenuItem value={1}>First Year</MenuItem>
                  <MenuItem value={2}>Second Year</MenuItem>
                  <MenuItem value={3}>Third Year</MenuItem>
                  <MenuItem value={4}>Fourth Year</MenuItem>
                </Select>
              </FormControl>
            </>
          )}
          
          <TextField
            margin="normal"
            required
            fullWidth
            label="Password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            error={!!formErrors.password}
            helperText={formErrors.password}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            label="Confirm Password"
            name="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={handleChange}
            error={!!formErrors.confirmPassword}
            helperText={formErrors.confirmPassword}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'SIGN UP'}
          </Button>
          
          <Box sx={{ mt: 1, textAlign: 'center' }}>
            <Typography variant="body2">
              Already have an account? <Button 
                variant="text" 
                size="small"
                onClick={() => navigate('/login')}
              >
                Sign In
              </Button>
            </Typography>
          </Box>
        </Box>
      </Box>
      
      <Snackbar open={showError} autoHideDuration={6000} onClose={handleCloseError}>
        <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
          {localError}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Register; 