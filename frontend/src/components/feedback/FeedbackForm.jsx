import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  Alert,
  CircularProgress,
  Chip,
  Grid,
  Paper,
  IconButton,
  FormControlLabel,
  Checkbox,
  FormHelperText
} from '@mui/material';
import { PhotoCamera, Delete } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { feedback } from '../../services/api';

// Debug helper function
const debugLog = (message, data) => {
  console.log(`DEBUG [${new Date().toISOString()}]: ${message}`, data || '');
};

const FeedbackForm = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    attachment: null,
    content: '',
    rating: 5
  });
  const [errors, setErrors] = useState({});
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [success, setSuccess] = useState(false);
  const [categories, setCategories] = useState([]);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    // Fetch categories when component mounts
    const fetchCategories = async () => {
      try {
        setLoadingCategories(true);
        debugLog('Fetching feedback categories...');
        
        // Try multiple approaches to fetch categories
        let categoriesData = [];
        let fetchError = null;
        
        // Approach 1: Using feedback service
        try {
          debugLog('Approach 1: Using feedback.getCategories()');
          const response = await feedback.getCategories();
          debugLog('Categories response from service:', response.data);
          
          if (response.data && Array.isArray(response.data)) {
            categoriesData = response.data;
            debugLog('Successfully fetched categories using service:', categoriesData);
          } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
            // Handle paginated response
            categoriesData = response.data.results;
            debugLog('Successfully fetched paginated categories:', categoriesData);
          }
        } catch (serviceError) {
          console.error('Error fetching categories with service:', serviceError);
          fetchError = serviceError;
          
          // Approach 2: Direct fetch with full URL
          try {
            console.log('Approach 2: Using direct fetch with absolute URL');
            const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
            const response = await fetch(`${baseUrl}/feedback/categories/`);
            
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Categories response from direct fetch:', data);
            
            if (Array.isArray(data)) {
              categoriesData = data;
            } else if (data && data.results && Array.isArray(data.results)) {
              categoriesData = data.results;
            }
            
            console.log('Successfully fetched categories using direct fetch:', categoriesData);
          } catch (fetchError) {
            console.error('Error with direct fetch:', fetchError);
            
            // Approach 3: Hardcoded fallback categories if everything fails
            console.log('Approach 3: Using hardcoded categories as fallback');
            categoriesData = [
              { id: 'academic', name: 'Academic' },
              { id: 'infrastructure', name: 'Infrastructure' },
              { id: 'administrative', name: 'Administrative' },
              { id: 'other', name: 'Other' }
            ];
            console.log('Using fallback categories:', categoriesData);
          }
        }
        
        // Set the categories regardless of which approach worked
        setCategories(categoriesData);
      } catch (err) {
        console.error('All category fetch methods failed:', err);
        // Use hardcoded fallback as last resort
        setCategories([
          { id: 'academic', name: 'Academic' },
          { id: 'infrastructure', name: 'Infrastructure' },
          { id: 'administrative', name: 'Administrative' },
          { id: 'other', name: 'Other' }
        ]);
      } finally {
        setLoadingCategories(false);
      }
    };

    fetchCategories();
  }, []);

  const validateForm = () => {
    const newErrors = {};
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }
    if (!formData.category) {
      newErrors.category = 'Category is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    
    // Set both description and content fields when description changes
    if (name === 'description') {
      setFormData({
        ...formData,
        description: value,
        content: value // Keep content and description in sync
      });
    } else {
      setFormData({
        ...formData,
        [name]: type === 'checkbox' ? checked : value
      });
    }
    
    // Clear error for this field
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
  };

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
      if (!allowedTypes.includes(selectedFile.type)) {
        setErrors({
          ...errors, 
          attachment: 'Only image files (jpg, jpeg, png, gif) are allowed'
        });
        return;
      }

      // Validate file size (10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setErrors({
          ...errors,
          attachment: 'File size must be less than 10MB'
        });
        return;
      }

      setFormData({
        ...formData,
        attachment: selectedFile
      });
      
      if (errors.attachment) {
        setErrors({
          ...errors,
          attachment: ''
        });
      }

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleRemoveFile = () => {
    setFormData({
      ...formData,
      attachment: null
    });
    setPreview(null);
    if (errors.attachment) {
      setErrors({
        ...errors,
        attachment: ''
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError('');
    debugLog('Submit button clicked, starting form validation');
    
    // Validate form
    if (!validateForm()) {
      debugLog('Form validation failed', errors);
      return;
    }
    
    setLoading(true);
    debugLog('Form validation passed, preparing data for submission');

    try {
      const formPayload = new FormData();
      
      // Map frontend fields to backend fields based on the updated serializer fields
      formPayload.append('title', formData.title);
      formPayload.append('content', formData.description);
      formPayload.append('category', formData.category);
      formPayload.append('rating', formData.rating || 5); // Default to 5 if not set
      
      // Add attachment if present
      if (formData.attachment) {
        debugLog('Adding attachment to form data', {
          name: formData.attachment.name,
          size: formData.attachment.size,
          type: formData.attachment.type
        });
        formPayload.append('attachment', formData.attachment);
      }

      // Log all form data fields for debugging
      const formDataLog = {};
      for (let [key, value] of formPayload.entries()) {
        formDataLog[key] = value instanceof File ? 
          `File: ${value.name} (${value.size} bytes)` : value;
      }
      debugLog('Submitting feedback with payload', formDataLog);
      
      try {
        debugLog('Sending API request to create feedback');
        const response = await feedback.create(formPayload);
        debugLog('Feedback creation successful', response.data);
        setSuccess(true);
        
        // Reset form after successful submission
        setFormData({
          title: '',
          description: '',
          category: '',
          attachment: null,
          content: '',
          rating: 5
        });
        setPreview(null);
        
        debugLog('Form reset, redirecting in 2 seconds');
        // Redirect after short delay
        setTimeout(() => {
          navigate('/feedback/list');
        }, 2000);
      } catch (submitError) {
        debugLog('Error submitting feedback', {
          status: submitError.response?.status,
          data: submitError.response?.data,
          message: submitError.message
        });
        throw submitError;
      }
      
    } catch (err) {
      console.error('Error submitting feedback:', err);
      debugLog('Setting error message for user', err.response?.data);
      
      // More detailed error message - display specific validation errors if available
      let errorMessage = 'Failed to submit feedback. Please try again.';
      
      if (err.response?.data) {
        if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        } else if (err.response.data.error) {
          errorMessage = err.response.data.error;
        } else if (err.response.data.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.response.data.message) {
          errorMessage = err.response.data.message;
        } else {
          // Check for validation errors in fields
          const fieldErrors = [];
          for (const field in err.response.data) {
            if (Array.isArray(err.response.data[field])) {
              fieldErrors.push(`${field}: ${err.response.data[field].join(', ')}`);
            }
          }
          
          if (fieldErrors.length > 0) {
            errorMessage = `Validation errors: ${fieldErrors.join('; ')}`;
          }
        }
      }
      
      setSubmitError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <Paper elevation={3} sx={{ p: 3, maxWidth: 800, mx: 'auto', mt: 4 }}>
        <Alert severity="success">
          Feedback submitted successfully! Redirecting...
        </Alert>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Submit Feedback
      </Typography>

      {submitError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {submitError}
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              label="Title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              error={!!errors.title}
              helperText={errors.title}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              multiline
              rows={4}
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              error={!!errors.description}
              helperText={errors.description}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth error={!!errors.category}>
              <InputLabel id="category-label">Category</InputLabel>
              <Select
                labelId="category-label"
                id="category"
                name="category"
                value={formData.category}
                label="Category"
                onChange={handleChange}
                disabled={loadingCategories}
              >
                {loadingCategories ? (
                  <MenuItem value="" disabled>Loading categories...</MenuItem>
                ) : categories && Array.isArray(categories) && categories.length > 0 ? (
                  categories.map((cat) => (
                    <MenuItem key={cat.id || cat._id} value={cat.id || cat._id}>
                      {cat.name}
                    </MenuItem>
                  ))
                ) : (
                  <MenuItem value="" disabled>No categories available</MenuItem>
                )}
              </Select>
              {errors.category && <FormHelperText>{errors.category}</FormHelperText>}
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Button
                variant="outlined"
                component="label"
                startIcon={<PhotoCamera />}
              >
                Upload Image
                <input
                  type="file"
                  hidden
                  accept="image/*"
                  onChange={handleFileChange}
                />
              </Button>
              {formData.attachment && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2">
                    {formData.attachment.name}
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={handleRemoveFile}
                    color="error"
                  >
                    <Delete />
                  </IconButton>
                </Box>
              )}
            </Box>
            {errors.attachment && (
              <FormHelperText error>{errors.attachment}</FormHelperText>
            )}
            {preview && (
              <Box sx={{ mt: 2 }}>
                <img
                  src={preview}
                  alt="Preview"
                  style={{ maxWidth: '100%', maxHeight: '200px' }}
                />
              </Box>
            )}
          </Grid>

          <Grid item xs={12}>
            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              disabled={loading}
              sx={{ mt: 2 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Submit Feedback'}
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};

export default FeedbackForm; 