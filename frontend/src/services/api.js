import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Add debugging for API configuration
console.log('API URL:', API_URL);

const api = axios.create({
    baseURL: API_URL,
    withCredentials: false,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
});

// Request interceptor for API calls
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        } else {
            // Add warning for authentication routes that should have a token
            const authRequiredPaths = [
                '/feedback/',
                '/auth/user/',
                '/auth/profile/',
                '/accounts/me/'
            ];
            
            // Check if current request path starts with any auth-required path
            const needsAuth = authRequiredPaths.some(path => 
                config.url.startsWith(path) && 
                !config.url.includes('login') && 
                !config.url.includes('register')
            );
            
            if (needsAuth) {
                console.warn('Authentication token missing for API call:', config.url);
            }
        }
        // Log the request for debugging
        console.log(`${config.method.toUpperCase()} ${config.baseURL}${config.url}`, config);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for API calls
api.interceptors.response.use(
    (response) => {
        // Log successful responses for debugging
        console.log('API Response:', response.status, response.data);
        return response;
    },
    async (error) => {
        const originalRequest = error.config;
        console.error('API Error:', error.response?.status, error.response?.data || error.message);

        // Handle 401 Unauthorized errors (token expired)
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            try {
                // Get refresh token
                const refreshToken = localStorage.getItem('refresh_token');
                if (!refreshToken) {
                    throw new Error('No refresh token available');
                }
                
                // Attempt to refresh token
                const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
                    refresh: refreshToken
                });
                
                // Update tokens
                const { access } = response.data;
                localStorage.setItem('token', access);
                
                // Update auth header and retry original request
                originalRequest.headers.Authorization = `Bearer ${access}`;
                return api(originalRequest);
            } catch (refreshError) {
                // Clear tokens on refresh failure
                localStorage.removeItem('token');
                localStorage.removeItem('refresh_token');
                
                // Redirect to login
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }
        
        return Promise.reject(error);
    }
);

// Auth endpoints
export const auth = {
    // Use a more reliable login approach
    login: async (data) => {
        console.log('Login request with:', data);
        
        // Define all possible login endpoints to try
        const endpoints = [
            { url: `${API_URL}/auth/login/`, name: 'API Auth Login' },
            { url: `${API_URL}/accounts/login/`, name: 'Accounts Login' }
        ];
        
        // Try each endpoint in sequence
        for (const endpoint of endpoints) {
            try {
                console.log(`Trying login endpoint: ${endpoint.name} (${endpoint.url})`);
                const response = await axios.post(endpoint.url, data, {
                    timeout: 8000  // 8 second timeout
                });
                console.log(`Login successful with ${endpoint.name}:`, response.data);
                return response;
            } catch (error) {
                // Only log and continue trying other endpoints if this was a connection error
                // or non-auth related error
                const status = error.response?.status;
                if (!status || status === 0 || status >= 500) {
                    console.error(`Login endpoint ${endpoint.name} connection error:`, error.message);
                    continue;
                } else if (status === 401 || status === 403) {
                    // Auth errors should be handled by caller
                    throw error;
                } else {
                    console.error(`Login endpoint ${endpoint.name} failed:`, 
                        error.response?.data || error.message);
                }
            }
        }
        
        // If we get here, all endpoints failed
        throw new Error('Server connection failed. Please check your internet connection and try again later.');
    },
    
    // Similar approach for register
    register: async (data) => {
        console.log('Registration request with:', data);
        
        // Ensure all required fields are present
        const formattedData = {
            email: data.email,
            username: data.username || data.email,
            password: data.password,
            password2: data.password2 || data.confirmPassword,
            first_name: data.firstName || data.first_name || '',
            last_name: data.lastName || data.last_name || '',
            role: data.role || 'student',
            user_type: data.userType || data.user_type || data.role || 'student'
        };
        
        // Include student-specific fields if present
        if (data.student_id) formattedData.student_id = data.student_id;
        if (data.department) formattedData.department = data.department;
        if (data.year_of_study) formattedData.year_of_study = data.year_of_study;
        if (data.phone_number) formattedData.phone_number = data.phone_number;
        
        console.log('Formatted registration data:', formattedData);
        
        // Define all possible registration endpoints
        const endpoints = [
            { url: `${API_URL}/auth/register/`, name: 'API Auth Register' },
            { url: `${API_URL}/accounts/register/`, name: 'Accounts Register' },
            { url: `${API_URL.replace('/api', '')}/accounts/register/`, name: 'Root Accounts Register' }
        ];
        
        // Try each endpoint in sequence
        for (const endpoint of endpoints) {
            try {
                console.log(`Trying registration endpoint: ${endpoint.name} (${endpoint.url})`);
                const response = await axios.post(endpoint.url, formattedData, {
                    timeout: 10000  // 10 second timeout for registration
                });
                console.log(`Registration successful with ${endpoint.name}:`, response.data);
                return response;
            } catch (error) {
                // Log validation errors for debugging
                if (error.response?.data) {
                    console.error(`Registration validation errors from ${endpoint.name}:`, error.response.data);
                }
                
                // Return validation errors immediately to be handled by the form
                if (error.response?.status === 400) {
                    throw error;
                }
                
                // Only try next endpoint if it was a connection or server error
                const status = error.response?.status;
                if (!status || status === 0 || status >= 500) {
                    console.error(`Registration endpoint ${endpoint.name} connection error:`, error.message);
                    continue;
                } else {
                    console.error(`Registration endpoint ${endpoint.name} failed:`, error.message);
                }
            }
        }
        
        // If we get here, all endpoints failed
        throw new Error('Server connection failed. Please check your internet connection and try again later.');
    },
    
    logout: (data) => api.post('/auth/logout/', data),
    refreshToken: (data) => api.post('/auth/token/refresh/', data),
    getUser: async () => {
        console.log('Getting current user profile');
        
        const errors = [];
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('No authentication token found');
        }
        
        // Define all possible user profile endpoints
        const endpoints = [
            { url: `${API_URL}/auth/user/`, name: 'Auth User' },
            { url: `${API_URL}/auth/profile/`, name: 'Auth Profile' },
            { url: `${API_URL}/accounts/me/`, name: 'Accounts Me' },
            { url: `${API_URL.replace('/api', '')}/accounts/me/`, name: 'Root Accounts Me' },
            { url: `${API_URL.replace('/api', '')}/api/auth/user/`, name: 'Full Path Auth User' }
        ];
        
        // Try each endpoint in sequence
        for (const endpoint of endpoints) {
            try {
                console.log(`Trying user profile endpoint: ${endpoint.name} (${endpoint.url})`);
                const response = await axios.get(endpoint.url, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                console.log(`User profile fetch successful with ${endpoint.name}:`, response.data);
                return response;
            } catch (error) {
                const errorMsg = error.response?.data || error.message || 'Unknown error';
                errors.push(`${endpoint.name} failed: ${JSON.stringify(errorMsg)}`);
                console.error(`User profile endpoint ${endpoint.name} failed:`, errorMsg);
                // Continue to next endpoint
            }
        }
        
        // If we get here, all endpoints failed
        const errorMessage = `All user profile endpoints failed:\n${errors.join('\n')}`;
        console.error(errorMessage);
        throw new Error(errorMessage);
    },
    updateProfile: (data) => api.patch('/auth/profile/', data),
};

