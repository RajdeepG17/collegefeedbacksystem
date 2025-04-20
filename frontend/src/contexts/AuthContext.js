import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import authService from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  const [error, setError] = useState('');

  // Set up axios interceptor for authentication
  useEffect(() => {
    // Set up interceptor to handle 401 Unauthorized errors
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        // If error is 401 and we have a refresh token, try to refresh
        if (error.response && error.response.status === 401) {
          try {
            // Only try to refresh if we're authenticated
            if (isAuthenticated) {
              // Try to refresh token
              await authService.refreshToken();
              
              // Retry the original request with new token
              const config = error.config;
              config.headers['Authorization'] = `Bearer ${localStorage.getItem('token')}`;
              return axios(config);
            } else {
              // Not authenticated, just logout
              logout();
            }
          } catch (refreshError) {
            // If refresh fails, logout
            console.error('Token refresh failed:', refreshError);
            logout();
          }
        }
        return Promise.reject(error);
      }
    );

    // Load user on initial mount
    loadUser();

    return () => {
      // Clean up interceptor on unmount
      axios.interceptors.response.eject(interceptor);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const clearError = () => {
    setError('');
  };

  const loadUser = async () => {
    setAuthLoading(true);
    try {
      if (authService.isAuthenticated()) {
        const user = await authService.getCurrentUser();
        if (user) {
          setCurrentUser(user);
          setIsAuthenticated(true);
        } else {
          // If we got no user but no error, clear token
          authService.logout();
        }
      }
    } catch (error) {
      console.error('Load user error:', error);
      authService.logout();
    } finally {
      setAuthLoading(false);
    }
  };

  const login = async (email, password) => {
    setLoading(true);
    clearError();
    
    try {
      const { user, token } = await authService.login(email, password);
      
      console.log('Login successful, token:', token ? 'Present' : 'Missing', 'User:', user);
      
      setCurrentUser(user);
      setIsAuthenticated(true);
      return user;
    } catch (error) {
      console.error('Login context error:', error);
      
      if (error.response) {
        // Server responded with an error status code
        if (error.response.data && error.response.data.detail) {
          setError(error.response.data.detail);
        } else if (error.response.data && error.response.data.non_field_errors) {
          setError(error.response.data.non_field_errors[0]);
        } else {
          setError('Invalid credentials. Please try again.');
        }
      } else if (error.request) {
        // Request was made but no response received
        setError('Network error. Please check your connection.');
      } else {
        // Something else happened
        setError('An error occurred. Please try again.');
      }
      
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    clearError();
    
    try {
      return await authService.register(userData);
    } catch (error) {
      console.error('Registration error:', error);
      
      // Special case: if we get an "already exists" error, but the user can log in,
      // then treat this as a successful registration
      if (error.response?.data?.email && 
          error.response.data.email[0].includes('already exists')) {
        
        try {
          // Try to login with the credentials to see if the user was actually created
          const loginResult = await authService.login(userData.email, userData.password);
          if (loginResult) {
            // User can log in, so registration was actually successful
            return {
              user: loginResult.user,
              message: "Registration completed successfully!"
            };
          }
        } catch (loginError) {
          console.log('Login check after registration failed');
          // If login fails, continue with the error handling below
        }
      }
      
      if (error.response) {
        // Handle various error formats from Django
        const errorData = error.response.data;
        
        if (errorData.email) {
          setError(`Email: ${errorData.email[0]}`);
        } else if (errorData.password) {
          setError(`Password: ${errorData.password[0]}`);
        } else if (errorData.non_field_errors) {
          setError(errorData.non_field_errors[0]);
        } else {
          setError('Registration failed. Please check your information.');
        }
      } else if (error.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('An error occurred. Please try again.');
      }
      
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    setCurrentUser(null);
    setIsAuthenticated(false);
  };

  const updateProfile = async (userData) => {
    setLoading(true);
    clearError();
    
    try {
      // Use the API_URL directly since authService doesn't have updateProfile yet
      const response = await axios.patch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000/api'}/users/me/`, userData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setCurrentUser(response.data);
      return response.data;
    } catch (error) {
      console.error('Update profile error:', error);
      
      if (error.response && error.response.data) {
        const errorData = error.response.data;
        // Create a readable error message from the error object
        const errorMessage = Object.entries(errorData)
          .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
          .join('; ');
        setError(errorMessage);
      } else {
        setError('Failed to update profile. Please try again.');
      }
      
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    currentUser,
    isAuthenticated,
    loading,
    authLoading,
    error,
    clearError,
    login,
    register,
    logout,
    updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext; 