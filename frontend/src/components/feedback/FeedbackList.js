import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const FeedbackList = () => {
    const [feedbacks, setFeedbacks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        status: '',
        priority: '',
        category: ''
    });
    const [categories, setCategories] = useState([]);

    useEffect(() => {
        fetchFeedbacks();
        fetchCategories();
    }, [filters]);

    const fetchFeedbacks = async () => {
        try {
            const params = new URLSearchParams();
            if (filters.status) params.append('status', filters.status);
            if (filters.priority) params.append('priority', filters.priority);
            if (filters.category) params.append('category', filters.category);

            const response = await axios.get(`/api/feedback/feedbacks/?${params.toString()}`);
            setFeedbacks(response.data.results);
        } catch (error) {
            console.error('Error fetching feedbacks:', error);
            toast.error('Failed to load feedbacks');
        } finally {
            setLoading(false);
        }
    };

    const fetchCategories = async () => {
        try {
            const response = await axios.get('/api/feedback/categories/');
            setCategories(response.data.results);
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    };

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFilters(prev => ({
            ...prev,
            [name]: value
        }));
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

    return (
        <div className="container mt-5">
            <div className="row mb-4">
                <div className="col">
                    <h2>Feedback List</h2>
                </div>
                <div className="col text-end">
                    <Link to="/feedback/submit" className="btn btn-primary">
                        Submit New Feedback
                    </Link>
                </div>
            </div>

            <div className="card shadow mb-4">
                <div className="card-body">
                    <div className="row mb-3">
                        <div className="col-md-4">
                            <select
                                className="form-select"
                                name="status"
                                value={filters.status}
                                onChange={handleFilterChange}
                            >
                                <option value="">All Status</option>
                                <option value="pending">Pending</option>
                                <option value="in_progress">In Progress</option>
                                <option value="resolved">Resolved</option>
                                <option value="closed">Closed</option>
                                <option value="rejected">Rejected</option>
                            </select>
                        </div>
                        <div className="col-md-4">
                            <select
                                className="form-select"
                                name="priority"
                                value={filters.priority}
                                onChange={handleFilterChange}
                            >
                                <option value="">All Priority</option>
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                                <option value="urgent">Urgent</option>
                            </select>
                        </div>
                        <div className="col-md-4">
                            <select
                                className="form-select"
                                name="category"
                                value={filters.category}
                                onChange={handleFilterChange}
                            >
                                <option value="">All Categories</option>
                                {categories.map(category => (
                                    <option key={category.id} value={category.id}>
                                        {category.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="table-responsive">
                        <table className="table table-hover">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Category</th>
                                    <th>Status</th>
                                    <th>Priority</th>
                                    <th>Submitted</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {feedbacks.map(feedback => (
                                    <tr key={feedback.id}>
                                        <td>
                                            <Link to={`/feedback/${feedback.id}`}>
                                                {feedback.title}
                                            </Link>
                                        </td>
                                        <td>{feedback.category_name}</td>
                                        <td>
                                            <span className={`badge ${getStatusBadgeClass(feedback.status)}`}>
                                                {feedback.status.replace('_', ' ')}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={`badge ${getPriorityBadgeClass(feedback.priority)}`}>
                                                {feedback.priority}
                                            </span>
                                        </td>
                                        <td>{new Date(feedback.created_at).toLocaleDateString()}</td>
                                        <td>
                                            <Link
                                                to={`/feedback/${feedback.id}`}
                                                className="btn btn-sm btn-outline-primary"
                                            >
                                                View
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FeedbackList; 