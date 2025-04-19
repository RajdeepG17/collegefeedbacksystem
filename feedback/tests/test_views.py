from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Feedback, FeedbackCategory, Notification
import json

User = get_user_model()

class FeedbackAPITests(APITestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='user'
        )
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
        
        # Create test category
        self.category = FeedbackCategory.objects.create(
            name='Academic',
            description='Academic related feedback'
        )
        
        # Create test feedback
        self.feedback = Feedback.objects.create(
            title='Test Feedback',
            description='This is a test feedback',
            category=self.category,
            submitter=self.user,
            priority='medium'
        )
        
        # Set up client
        self.client = Client()
        
    def test_feedback_list_authenticated(self):
        """Test that authenticated users can view feedback list"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('feedback-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_feedback_list_unauthenticated(self):
        """Test that unauthenticated users cannot view feedback list"""
        response = self.client.get(reverse('feedback-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_create_feedback(self):
        """Test creating new feedback"""
        self.client.force_login(self.user)
        data = {
            'title': 'New Feedback',
            'description': 'This is a new feedback',
            'category': self.category.id,
            'priority': 'high'
        }
        response = self.client.post(
            reverse('feedback-list'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feedback.objects.count(), 2)
        
    def test_update_feedback_status(self):
        """Test updating feedback status by admin"""
        self.client.force_login(self.admin)
        data = {
            'status': 'in_progress'
        }
        response = self.client.patch(
            reverse('feedback-detail', args=[self.feedback.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.status, 'in_progress')
        
    def test_notification_creation(self):
        """Test that notification is created when feedback is submitted"""
        self.client.force_login(self.user)
        data = {
            'title': 'New Feedback',
            'description': 'This is a new feedback',
            'category': self.category.id,
            'priority': 'high'
        }
        response = self.client.post(
            reverse('feedback-list'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(
            feedback_id=response.data['id']
        ).exists())
        
    def test_file_upload(self):
        """Test file upload with feedback"""
        self.client.force_login(self.user)
        with open('test.jpg', 'rb') as file:
            data = {
                'title': 'Feedback with file',
                'description': 'This feedback has a file',
                'category': self.category.id,
                'priority': 'medium',
                'attachment': file
            }
            response = self.client.post(
                reverse('feedback-list'),
                data=data,
                format='multipart'
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('attachment' in response.data)
        
    def test_category_filtering(self):
        """Test filtering feedback by category"""
        self.client.force_login(self.user)
        response = self.client.get(
            f"{reverse('feedback-list')}?category={self.category.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_admin_access_control(self):
        """Test that only admins can access admin endpoints"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.client.force_login(self.admin)
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, status.HTTP_200_OK) 