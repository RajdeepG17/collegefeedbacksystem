import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';

const FeedbackDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [feedback, setFeedback] = useState(null);
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState('');
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);

    useEffect(() => {
        fetchFeedback();
        fetchComments();
    }, [id]);

    const fetchFeedback = async () => {
        try {
            const response = await axios.get(`/api/feedback/feedbacks/${id}/`);
            setFeedback(response.data);
        } catch (error) {
            console.error('Error fetching feedback:', error);
            toast.error('Failed to load feedback');
        } finally {
            setLoading(false);
        }
    };

    const fetchComments = async () => {
        try {
            const response = await axios.get(`/api/feedback/comments/?feedback=${id}`);
            setComments(response.data.results);
        } catch (error) {
            console.error('Error fetching comments:', error);
        }
    };

    const handleCommentSubmit = async (e) => {
        e.preventDefault();
        if (!newComment.trim()) return;

        try {
            await axios.post('/api/feedback/comments/', {
                feedback: id,
                comment: newComment
            });
            setNewComment('');
            fetchComments();
            toast.success('Comment added successfully');
        } catch (error) {
            console.error('Error adding comment:', error);
            toast.error('Failed to add comment');
        }
    };

    const handleStatusChange = async (newStatus) => {
        setActionLoading(true);
        try {
            await axios.post(`/api/feedback/feedbacks/${id}/${newStatus}/`);
            fetchFeedback();
            toast.success(`Feedback marked as ${newStatus}`);
        } catch (error) {
            console.error('Error updating status:', error);
            toast.error('Failed to update status');
        } finally {
            setActionLoading(false);
        }
    };

    const getStatusBadgeClass = (status) => {
        switch (status) {
            case 'pending':
                return 'bg-warning';
            case 'in_progress':
                return 'bg-info';
            case 'resolved':
                return 'bg-success';
            case 'closed':
                return 'bg-secondary';
            case 'rejected':
                return 'bg-danger';
            default:
                return 'bg-secondary';
        }
    };

    const getPriorityBadgeClass = (priority) => {
        switch (priority) {
            case 'low':
                return 'bg-success';
            case 'medium':
                return 'bg-info';
            case 'high':
                return 'bg-warning';
            case 'urgent':
                return 'bg-danger';
            default:
                return 'bg-secondary';
        }
    };

    if (loading) {
        return <div className="text-center mt-5">Loading...</div>;
    }

    if (!feedback) {
        return <div className="text-center mt-5">Feedback not found</div>;
    }

    return (
        <div className="container mt-5">
            <div className="row mb-4">
                <div className="col">
                    <h2>{feedback.title}</h2>
                </div>
                <div className="col text-end">
                    <button
                        className="btn btn-outline-secondary me-2"
                        onClick={() => navigate('/feedback')}
                    >
                        Back to List
                    </button>
                    {user.user_type === 'admin' && (
                        <>
                            {feedback.status === 'pending' && (
                                <button
                                    className="btn btn-primary me-2"
                                    onClick={() => handleStatusChange('in_progress')}
                                    disabled={actionLoading}
                                >
                                    Start Progress
                                </button>
                            )}
                            {feedback.status === 'in_progress' && (
                                <button
                                    className="btn btn-success me-2"
                                    onClick={() => handleStatusChange('resolved')}
                                    disabled={actionLoading}
                                >
                                    Mark Resolved
                                </button>
                            )}
                            {feedback.status === 'resolved' && (
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => handleStatusChange('closed')}
                                    disabled={actionLoading}
                                >
                                    Close Feedback
                                </button>
                            )}
                        </>
                    )}
                </div>
            </div>

            <div className="card shadow mb-4">
                <div className="card-body">
                    <div className="row mb-4">
                        <div className="col-md-8">
                            <h5 className="card-title">Description</h5>
                            <p className="card-text">{feedback.description}</p>
                        </div>
                        <div className="col-md-4">
                            <div className="mb-3">
                                <strong>Status:</strong>{' '}
                                <span className={`badge ${getStatusBadgeClass(feedback.status)}`}>
                                    {feedback.status.replace('_', ' ')}
                                </span>
                            </div>
                            <div className="mb-3">
                                <strong>Priority:</strong>{' '}
                                <span className={`badge ${getPriorityBadgeClass(feedback.priority)}`}>
                                    {feedback.priority}
                                </span>
                            </div>
                            <div className="mb-3">
                                <strong>Category:</strong> {feedback.category_name}
                            </div>
                            <div className="mb-3">
                                <strong>Submitted by:</strong>{' '}
                                {feedback.is_anonymous ? 'Anonymous' : feedback.submitter_name}
                            </div>
                            <div className="mb-3">
                                <strong>Submitted on:</strong>{' '}
                                {new Date(feedback.created_at).toLocaleString()}
                            </div>
                            {feedback.attachment && (
                                <div className="mb-3">
                                    <strong>Attachment:</strong>{' '}
                                    <a
                                        href={feedback.attachment}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        Download
                                    </a>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="mt-4">
                        <h5>Comments</h5>
                        <div className="mb-4">
                            {comments.map(comment => (
                                <div key={comment.id} className="card mb-2">
                                    <div className="card-body">
                                        <div className="d-flex justify-content-between">
                                            <strong>{comment.user_name}</strong>
                                            <small className="text-muted">
                                                {new Date(comment.created_at).toLocaleString()}
                                            </small>
                                        </div>
                                        <p className="card-text mt-2">{comment.comment}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <form onSubmit={handleCommentSubmit}>
                            <div className="mb-3">
                                <textarea
                                    className="form-control"
                                    rows="3"
                                    value={newComment}
                                    onChange={(e) => setNewComment(e.target.value)}
                                    placeholder="Add a comment..."
                                />
                            </div>
                            <button type="submit" className="btn btn-primary">
                                Add Comment
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FeedbackDetail; 