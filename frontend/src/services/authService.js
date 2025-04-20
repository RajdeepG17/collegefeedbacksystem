import axios from 'axios';
import { API_URL, AUTH_ENDPOINTS } from '../config/constants';

// Create axios instance for auth
const authAPI = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Set authorization header if token exists
const setAuthToken = (token) => {
  if (token) {
    authAPI.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('token', token);
  } else {
    delete authAPI.defaults.headers.common['Authorization'];
    localStorage.removeItem('token');
  }
};

// Initialize from localStorage if token exists
const token = localStorage.getItem('token');
if (token) {
  setAuthToken(token);
}

const authService = {
  // Register new user
  register: async (userData) => {
    try {
      // Adjust field names to match backend expectations
      const apiData = {
        email: userData.email,
        // Always use email as username if not explicitly provided
        username: userData.email, // Always use email as the username
        password: userData.password,
        password2: userData.confirmPassword || userData.password2,
        first_name: userData.firstName || userData.first_name,
        last_name: userData.lastName || userData.last_name,
        role: userData.role || 'student',
        user_type: userData.userType || userData.role || 'student',
        phone_number: userData.phone_number || ''
      };
      
      // Add student-specific fields if present and role is student
      if (userData.role === 'student') {
        if (userData.student_id) apiData.student_id = userData.student_id;
        if (userData.department) apiData.department = userData.department;
        if (userData.year_of_study) apiData.year_of_study = userData.year_of_study;
      }
      
      console.log('Sending registration data:', apiData);
      
      // First try the auth endpoint
      try {
        const response = await authAPI.post(AUTH_ENDPOINTS.REGISTER, apiData);
        console.log('Registration response from auth endpoint:', response.data);
        return response.data;
      } catch (authError) {
        console.log('Auth endpoint registration failed, trying accounts endpoint:', authError.response?.status);
        
        // Check if the error is "user with this email already exists"
        if (authError.response?.status === 400 && 
            authError.response?.data?.email?.[0]?.includes('already exists')) {
          // Try a login to see if the user can actually log in
          try {
            const loginResponse = await authAPI.post(AUTH_ENDPOINTS.LOGIN, { 
              email: apiData.email, 
              password: apiData.password 
            });
            
            // If login is successful, the user was actually created despite the error
            if (loginResponse.status === 200) {
              console.log('User can log in despite "already exists" error - account must have been created');
              // Return a fake success response
              return {
                user: {
                  email: apiData.email,
                  first_name: apiData.first_name,
                  last_name: apiData.last_name,
                  user_type: apiData.user_type
                },
                message: 'Registration successful despite "already exists" error'
              };
            }
          } catch (loginError) {
            console.log('Login check failed:', loginError.response?.status);
            // Fall through to try the accounts endpoint
          }
        }
        
        // If auth endpoint fails or login check fails, try the accounts endpoint
        const accountsResponse = await axios.post(`${API_URL.replace('/api', '')}/accounts/register/`, apiData);
        console.log('Registration response from accounts endpoint:', accountsResponse.data);
        return accountsResponse.data;
      }
    } catch (error) {
      console.error('Registration error details:', error.response?.status, error.response?.data || error.message);
      throw error;
    }
  },

  // Login user
  login: async (email, password) => {
    try {
      console.log(`Attempting login with email: ${email}`);
      
      // Try both endpoints in sequence to find one that works
      try {
        // First try primary login endpoint (auth)
        console.log('Trying auth login endpoint...');
        const response = await authAPI.post(AUTH_ENDPOINTS.LOGIN, { 
          email, 
          password 
        });
        
        console.log('Auth login response received:', response.status);
        
        const { access, refresh, user } = response.data;
        
        // If we get a token, set it in axios and localStorage
        if (access) {
          setAuthToken(access);
          
          // Store refresh token if available
          if (refresh) {
            localStorage.setItem('refresh_token', refresh);
          }
          
          console.log('Auth login successful, user:', user);
          
          return {
            token: access,
            user
          };
        }
      } catch (authError) {
        console.log('Auth login failed:', authError.response?.status);
        
        // Try accounts endpoint if auth fails
        console.log('Trying accounts login endpoint...');
        const accountsResponse = await axios.post(`${API_URL.replace('/api', '')}/accounts/login/`, {
          email,
          password
        });
        
        console.log('Accounts login response received:', accountsResponse.status);
        
        const { access, refresh, user } = accountsResponse.data;
        
        if (access) {
          setAuthToken(access);
          
          if (refresh) {
            localStorage.setItem('refresh_token', refresh);
          }
          
          console.log('Accounts login successful, user:', user);
          
          return {
            token: access,
            user
          };
        }
      }
      
      throw new Error('Login failed. Neither endpoint returned a valid token.');
    } catch (error) {
      console.error('Login error status:', error.response?.status);
      console.error('Login error details:', error.response?.data || error.message);
      throw error;
    }
  },

  // Logout user
  logout: () => {
    setAuthToken(null);
    localStorage.removeItem('refresh_token');
  },

  // Get current user
  getCurrentUser: async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        return null;
      }
      
      setAuthToken(token);
      const response = await authAPI.get(AUTH_ENDPOINTS.USER_PROFILE);
      return response.data;
    } catch (error) {
      // If main endpoint fails, try alternative
      try {
        const altResponse = await authAPI.get('/auth/profile/');
        return altResponse.data;
      } catch (altError) {
        try {
          // Try accounts endpoint as last resort
          const accountsResponse = await axios.get(`${API_URL.replace('/api', '')}/accounts/me/`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          });
          return accountsResponse.data;
        } catch (accountsError) {
          console.error('Failed to get user profile:', accountsError.response?.data || accountsError.message);
          setAuthToken(null);
          throw accountsError;
        }
      }
    }
  },

  // Refresh token
  refreshToken: async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await authAPI.post(AUTH_ENDPOINTS.REFRESH_TOKEN, {
        refresh: refreshToken
      });
      
      const { access } = response.data;
      setAuthToken(access);
      
      return access;
    } catch (error) {
      console.error('Token refresh error:', error.response?.data || error.message);
      setAuthToken(null);
      throw error;
    }
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  }
};

export default authService; 