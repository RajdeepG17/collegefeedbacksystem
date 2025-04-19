// src/pages/admin/AdminDashboard.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Table, Badge } from 'react-bootstrap';
import { Doughnut, Bar } from 'react-chartjs-2';
import { feedbackAPI } from '../../utils/api';

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const data = await feedbackAPI.getDashboardData();
        setDashboardData(data);
      } catch (err) {
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);
  
  // Chart data and utility functions
  
  if (loading) {
    return <div className="text-center p-5">Loading dashboard data...</div>;
  }
  
  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Admin Dashboard</h1>
        <Button as={Link} to="/admin/feedback" variant="primary">
          View All Feedback
        </Button>
      </div>
      
      {/* Admin dashboard content */}
      {/* Status cards, charts, tables */}
    </Container>
  );
};

export default AdminDashboard;