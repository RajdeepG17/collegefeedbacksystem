import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import {
  CssBaseline,
  ThemeProvider,
  createTheme,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  CircularProgress,
  Snackbar,
  Alert,
} from '@mui/material';
import { Menu as MenuIcon } from '@mui/icons-material';
import { AuthProvider } from './contexts/AuthContext';
import { FeedbackProvider } from './contexts/FeedbackContext';

// Layouts
import MainLayout from './components/layouts/MainLayout';
import PrivateRoute from './components/PrivateRoute';

// Auth Pages
import Login from './pages/Login';
import Register from './pages/Register';

// Feedback Pages
import FeedbackList from './pages/FeedbackList';
import FeedbackDetail from './pages/FeedbackDetail';
import Dashboard from './pages/Dashboard';

// Other Pages
import Settings from './pages/Settings';
import Home from './pages/Home';
import Profile from './pages/Profile';

// Components
import FeedbackForm from './components/feedback/FeedbackForm';
import ProtectedRoute from './components/auth/ProtectedRoute';

const theme = createTheme();

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Alert severity="error">
            Something went wrong. Please try refreshing the page.
          </Alert>
        </Box>
      );
    }
    return this.props.children;
  }
}

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userType, setUserType] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const type = localStorage.getItem('user_type');
    setIsAuthenticated(!!token);
    setUserType(type);
    setLoading(false);

    // Cleanup function
    return () => {
      // Remove any event listeners or subscriptions here
    };
  }, []);

  const handleLogout = () => {
    try {
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_type');
      setIsAuthenticated(false);
      setUserType(null);
      window.location.href = '/login';
    } catch (err) {
      setError('Error during logout. Please try again.');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <FeedbackProvider>
            <Router>
              {isAuthenticated && (
                <AppBar position="static">
                  <Toolbar>
                    <IconButton
                      size="large"
                      edge="start"
                      color="inherit"
                      aria-label="menu"
                      sx={{ mr: 2 }}
                    >
                      <MenuIcon />
                    </IconButton>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                      College Feedback System
                    </Typography>
                    <Button color="inherit" href="/dashboard">
                      Dashboard
                    </Button>
                    <Button color="inherit" href="/feedback/submit">
                      Submit Feedback
                    </Button>
                    <Button color="inherit" href="/feedback/list">
                      View Feedback
                    </Button>
                    <Button color="inherit" onClick={handleLogout}>
                      Logout
                    </Button>
                  </Toolbar>
                </AppBar>
              )}

              <Box sx={{ flexGrow: 1, mt: isAuthenticated ? 2 : 0 }}>
                <Routes>
                  <Route
                    path="/"
                    element={
                      isAuthenticated ? (
                        <Navigate to="/dashboard" replace />
                      ) : (
                        <Navigate to="/login" replace />
                      )
                    }
                  />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route
                    path="/dashboard"
                    element={
                      <ProtectedRoute>
                        <Dashboard />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/feedback/submit"
                    element={
                      <ProtectedRoute>
                        <FeedbackForm />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/feedback/list"
                    element={
                      <ProtectedRoute>
                        <FeedbackList />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/admin/*"
                    element={
                      <ProtectedRoute allowedRoles={['admin']}>
                        {/* Add admin components here */}
                        <div>Admin Panel</div>
                      </ProtectedRoute>
                    }
                  />
                </Routes>
              </Box>
            </Router>
          </FeedbackProvider>
        </AuthProvider>
        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={() => setError(null)}
        >
          <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        </Snackbar>
      </ThemeProvider>
    </ErrorBoundary>
  );
};

export default App;
