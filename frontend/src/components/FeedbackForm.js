import React, { useState } from 'react';
import {
    Box,
    Button,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    FormControlLabel,
    Checkbox,
    Typography,
    Alert,
    CircularProgress
} from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { feedbackSchema } from '../validation/feedbackSchema';
import { feedback } from '../services/api';
import Loading from './Loading';

const FeedbackForm = ({ categories, onSubmitSuccess }) => {
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const formik = useFormik({
        initialValues: {
            title: '',
            description: '',
            category: '',
            priority: 'medium',
            is_anonymous: false,
            attachment: null
        },
        validationSchema: feedbackSchema,
        onSubmit: async (values, { resetForm }) => {
            try {
                setLoading(true);
                setError(null);
                
                const formData = new FormData();
                Object.keys(values).forEach(key => {
                    if (key === 'attachment' && values[key]) {
                        formData.append(key, values[key]);
                    } else if (values[key] !== null) {
                        formData.append(key, values[key]);
                    }
                });
                
                await feedback.create(formData);
                resetForm();
                if (onSubmitSuccess) {
                    onSubmitSuccess();
                }
            } catch (err) {
                setError(err.response?.data?.detail || 'An error occurred while submitting feedback');
            } finally {
                setLoading(false);
            }
        }
    });
    
    const handleFileChange = (event) => {
        const file = event.currentTarget.files[0];
        formik.setFieldValue('attachment', file);
    };
    
    return (
        <Box component="form" onSubmit={formik.handleSubmit} sx={{ mt: 3 }}>
            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}
            
            <TextField
                fullWidth
                id="title"
                name="title"
                label="Title"
                value={formik.values.title}
                onChange={formik.handleChange}
                error={formik.touched.title && Boolean(formik.errors.title)}
                helperText={formik.touched.title && formik.errors.title}
                sx={{ mb: 2 }}
            />
            
            <TextField
                fullWidth
                id="description"
                name="description"
                label="Description"
                multiline
                rows={4}
                value={formik.values.description}
                onChange={formik.handleChange}
                error={formik.touched.description && Boolean(formik.errors.description)}
                helperText={formik.touched.description && formik.errors.description}
                sx={{ mb: 2 }}
            />
            
            <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel id="category-label">Category</InputLabel>
                <Select
                    labelId="category-label"
                    id="category"
                    name="category"
                    value={formik.values.category}
                    onChange={formik.handleChange}
                    error={formik.touched.category && Boolean(formik.errors.category)}
                >
                    {categories.map((category) => (
                        <MenuItem key={category.id} value={category.id}>
                            {category.name}
                        </MenuItem>
                    ))}
                </Select>
                {formik.touched.category && formik.errors.category && (
                    <Typography color="error" variant="caption">
                        {formik.errors.category}
                    </Typography>
                )}
            </FormControl>
            
            <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel id="priority-label">Priority</InputLabel>
                <Select
                    labelId="priority-label"
                    id="priority"
                    name="priority"
                    value={formik.values.priority}
                    onChange={formik.handleChange}
                    error={formik.touched.priority && Boolean(formik.errors.priority)}
                >
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
                {formik.touched.priority && formik.errors.priority && (
                    <Typography color="error" variant="caption">
                        {formik.errors.priority}
                    </Typography>
                )}
            </FormControl>
            
            <FormControlLabel
                control={
                    <Checkbox
                        id="is_anonymous"
                        name="is_anonymous"
                        checked={formik.values.is_anonymous}
                        onChange={formik.handleChange}
                    />
                }
                label="Submit anonymously"
                sx={{ mb: 2 }}
            />
            
            <Box sx={{ mb: 2 }}>
                <input
                    accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                    style={{ display: 'none' }}
                    id="attachment"
                    name="attachment"
                    type="file"
                    onChange={handleFileChange}
                />
                <label htmlFor="attachment">
                    <Button
                        variant="outlined"
                        component="span"
                        sx={{ mr: 1 }}
                    >
                        Attach File
                    </Button>
                </label>
                {formik.values.attachment && (
                    <Typography variant="body2" color="text.secondary">
                        {formik.values.attachment.name}
                    </Typography>
                )}
                {formik.touched.attachment && formik.errors.attachment && (
                    <Typography color="error" variant="caption">
                        {formik.errors.attachment}
                    </Typography>
                )}
            </Box>
            
            <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={loading}
                fullWidth
            >
                {loading ? <CircularProgress size={24} /> : 'Submit Feedback'}
            </Button>
        </Box>
    );
};

export default FeedbackForm; 