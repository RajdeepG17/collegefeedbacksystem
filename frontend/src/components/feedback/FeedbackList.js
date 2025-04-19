import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  Chip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
} from '@mui/material';
import {
  Comment as CommentIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';

const FeedbackList = () => {
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFeedback, setSelectedFeedback] = useState(null);
  const [commentDialogOpen, setCommentDialogOpen] = useState(false);
  const [newComment, setNewComment] = useState('');
  const userType = localStorage.getItem('user_type');

  useEffect(() => {
    fetchFeedbacks();
  }, []);

  const fetchFeedbacks = async () => {
    try {
      const response = await axios.get('/api/feedback/feedbacks/');
      setFeedbacks(response.data);
    } catch (error) {
      console.error('Error fetching feedbacks:', error);
      setError('Failed to load feedbacks');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (feedbackId, newStatus) => {
    try {
      await axios.post(`/api/feedback/feedbacks/${feedbackId}/change_status/`, {
        status: newStatus,
      });
      fetchFeedbacks();
    } catch (error) {
      console.error('Error changing status:', error);
      setError('Failed to update status');
    }
  };

  const handleCommentSubmit = async () => {
    try {
      await axios.post(`/api/feedback/feedbacks/${selectedFeedback.id}/comments/`, {
        comment: newComment,
      });
      setCommentDialogOpen(false);
      setNewComment('');
      fetchFeedbacks();
    } catch (error) {
      console.error('Error submitting comment:', error);
      setError('Failed to submit comment');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      in_progress: 'info',
      resolved: 'success',
      closed: 'default',
    };
    return colors[status] || 'default';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'success',
      medium: 'warning',
      high: 'error',
    };
    return colors[priority] || 'default';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Feedback List
        </Typography>

        {error && (
          <Typography color="error" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}

        <List>
          {feedbacks.map((feedback) => (
            <ListItem
              key={feedback.id}
              alignItems="flex-start"
              divider
              sx={{
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <ListItemText
                primary={
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Typography variant="subtitle1">{feedback.title}</Typography>
                    <Box>
                      <Chip
                        label={feedback.status}
                        color={getStatusColor(feedback.status)}
                        size="small"
                        sx={{ mr: 1 }}
                      />
                      <Chip
                        label={feedback.priority}
                        color={getPriorityColor(feedback.priority)}
                        size="small"
                      />
                    </Box>
                  </Box>
                }
                secondary={
                  <>
                    <Typography component="span" variant="body2" color="text.primary">
                      {feedback.description}
                    </Typography>
                    <Box mt={1}>
                      <Typography variant="caption" display="block">
                        Category: {feedback.category_name}
                      </Typography>
                      <Typography variant="caption" display="block">
                        Department: {feedback.department}
                      </Typography>
                      <Typography variant="caption" display="block">
                        Submitted by: {feedback.submitted_by_name}
                      </Typography>
                      {feedback.assigned_to_name && (
                        <Typography variant="caption" display="block">
                          Assigned to: {feedback.assigned_to_name}
                        </Typography>
                      )}
                    </Box>
                  </>
                }
              />
              <Box>
                <IconButton
                  onClick={() => {
                    setSelectedFeedback(feedback);
                    setCommentDialogOpen(true);
                  }}
                >
                  <CommentIcon />
                </IconButton>
                {userType === 'admin' && (
                  <IconButton>
                    <AssignmentIcon />
                  </IconButton>
                )}
              </Box>
            </ListItem>
          ))}
        </List>

        <Dialog
          open={commentDialogOpen}
          onClose={() => setCommentDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Add Comment</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Comment"
              fullWidth
              multiline
              rows={4}
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
            />
            {selectedFeedback?.comments?.map((comment) => (
              <Paper key={comment.id} sx={{ p: 2, mt: 2 }}>
                <Typography variant="subtitle2">{comment.user_name}</Typography>
                <Typography variant="body2">{comment.comment}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(comment.created_at).toLocaleString()}
                </Typography>
              </Paper>
            ))}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCommentDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleCommentSubmit} variant="contained">
              Submit Comment
            </Button>
          </DialogActions>
        </Dialog>
      </Paper>
    </Container>
  );
};

export default FeedbackList; 