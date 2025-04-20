import React, { createContext, useState, useContext } from 'react';
import api, { feedback } from '../services/api';

// Initialize with an empty object instead of null to prevent destructuring errors
const FeedbackContext = createContext({
  feedbacks: [],
  loading: false,
  error: null,
  stats: {
    status_counts: {},
    category_counts: [],
    recent: [],
    urgent: []
  },
  fetchFeedbacks: () => {},
  fetchFeedback: () => {},
  createFeedback: () => {},
  updateFeedback: () => {},
  deleteFeedback: () => {},
  addComment: () => {},
  fetchDashboardStats: () => {}
});

export const useFeedback = () => useContext(FeedbackContext);

export const FeedbackProvider = ({ children }) => {
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    status_counts: {},
    category_counts: [],
    recent: [],
    urgent: []
  });

  const fetchFeedbacks = async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/feedback/feedbacks/', { params });
      setFeedbacks(response.data);
    } catch (err) {
      console.error('Error fetching feedbacks:', err);
      setError(err.response?.data?.message || 'Failed to fetch feedbacks');
    } finally {
      setLoading(false);
    }
  };

  const fetchFeedback = async (id) => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`/feedback/feedbacks/${id}/`);
      return response.data;
    } catch (err) {
      console.error('Error fetching feedback:', err);
      setError(err.response?.data?.message || 'Failed to fetch feedback');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const createFeedback = async (feedbackData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.post('/feedback/feedbacks/', feedbackData);
      setFeedbacks(prev => [response.data, ...prev]);
      return response.data;
    } catch (err) {
      console.error('Error creating feedback:', err);
      setError(err.response?.data?.message || 'Failed to create feedback');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateFeedback = async (id, feedbackData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.put(`/feedback/feedbacks/${id}/`, feedbackData);
      setFeedbacks(prev => prev.map(f => f.id === id ? response.data : f));
      return response.data;
    } catch (err) {
      console.error('Error updating feedback:', err);
      setError(err.response?.data?.message || 'Failed to update feedback');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteFeedback = async (id) => {
    try {
      setLoading(true);
      setError(null);
      await api.delete(`/feedback/feedbacks/${id}/`);
      setFeedbacks(prev => prev.filter(f => f.id !== id));
    } catch (err) {
      console.error('Error deleting feedback:', err);
      setError(err.response?.data?.message || 'Failed to delete feedback');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const addComment = async (feedbackId, commentData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.post(`/feedback/feedback/${feedbackId}/comments/`, commentData);
      setFeedbacks(prev => prev.map(f => {
        if (f.id === feedbackId) {
          return {
            ...f,
            comments: [...(f.comments || []), response.data]
          };
        }
        return f;
      }));
      return response.data;
    } catch (err) {
      console.error('Error adding comment:', err);
      setError(err.response?.data?.message || 'Failed to add comment');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching dashboard stats...');

      // Try different dashboard API endpoints
      let response;
      
      try {
        // Try first using the feedback service
        console.log('Trying feedback.getDashboard()');
        response = await feedback.getDashboard();
      } catch (dashboardError) {
        console.error('Error with feedback.getDashboard():', dashboardError);
        
        // Fall back to directly calling the API
        console.log('Trying direct API call to /feedback/feedbacks/dashboard/');
        response = await api.get('/feedback/feedbacks/dashboard/');
      }
      
      console.log('Dashboard stats response:', response.data);
      setStats(response.data);
      return response.data;
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
      setError(err.response?.data?.message || 'Failed to fetch dashboard stats');
      // Stats are already initialized with empty values in useState
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    feedbacks,
    loading,
    error,
    stats,
    fetchFeedbacks,
    fetchFeedback,
    createFeedback,
    updateFeedback,
    deleteFeedback,
    addComment,
    fetchDashboardStats,
  };

  return (
    <FeedbackContext.Provider value={value}>
      {children}
    </FeedbackContext.Provider>
  );
}; 