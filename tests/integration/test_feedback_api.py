import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import Department, UserProfile
from feedback.models import FeedbackCategory, Feedback

User = get_user_model()

@pytest.mark.integration
@pytest.mark.feedback
class TestFeedbackAPI:
    """Test suite for the Feedback API endpoints."""
    
    @pytest.fixture
    def api_client(self):
        """Create an API client."""
        return APIClient()
    
    @pytest.fixture
    def user(self):
        """Create a test user."""
        user = User.objects.create_user(
            email="testapi@example.com",
            password="ApiTest123",
            first_name="API",
            last_name="Test"
        )
        return user
    
    @pytest.fixture
    def department(self):
        """Create a test department."""
        return Department.objects.create(
            name="API Test Department",
            code="ATD"
        )
    
    @pytest.fixture
    def user_profile(self, user, department):
        """Create a user profile."""
        return UserProfile.objects.create(
            user=user,
            department=department,
            role="student"
        )
    
    @pytest.fixture
    def category(self):
        """Create a test feedback category."""
        return FeedbackCategory.objects.create(
            name="API Test Category",
            description="Category for API testing"
        )
    
    @pytest.fixture
    def authenticated_client(self, api_client, user):
        """Create an authenticated API client."""
        api_client.force_authenticate(user=user)
        return api_client
    
    def test_feedback_list_authenticated(self, authenticated_client):
        """Test that authenticated users can access feedback list."""
        url = reverse('feedback-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_feedback_list_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot access feedback list."""
        url = reverse('feedback-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_feedback(self, authenticated_client, category, user):
        """Test creating a new feedback."""
        url = reverse('feedback-list')
        data = {
            'title': 'New API Feedback',
            'content': 'This is a test feedback created via API',
            'category': category.id,
            'is_anonymous': False,
            'priority': 'medium'
        }
        
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New API Feedback'
        assert response.data['submitter'] == user.id
    
    def test_update_feedback(self, authenticated_client, category, user):
        """Test updating an existing feedback."""
        # Create a feedback first
        feedback = Feedback.objects.create(
            title="Feedback to Update",
            content="This will be updated",
            status="pending",
            is_anonymous=False,
            category=category,
            submitter=user,
            priority="low"
        )
        
        url = reverse('feedback-detail', kwargs={'pk': feedback.id})
        data = {
            'title': 'Updated Feedback',
            'content': 'This content has been updated',
            'priority': 'high'
        }
        
        response = authenticated_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Feedback'
        assert response.data['priority'] == 'high'
    
    def test_delete_feedback(self, authenticated_client, category, user):
        """Test deleting a feedback."""
        # Create a feedback first
        feedback = Feedback.objects.create(
            title="Feedback to Delete",
            content="This will be deleted",
            status="pending", 
            is_anonymous=False,
            category=category,
            submitter=user,
            priority="medium"
        )
        
        url = reverse('feedback-detail', kwargs={'pk': feedback.id})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's deleted
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND 