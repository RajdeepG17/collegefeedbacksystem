import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Typography,
  Box,
} from '@mui/material';
import { useFeedback } from '../../contexts/FeedbackContext';

const FeedbackList = () => {
  const { feedbacks, loading, error, fetchFeedbacks } = useFeedback();
  const navigate = useNavigate();

  useEffect(() => {
    fetchFeedbacks();
  }, []);

  if (loading) return <Typography>Loading...</Typography>;
  if (error) return <Typography color="error">{error}</Typography>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h4">Feedback List</Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => navigate('/feedback/create')}
        >
          Create Feedback
        </Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created At</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {feedbacks.map((feedback) => (
              <TableRow key={feedback.id}>
                <TableCell>{feedback.title}</TableCell>
                <TableCell>{feedback.category}</TableCell>
                <TableCell>{feedback.status}</TableCell>
                <TableCell>{new Date(feedback.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => navigate(`/feedback/${feedback.id}`)}
                  >
                    View
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default FeedbackList; 