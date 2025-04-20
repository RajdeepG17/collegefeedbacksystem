import React from 'react';
import { Box, Alert, Typography, Button } from '@mui/material';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        // You can log the error to an error reporting service
        console.error('Error caught by boundary:', error, errorInfo);
        this.setState({ errorInfo });
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    }

    render() {
        if (this.state.hasError) {
            return (
                <Box 
                    sx={{ 
                        p: 4, 
                        textAlign: 'center', 
                        display: 'flex', 
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        minHeight: '100vh'
                    }}
                >
                    <Typography variant="h4" gutterBottom>
                        Something went wrong
                    </Typography>
                    
                    <Alert severity="error" sx={{ mb: 3, maxWidth: 600 }}>
                        {this.state.error?.message || 'An unexpected error occurred'}
                    </Alert>
                    
                    <Box sx={{ mt: 2 }}>
                        <Button 
                            variant="contained" 
                            onClick={() => window.location.href = '/'}
                            sx={{ mr: 2 }}
                        >
                            Go to Home
                        </Button>
                        
                        <Button 
                            variant="outlined" 
                            onClick={this.handleReset}
                        >
                            Try Again
                        </Button>
                    </Box>
                </Box>
            );
        }
        
        // If there's no error, render children normally
        return this.props.children;
    }
}

export default ErrorBoundary; 