import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import Department
from feedback.models import Feedback, FeedbackCategory

User = get_user_model()

@pytest.mark.unit
@pytest.mark.feedback
class TestFeedbackModel:
    """Test suite for the Feedback model."""
    
    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            email="testuser@example.com",
            password="TestPass123",
            first_name="Test",
            last_name="User"
        )
    
    @pytest.fixture
    def department(self):
        """Create a test department."""
        return Department.objects.create(
            name="Test Department",
            code="TD"
        )
    
    @pytest.fixture
    def category(self):
        """Create a test feedback category."""
        return FeedbackCategory.objects.create(
            name="Test Category",
            description="Category for testing"
        )
    
    @pytest.fixture
    def feedback(self, user, category):
        """Create a test feedback instance."""
        return Feedback.objects.create(
            title="Test Feedback",
            content="This is a test feedback content",
            status="pending",
            is_anonymous=False,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            category=category,
            submitter=user,
            priority="medium"
        )
    
    def test_feedback_creation(self, feedback):
        """Test that feedback can be created with valid data."""
        assert feedback.title == "Test Feedback"
        assert feedback.content == "This is a test feedback content"
        assert feedback.status == "pending"
        assert feedback.is_anonymous is False
        assert feedback.priority == "medium"
    
    def test_feedback_string_representation(self, feedback):
        """Test the string representation of feedback."""
        assert str(feedback) == "Test Feedback"
    
    def test_feedback_with_anonymous(self, user, category):
        """Test that anonymous feedback works correctly."""
        anonymous_feedback = Feedback.objects.create(
            title="Anonymous Feedback",
            content="This is an anonymous feedback",
            status="pending",
            is_anonymous=True,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            category=category,
            submitter=user,
            priority="high"
        )
        
        assert anonymous_feedback.is_anonymous is True
        assert anonymous_feedback.priority == "high"
    
    def test_feedback_status_transitions(self, feedback):
        """Test that feedback status can be updated."""
        feedback.status = "in_progress"
        feedback.save()
        assert feedback.status == "in_progress"
        
        feedback.status = "resolved"
        feedback.resolved_at = timezone.now()
        feedback.save()
        assert feedback.status == "resolved"
        assert feedback.resolved_at is not None 