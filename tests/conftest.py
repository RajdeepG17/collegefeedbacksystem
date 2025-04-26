"""
Configuration file for pytest containing shared fixtures.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from accounts.models import Department, UserProfile
from feedback.models import FeedbackCategory

User = get_user_model()

@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()

@pytest.fixture
def test_password():
    """Return a test password."""
    return "Test123!"

@pytest.fixture
def test_user(test_password):
    """Create a test user."""
    user = User.objects.create_user(
        email="testuser@example.com",
        password=test_password,
        first_name="Test",
        last_name="User"
    )
    return user

@pytest.fixture
def test_admin(test_password):
    """Create a test admin user."""
    admin = User.objects.create_superuser(
        email="admin@example.com",
        password=test_password,
        first_name="Admin",
        last_name="User"
    )
    return admin

@pytest.fixture
def test_department():
    """Create a test department."""
    return Department.objects.create(
        name="Test Department",
        code="TEST"
    )

@pytest.fixture
def test_user_profile(test_user, test_department):
    """Create a test user profile."""
    return UserProfile.objects.create(
        user=test_user,
        department=test_department,
        role="student",
        phone_number="+1234567890"
    )

@pytest.fixture
def test_admin_profile(test_admin, test_department):
    """Create a test admin profile."""
    return UserProfile.objects.create(
        user=test_admin,
        department=test_department,
        role="admin",
        phone_number="+0987654321"
    )

@pytest.fixture
def test_category():
    """Create a test feedback category."""
    return FeedbackCategory.objects.create(
        name="Test Category",
        description="Category for testing purposes"
    )

@pytest.fixture
def authenticated_user_client(api_client, test_user):
    """Return an authenticated client as a regular user."""
    api_client.force_authenticate(user=test_user)
    return api_client

@pytest.fixture
def authenticated_admin_client(api_client, test_admin):
    """Return an authenticated client as an admin user."""
    api_client.force_authenticate(user=test_admin)
    return api_client 