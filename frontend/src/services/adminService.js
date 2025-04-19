import axios from 'axios';
import { API_BASE_URL } from '../config';

const adminService = {
  getDashboardStats: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/admin/dashboard/stats/`);
      return response;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch dashboard statistics' };
    }
  },

  getRecentFeedback: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/admin/dashboard/recent-feedback/`);
      return response;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch recent feedback' };
    }
  },

  getFeedbackDetails: async (feedbackId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/admin/feedback/${feedbackId}/`);
      return response;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch feedback details' };
    }
  },

  updateFeedbackStatus: async (feedbackId, status) => {
    try {
      const response = await axios.patch(
        `${API_BASE_URL}/api/admin/feedback/${feedbackId}/`,
        { status }
      );
      return response;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to update feedback status' };
    }
  },

  getDepartmentStats: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/admin/dashboard/department-stats/`);
      return response;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch department statistics' };
    }
  },

  getCategoryStats: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/admin/dashboard/category-stats/`);
      return response;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch category statistics' };
    }
  },

  getFeedbackTrends: async (days = 7) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/admin/dashboard/feedback-trends/?days=${days}`
      );
      return response;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch feedback trends' };
    }
  }
};

export default adminService; 