// Feedback endpoints
export const feedback = {
    getAll: (params) => api.get('/feedback/feedbacks/', { params }),
    get: (id) => api.get(`/feedback/feedbacks/${id}/`),
    create: async (data) => {
        // Check if data is FormData (for file uploads)
        const isFormData = data instanceof FormData;
        
        // Create request config
        const config = {
            // Always add timeout
            timeout: 15000 // 15 seconds timeout to handle large file uploads
        };
        
        // Set appropriate headers for FormData
        if (isFormData) {
            config.headers = {
                'Content-Type': 'multipart/form-data',
            };
            
            // Log form data entries for debugging
            console.log('FormData entries:');
            for (let pair of data.entries()) {
                console.log(pair[0] + ': ' + (pair[1] instanceof File ? 
                    `File: ${pair[1].name} (${pair[1].size} bytes)` : 
                    pair[1]));
            }
        } else {
            console.log('Creating feedback with:', data);
        }
        
        try {
            // Make the API request with proper config
            // Use direct axios call to bypass interceptors for upload progress if needed
            let response;
            
            if (isFormData) {
                console.log('Using direct axios call for FormData submission');
                response = await axios.post(`${API_URL}/feedback/feedbacks/`, data, {
                    ...config,
                    headers: {
                        ...config.headers,
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
            } else {
                response = await api.post('/feedback/feedbacks/', data, config);
            }
            
            console.log('Feedback creation successful:', response.data);
            return response;
        } catch (error) {
            console.error('Feedback creation error:', 
                error.response?.status, 
                error.response?.statusText,
                error.response?.data);
                
            // Enhanced error logging for network errors
            if (!error.response) {
                console.error('Network error or CORS issue:', error.message);
            }
            
            throw error;
        }
    },
    update: (id, data) => api.put(`/feedback/feedbacks/${id}/`, data),
    delete: (id) => api.delete(`/feedback/feedbacks/${id}/`),
    getCategories: () => api.get('/feedback/categories/'),
    addComment: (feedbackId, data) => api.post(`/feedback/feedback/${feedbackId}/comments/`, data),
    getComments: (feedbackId) => api.get(`/feedback/feedback/${feedbackId}/comments/`),
    getDashboard: () => api.get('/feedback/feedbacks/dashboard/')
};

// Comments endpoints
export const comments = {
    list: (feedbackId) => api.get(`/feedback/${feedbackId}/comments/`),
    create: (feedbackId, data) => api.post(`/feedback/${feedbackId}/comments/`, data),
    update: (feedbackId, commentId, data) => api.patch(`/feedback/${feedbackId}/comments/${commentId}/`, data),
    delete: (feedbackId, commentId) => api.delete(`/feedback/${feedbackId}/comments/${commentId}/`),
};

export default api; 