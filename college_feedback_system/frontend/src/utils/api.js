// src/utils/api.js
import axios from 'axios';

// Set up axios defaults
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.withCredentials = true;

// Base API URLs
const BASE_URL = '/api';
const ACCOUNTS_URL = `${BASE_URL}/accounts`;
const FEEDBACK_URL = `${BASE_URL}/feedback`;

// Error handler
const handleError = (error) => {
  console.error('API Error:', error);
  
  // Return standardized error object
  return {
    error: true,
    message: error.response?.data?.error || error.response?.data?.detail || error.message || 'An error occurred',
    status: error.response?.status,
    data: error.response?.data
  };
};

// Authentication API
export const authAPI = {
  login: async (email, password) => {
    try {
      const response = await axios.post(`${ACCOUNTS_URL}/login/`, { email, password });
      return response.data;
    } catch (error) {
      console.error('Login error details:', error);
      throw {
        message: error.response?.data?.error || error.message || 'Login failed',
        status: error.response?.status,
        data: error.response?.data
    };
  }
},
  
  register: async (userData) => {
    try {
      const response = await axios.post(`${ACCOUNTS_URL}/register/`, userData);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  logout: async () => {
    try {
      const response = await axios.post(`${ACCOUNTS_URL}/logout/`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  getCurrentUser: async () => {
    try {
      const response = await axios.get(`${ACCOUNTS_URL}/users/me/`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  updateProfile: async (userId, data) => {
    try {
      const response = await axios.patch(`${ACCOUNTS_URL}/users/${userId}/`, data);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  changePassword: async (passwordData) => {
    try {
      const response = await axios.post(`${ACCOUNTS_URL}/users/change_password/`, passwordData);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  }
};

// User API
export const userAPI = {
  getUsers: async () => {
    try {
      const response = await axios.get(`${ACCOUNTS_URL}/users/`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  getUser: async (userId) => {
    try {
      const response = await axios.get(`${ACCOUNTS_URL}/users/${userId}/`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  createUser: async (userData) => {
    try {
      const response = await axios.post(`${ACCOUNTS_URL}/users/`, userData);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  updateUser: async (userId, userData) => {
    try {
      const response = await axios.patch(`${ACCOUNTS_URL}/users/${userId}/`, userData);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  deleteUser: async (userId) => {
    try {
      const response = await axios.delete(`${ACCOUNTS_URL}/users/${userId}/`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  getAdmins: async () => {
    try {
      const response = await axios.get(`${ACCOUNTS_URL}/users/admins/`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  }
};

// Feedback API
export const feedbackAPI = {
  getCategories: async () => {
    try {
      const response = await axios.get(`${FEEDBACK_URL}/categories/`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  createCategory: async (data) => {
    try {
      const response = await axios.post(`${FEEDBACK_URL}/categories/`, data);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  updateCategory: async (categoryId, data) => {
    try {
      const response = await axios.patch(`${FEEDBACK_URL}/categories/${categoryId}/`, data);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  deleteCategory: async (categoryId) => {
    try {
      const response = await axios.delete(`${FEEDBACK_URL}/categories/${categoryId}/`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  getFeedbacks: async (params = {}) => {
    try {
      const response = await axios.get(`${FEEDBACK_URL}/feedback/`, { params });
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  getFeedback: async (feedbackId) => {
    try {
      const response = await axios.get(`${FEEDBACK_URL}/feedback/${feedbackId}/`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  createFeedback: async (data) => {
    try {
      // Handle file uploads with FormData
      let formData = null;
      if (data.attachment) {
        formData = new FormData();
        Object.keys(data).forEach(key => {
          if (key === 'attachment') {
            formData.append(key, data[key]);
          } else {
            formData.append(key, data[key]);
          }
        });
      }
      
      const response = await axios.post(
        `${FEEDBACK_URL}/feedback/`, 
        formData || data,
        formData ? { headers: { 'Content-Type': 'multipart/form-data' } } : {}
      );
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  updateFeedback: async (feedbackId, data) => {
    try {
      const response = await axios.patch(`${FEEDBACK_URL}/feedback/${feedbackId}/`, data);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  deleteFeedback: async (feedbackId) => {
    try {
      const response = await axios.delete(`${FEEDBACK_URL}/feedback/${feedbackId}/`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  resolveFeedback: async (feedbackId) => {
    try {
      const response = await axios.post(`${FEEDBACK_URL}/feedback/${feedbackId}/resolve/`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  reopenFeedback: async (feedbackId) => {
    try {
      const response = await axios.post(`${FEEDBACK_URL}/feedback/${feedbackId}/reopen/`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  rateFeedback: async (feedbackId, rating) => {
    try {
      const response = await axios.post(`${FEEDBACK_URL}/feedback/${feedbackId}/rate/`, { rating });
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  getDashboardData: async () => {
    try {
      const response = await axios.get(`${FEEDBACK_URL}/feedback/dashboard/`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  // Comments
  getComments: async (feedbackId) => {
    try {
      const response = await axios.get(`${FEEDBACK_URL}/comments/`, { 
        params: { feedback_id: feedbackId } 
      });
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  createComment: async (data) => {
    try {
      // Handle file uploads with FormData
      let formData = null;
      if (data.attachment) {
        formData = new FormData();
        Object.keys(data).forEach(key => {
          if (key === 'attachment') {
            formData.append(key, data[key]);
          } else {
            formData.append(key, data[key]);
          }
        });
      }
      
      const response = await axios.post(
        `${FEEDBACK_URL}/comments/`, 
        formData || data,
        formData ? { headers: { 'Content-Type': 'multipart/form-data' } } : {}
      );
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
  
  // History
  getHistory: async (feedbackId) => {
    try {
      const response = await axios.get(`${FEEDBACK_URL}/history/`, { 
        params: { feedback_id: feedbackId } 
      });
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  }
};