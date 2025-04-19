import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { auth } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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

    const fetchUser = async () => {
        try {
            const response = await auth.getUser();
            console.log('Fetched user:', response.data);
            setUser(response.data);
        } catch (err) {
            console.error('Error fetching user:', err);
            localStorage.removeItem('token');
            localStorage.removeItem('refresh_token');
            delete axios.defaults.headers.common['Authorization'];
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        try {
            console.log('Attempting login with:', email);
            const response = await auth.login({ email, password });
            console.log('Login response:', response.data);
            
            const { access, refresh } = response.data;
            localStorage.setItem('token', access);
            localStorage.setItem('refresh_token', refresh);
            
            axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
            await fetchUser();
            
            console.log('Login successful, user:', user);
            return response.data;
        } catch (err) {
            console.error('Login error:', err);
            const errorMessage = err.response?.data?.message || err.response?.data?.detail || 'Login failed';
            setError(errorMessage);
            throw new Error(errorMessage);
        }
    };

    const register = async (userData) => {
        try {
            const response = await auth.register(userData);
            return response.data;
        } catch (err) {
            const errorMessage = err.response?.data?.message || 'Registration failed';
            setError(errorMessage);
            throw new Error(errorMessage);
        }
    };

    const logout = async () => {
        try {
            await auth.logout();
        } catch (err) {
            console.error('Logout error:', err);
        } finally {
            localStorage.removeItem('token');
            localStorage.removeItem('refresh_token');
            delete axios.defaults.headers.common['Authorization'];
            setUser(null);
        }
    };

    const updateProfile = async (profileData) => {
        try {
            const response = await auth.updateProfile(profileData);
            setUser(response.data);
            return response.data;
        } catch (err) {
            const errorMessage = err.response?.data?.message || 'Profile update failed';
            setError(errorMessage);
            throw new Error(errorMessage);
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
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
}; 