from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User
from feedback.models import Feedback
import json

class APIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            user_type='student'
        )
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            user_type='admin',
            is_staff=True
        )

    def test_authentication_flow(self):
        """Test the complete authentication flow"""
        # Test registration
        register_data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'user_type': 'student'
        }
        response = self.client.post('/api/v1/auth/register/', register_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test login
        login_data = {
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response = self.client.post('/api/v1/auth/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Store tokens
        access_token = response.data['access']
        refresh_token = response.data['refresh']

        # Test token refresh
        refresh_data = {'refresh': refresh_token}
        response = self.client.post('/api/v1/auth/token/refresh/', refresh_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_feedback_crud_operations(self):
        """Test feedback creation, reading, updating, and deletion"""
        # Login as student
        self.client.force_authenticate(user=self.user)

        # Create feedback
        feedback_data = {
            'title': 'Test Feedback',
            'content': 'This is a test feedback',
            'rating': 4
        }
        response = self.client.post('/api/v1/feedback/', feedback_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        feedback_id = response.data['id']

        # Read feedback
        response = self.client.get(f'/api/v1/feedback/{feedback_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Feedback')

        # Update feedback
        update_data = {
            'title': 'Updated Feedback',
            'content': 'This is an updated feedback',
            'rating': 5
        }
        response = self.client.put(f'/api/v1/feedback/{feedback_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Feedback')

        # Delete feedback
        response = self.client.delete(f'/api/v1/feedback/{feedback_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_rate_limiting(self):
        """Test API rate limiting"""
        # Login as student
        self.client.force_authenticate(user=self.user)

        # Make requests up to the limit
        for _ in range(60):  # Default limit is 60 requests per minute
            response = self.client.get('/api/v1/feedback/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Next request should be rate limited
        response = self.client.get('/api/v1/feedback/')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_permission_checks(self):
        """Test permission-based access control"""
        # Create a feedback as student
        self.client.force_authenticate(user=self.user)
        feedback_data = {
            'title': 'Test Feedback',
            'content': 'This is a test feedback',
            'rating': 4
        }
        response = self.client.post('/api/v1/feedback/', feedback_data)
        feedback_id = response.data['id']

        # Try to access admin-only endpoint as student
        response = self.client.get('/api/v1/admin/feedback/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Access as admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/v1/admin/feedback/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_error_handling(self):
        """Test error handling and validation"""
        # Test invalid registration data
        invalid_data = {
            'email': 'invalid-email',
            'password': 'short',
            'user_type': 'invalid'
        }
        response = self.client.post('/api/v1/auth/register/', invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)
        self.assertIn('user_type', response.data)

        # Test invalid feedback data
        self.client.force_authenticate(user=self.user)
        invalid_feedback = {
            'title': '',  # Empty title
            'content': 'Test content',
            'rating': 6  # Invalid rating
        }
        response = self.client.post('/api/v1/feedback/', invalid_feedback)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('rating', response.data)

    def test_pagination(self):
        """Test API pagination"""
        # Create multiple feedback entries
        self.client.force_authenticate(user=self.user)
        for i in range(15):
            feedback_data = {
                'title': f'Feedback {i}',
                'content': f'Content {i}',
                'rating': i % 5 + 1
            }
            self.client.post('/api/v1/feedback/', feedback_data)

        # Test pagination
        response = self.client.get('/api/v1/feedback/?page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 10)  # Default page size

        # Test second page
        response = self.client.get('/api/v1/feedback/?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # Remaining items 