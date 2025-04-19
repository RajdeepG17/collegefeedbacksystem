import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { Error as ErrorIcon } from '@mui/icons-material';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        this.setState({
            error: error,
            errorInfo: errorInfo
        });
        // Log error to error reporting service
        console.error('Error caught by ErrorBoundary:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <Box
                    sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        minHeight: '100vh',
                        p: 3,
                        textAlign: 'center',
                    }}
                >
                    <ErrorIcon sx={{ fontSize: 60, color: 'error.main', mb: 2 }} />
                    <Typography variant="h4" gutterBottom>
                        Something went wrong
                    </Typography>
                    <Typography variant="body1" color="text.secondary" paragraph>
                        We're sorry, but something went wrong. Please try refreshing the page or contact support if the problem persists.
                    </Typography>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={() => window.location.reload()}
                        sx={{ mt: 2 }}
                    >
                        Refresh Page
                    </Button>
                    {process.env.NODE_ENV === 'development' && (
                        <Box sx={{ mt: 4, textAlign: 'left', maxWidth: '800px' }}>
                            <Typography variant="h6" gutterBottom>
                                Error Details:
                            </Typography>
                            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                                {this.state.error && this.state.error.toString()}
                                {this.state.errorInfo && this.state.errorInfo.componentStack}
                            </pre>
                        </Box>
                    )}
                </Box>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary; 