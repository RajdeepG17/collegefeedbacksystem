// src/pages/FeedbackDetail.js
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Container, Row, Col, Card, Badge, Button, Alert, Form, ListGroup } from 'react-bootstrap';
import { feedbackAPI } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

const FeedbackDetail = () => {
  const { id } = useParams();
  const [feedback, setFeedback] = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [commentText, setCommentText] = useState('');
  
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const isAdminRoute = location.pathname.startsWith('/admin');

  // Add this function inside your FeedbackDetail component
const getStatusBadgeVariant = (status) => {
  switch (status) {
    case 'pending': return 'warning';
    case 'in_progress': return 'info';
    case 'resolved': return 'success';
    case 'closed': return 'secondary';
    case 'rejected': return 'danger';
    default: return 'primary';
  }
};
  useEffect(() => {
    // Fetch feedback details, comments, history
  }, [id]);
  
  // Functions for adding comments, resolving feedback, etc.
  const handleSubmit = async () => {
    // After successful submission
    navigate('/feedback');
  };

  <Link to="/feedback">View Feedback</Link>

  if (loading) {
    return <div className="text-center p-5">Loading feedback details...</div>;
  }
  
  return (
    <Container>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>
          Feedback #{feedback?.id}
          <Badge className="ms-2" bg={getStatusBadgeVariant(feedback?.status)}>
            {feedback?.status.toUpperCase()}
          </Badge>
        </h1>
        <Button variant="outline-primary" onClick={() => navigate(-1)}>
          Back
        </Button>
      </div>
      
      <Row>
        <Col md={8}>
          {/* Feedback details card */}
          
          {/* Comments section */}
        </Col>
        <Col md={4}>
          {/* Status management (admin only) */}
          
          {/* Submitter info */}
          
          {/* History section */}
        </Col>
      </Row>
    </Container>
  );
};

export default FeedbackDetail;