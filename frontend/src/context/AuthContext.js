import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import api, { auth } from '../services/api';

// Initialize with default values to prevent null errors
const AuthContext = createContext({
  user: null,
  loading: true,
  error: null,
  login: () => {},
  register: () => {},
  logout: () => {},
  updateProfile: () => {},
  isAuthenticated: false,
  currentUser: null,
  authLoading: true,
  clearError: () => {}
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const clearError = () => {
    setError(null);
  };

  const fetchUser = async () => {
    try {
      console.log('Fetching current user data...');
      
      // Try using the auth service first
      try {
        const response = await auth.getUser();
        console.log('User data fetched successfully:', response.data);
        setUser(response.data);
        setIsAuthenticated(true);
      } catch (serviceError) {
        console.error('Error fetching user with service:', serviceError);
        
        // Fall back to direct axios call
        console.log('Trying direct axios call for user data...');
        const response = await axios.get('/api/auth/user/');
        console.log('User data fetched with direct call:', response.data);
        setUser(response.data);
        setIsAuthenticated(true);
      }
    } catch (err) {
      console.error('Failed to fetch user:', err);
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      console.log('Attempting login with:', { email });
      
      // Try auth service first
      let userData;
      try {
        const response = await auth.login({ email, password });
        const { token, user, access } = response.data;
        const authToken = token || access;
        
        if (authToken) {
          localStorage.setItem('token', authToken);
          axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
          setUser(user);
          setIsAuthenticated(true);
          userData = user;
        } else {
          throw new Error('No token received from server');
        }
      } catch (serviceError) {
        console.error('Login service error:', serviceError);
        
        // Fall back to direct axios call
        const response = await axios.post('/api/auth/login/', { email, password });
        const { token, user, access } = response.data;
        const authToken = token || access;
        
        if (authToken) {
          localStorage.setItem('token', authToken);
          axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
          setUser(user);
          setIsAuthenticated(true);
          userData = user;
        } else {
          throw new Error('No token received from server');
        }
      }
      
      return userData;
    } catch (err) {
      console.error('Login error:', err);
      setError(err.response?.data?.message || err.response?.data?.detail || 'Login failed');
      throw err;
    }
  };

  const register = async (userData) => {
    try {
      setError(null);
      console.log('Attempting registration with:', userData);
      
      // Try auth service first
      let registeredUser;
      try {
        const response = await auth.register(userData);
        const { token, user, access } = response.data;
        const authToken = token || access;
        
        if (authToken) {
          localStorage.setItem('token', authToken);
          axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
          setUser(user);
          setIsAuthenticated(true);
          registeredUser = user;
        }
      } catch (serviceError) {
        console.error('Registration service error:', serviceError);
        
        // Fall back to direct axios call
        const response = await axios.post('/api/auth/register/', userData);
        const { token, user, access } = response.data;
        const authToken = token || access;
        
        if (authToken) {
          localStorage.setItem('token', authToken);
          axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
          setUser(user);
          setIsAuthenticated(true);
          registeredUser = user;
        }
      }
      
      return registeredUser;
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.response?.data?.message || err.response?.data?.detail || 'Registration failed');
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    setIsAuthenticated(false);
  };

  const updateProfile = async (profileData) => {
    try {
      setError(null);
      console.log('Updating profile with:', profileData);
      
      let updatedUser;
      try {
        // Try auth service first
        const response = await auth.updateProfile(profileData);
        setUser(response.data);
        updatedUser = response.data;
      } catch (serviceError) {
        console.error('Update profile service error:', serviceError);
        
        // Fall back to direct axios call
        const response = await axios.put('/api/auth/profile/', profileData);
        setUser(response.data);
        updatedUser = response.data;
      }
      
      return updatedUser;
    } catch (err) {
      console.error('Profile update error:', err);
      setError(err.response?.data?.message || err.response?.data?.detail || 'Profile update failed');
      throw err;
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    updateProfile,
    isAuthenticated,
    currentUser: user, // Alias for compatibility
    authLoading: loading, // Alias for compatibility
    clearError
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 