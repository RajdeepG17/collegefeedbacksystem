import axios from 'axios';

const api = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for API calls
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for API calls
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Handle 401 Unauthorized errors
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                // Attempt to refresh token
                const response = await api.post('/auth/refresh-token');
                const { token } = response.data;
                localStorage.setItem('token', token);
                originalRequest.headers.Authorization = `Bearer ${token}`;
                return api(originalRequest);
            } catch (refreshError) {
                // If refresh fails, redirect to login
                localStorage.removeItem('token');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }
        return Promise.reject(error);
    }
);

// Auth endpoints
export const auth = {
    login: (data) => api.post('/auth/login/', data),
    register: (data) => api.post('/auth/register/', data),
    logout: () => api.post('/auth/logout/'),
    refreshToken: () => api.post('/auth/refresh-token/'),
};

// Feedback endpoints
export const feedback = {
    list: (params) => api.get('/feedback/', { params }),
    create: (data) => api.post('/feedback/', data),
    retrieve: (id) => api.get(`/feedback/${id}/`),
    update: (id, data) => api.patch(`/feedback/${id}/`, data),
    delete: (id) => api.delete(`/feedback/${id}/`),
    resolve: (id) => api.post(`/feedback/${id}/resolve/`),
    reopen: (id) => api.post(`/feedback/${id}/reopen/`),
    rate: (id, data) => api.post(`/feedback/${id}/rate/`, data),
    dashboard: () => api.get('/feedback/dashboard/'),
};

// Category endpoints
export const categories = {
    list: () => api.get('/categories/'),
    create: (data) => api.post('/categories/', data),
    update: (id, data) => api.patch(`/categories/${id}/`, data),
    delete: (id) => api.delete(`/categories/${id}/`),
};

// Comments endpoints
export const comments = {
    list: (feedbackId) => api.get(`/feedback/${feedbackId}/comments/`),
    create: (feedbackId, data) => api.post(`/feedback/${feedbackId}/comments/`, data),
    update: (feedbackId, commentId, data) => api.patch(`/feedback/${feedbackId}/comments/${commentId}/`, data),
    delete: (feedbackId, commentId) => api.delete(`/feedback/${feedbackId}/comments/${commentId}/`),
};

export default api; 