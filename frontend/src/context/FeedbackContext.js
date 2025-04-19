import React, { createContext, useState, useContext } from 'react';
import axios from 'axios';

const FeedbackContext = createContext(null);

export const useFeedback = () => useContext(FeedbackContext);

export const FeedbackProvider = ({ children }) => {
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  const fetchFeedbacks = async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get('/api/feedback/', { params });
      setFeedbacks(response.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch feedbacks');
    } finally {
      setLoading(false);
    }
  };

  const fetchFeedback = async (id) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`/api/feedback/${id}/`);
      return response.data;
    } catch (err) {
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
      const response = await axios.post('/api/feedback/', feedbackData);
      setFeedbacks(prev => [response.data, ...prev]);
      return response.data;
    } catch (err) {
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
      const response = await axios.put(`/api/feedback/${id}/`, feedbackData);
      setFeedbacks(prev => prev.map(f => f.id === id ? response.data : f));
      return response.data;
    } catch (err) {
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
      await axios.delete(`/api/feedback/${id}/`);
      setFeedbacks(prev => prev.filter(f => f.id !== id));
    } catch (err) {
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
      const response = await axios.post(`/api/feedback/${feedbackId}/comments/`, commentData);
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
      const response = await axios.get('/api/feedback/dashboard/');
      setStats(response.data);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch dashboard stats');
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