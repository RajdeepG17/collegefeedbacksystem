// src/pages/NewFeedback.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Card, Form, Button, Alert } from 'react-bootstrap';
import { feedbackAPI } from '../utils/api';

const NewFeedback = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    priority: 'medium',
    is_anonymous: false,
    attachment: null
  });
  
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  
  useEffect(() => {
    // Fetch categories
    const fetchCategories = async () => {
      try {
        const response = await feedbackAPI.getCategories();
        setCategories(response);
        if (response.length > 0) {
          setFormData(prev => ({ ...prev, category: response[0].id }));
        }
      } catch (err) {
        setError('Failed to load categories');
      }
    };
    
    fetchCategories();
  }, []);
  
  const handleChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : 
              type === 'file' ? files[0] : 
              value
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    // Form validation
    // Submit feedback
  };
  
  return (
    <Container>
      <h1 className="mb-4">Submit New Feedback</h1>
      
      <Card>
        <Card.Body>
          {error && <Alert variant="danger">{error}</Alert>}
          
          <Form onSubmit={handleSubmit}>
            {/* Form fields for feedback submission */}
            <div className="d-grid gap-2 mt-4">
              <Button 
                variant="primary" 
                type="submit" 
                disabled={loading}
              >
                {loading ? 'Submitting...' : 'Submit Feedback'}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default NewFeedback;