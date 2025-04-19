import React, { createContext, useState, useContext } from 'react';
import axios from 'axios';

const FeedbackContext = createContext();

export const useFeedback = () => useContext(FeedbackContext);

export const FeedbackProvider = ({ children }) => {
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchFeedbacks = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/feedback/');
      setFeedbacks(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch feedbacks');
    } finally {
      setLoading(false);
    }
  };

  const createFeedback = async (feedbackData) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/feedback/', feedbackData);
      setFeedbacks([...feedbacks, response.data]);
      setError(null);
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
      const response = await axios.patch(`/api/feedback/${id}/`, feedbackData);
      setFeedbacks(feedbacks.map(fb => fb.id === id ? response.data : fb));
      setError(null);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update feedback');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    feedbacks,
    loading,
    error,
    fetchFeedbacks,
    createFeedback,
    updateFeedback,
  };

  return (
    <FeedbackContext.Provider value={value}>
      {children}
    </FeedbackContext.Provider>
  );
}; 