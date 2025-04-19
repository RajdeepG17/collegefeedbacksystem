import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Divider,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Person as PersonIcon,
  Send as SendIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useFeedback } from '../context/FeedbackContext';
import StatusChip from '../components/StatusChip';

const FeedbackDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const {
    feedbacks,
    loading,
    error,
    fetchFeedback,
    updateFeedback,
    deleteFeedback,
    addComment,
  } = useFeedback();

  const [feedback, setFeedback] = useState(null);
  const [comment, setComment] = useState('');
  const [submitError, setSubmitError] = useState('');

  useEffect(() => {
    const loadFeedback = async () => {
      try {
        const data = await fetchFeedback(id);
        setFeedback(data);
      } catch (error) {
        console.error('Failed to load feedback:', error);
      }
    };
    loadFeedback();
  }, [id]);

  const handleStatusChange = async (newStatus) => {
    try {
      const updatedFeedback = await updateFeedback(id, {
        ...feedback,
        status: newStatus,
      });
      setFeedback(updatedFeedback);
    } catch (error) {
      setSubmitError('Failed to update status');
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this feedback?')) {
      try {
        await deleteFeedback(id);
        navigate('/feedback');
      } catch (error) {
        setSubmitError('Failed to delete feedback');
      }
    }
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!comment.trim()) return;

    try {
      const newComment = await addComment(id, { comment: comment.trim() });
      setFeedback((prev) => ({
        ...prev,
        comments: [...prev.comments, newComment],
      }));
      setComment('');
    } catch (error) {
      setSubmitError('Failed to add comment');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !feedback) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <Alert severity="error">{error || 'Feedback not found'}</Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">{feedback.title}</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<EditIcon />}
            onClick={() => navigate(`/feedback/${id}/edit`)}
            sx={{ mr: 1 }}
          >
            Edit
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleDelete}
          >
            Delete
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Description
            </Typography>
            <Typography paragraph>{feedback.description}</Typography>

            <Box display="flex" gap={2} mb={3}>
              <StatusChip status={feedback.status} />
              <Chip
                label={feedback.priority.toUpperCase()}
                color={
                  feedback.priority === 'urgent'
                    ? 'error'
                    : feedback.priority === 'high'
                    ? 'warning'
                    : 'default'
                }
              />
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Submitted by
                </Typography>
                <Typography>
                  {feedback.submitter.first_name} {feedback.submitter.last_name}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Submitted on
                </Typography>
                <Typography>
                  {new Date(feedback.created_at).toLocaleString()}
                </Typography>
              </Grid>
              {feedback.assigned_to && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Assigned to
                  </Typography>
                  <Typography>
                    {feedback.assigned_to.first_name} {feedback.assigned_to.last_name}
                  </Typography>
                </Grid>
              )}
            </Grid>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Comments
            </Typography>
            <List>
              {feedback.comments?.map((comment) => (
                <React.Fragment key={comment.id}>
                  <ListItem alignItems="flex-start">
                    <ListItemAvatar>
                      <Avatar>
                        <PersonIcon />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box display="flex" justifyContent="space-between">
                          <Typography>
                            {comment.user.first_name} {comment.user.last_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(comment.created_at).toLocaleString()}
                          </Typography>
                        </Box>
                      }
                      secondary={comment.comment}
                    />
                  </ListItem>
                  <Divider variant="inset" component="li" />
                </React.Fragment>
              ))}
            </List>

            <Box component="form" onSubmit={handleCommentSubmit} sx={{ mt: 2 }}>
              <TextField
                fullWidth
                multiline
                rows={3}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Add a comment..."
                variant="outlined"
              />
              <Box display="flex" justifyContent="flex-end" mt={1}>
                <Button
                  type="submit"
                  variant="contained"
                  endIcon={<SendIcon />}
                  disabled={!comment.trim()}
                >
                  Send
                </Button>
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Actions
            </Typography>
            <Box display="flex" flexDirection="column" gap={1}>
              {feedback.status === 'pending' && (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => handleStatusChange('in_progress')}
                >
                  Start Progress
                </Button>
              )}
              {feedback.status === 'in_progress' && (
                <Button
                  variant="contained"
                  color="success"
                  onClick={() => handleStatusChange('resolved')}
                >
                  Mark as Resolved
                </Button>
              )}
              {feedback.status === 'resolved' && (
                <Button
                  variant="contained"
                  color="default"
                  onClick={() => handleStatusChange('closed')}
                >
                  Close Feedback
                </Button>
              )}
              {feedback.status !== 'closed' && feedback.status !== 'rejected' && (
                <Button
                  variant="contained"
                  color="error"
                  onClick={() => handleStatusChange('rejected')}
                >
                  Reject
                </Button>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FeedbackDetail; 