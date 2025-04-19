from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import FeedbackCategory, Feedback, FeedbackComment, FeedbackHistory

User = get_user_model()

class FeedbackTests(APITestCase):
    def setUp(self):
        # Create test users
        self.student = User.objects.create_user(
            email='student@example.com',
            password='testpass123',
            user_type='student'
        )
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            user_type='admin',
            admin_category='academic'
        )
        self.superadmin = User.objects.create_user(
            email='superadmin@example.com',
            password='testpass123',
            user_type='superadmin'
        )
        
        # Create test category
        self.category = FeedbackCategory.objects.create(
            name='Academic',
            description='Academic related feedback',
            icon='fa-book',
            active=True
        )
        
        # Create test feedback
        self.feedback = Feedback.objects.create(
            title='Test Feedback',
            description='Test description',
            category=self.category,
            submitter=self.student,
            status='pending',
            priority='medium'
        )
        
        # Create test comment
        self.comment = FeedbackComment.objects.create(
            feedback=self.feedback,
            user=self.admin,
            comment='Test comment',
            is_internal=False
        )
        
        # Create test history
        self.history = FeedbackHistory.objects.create(
            feedback=self.feedback,
            changed_by=self.admin,
            old_status='pending',
            new_status='in_progress',
            notes='Test history'
        )
        
        # Set up API client
        self.client = APIClient()
    
    def test_feedback_category_list(self):
        """Test listing feedback categories"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(reverse('category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_feedback_category_create(self):
        """Test creating feedback category"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'name': 'New Category',
            'description': 'New category description',
            'icon': 'fa-star',
            'active': True
        }
        response = self.client.post(reverse('category-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FeedbackCategory.objects.count(), 2)
    
    def test_feedback_list(self):
        """Test listing feedback"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(reverse('feedback-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_feedback_create(self):
        """Test creating feedback"""
        self.client.force_authenticate(user=self.student)
        data = {
            'title': 'New Feedback',
            'description': 'New feedback description',
            'category': self.category.id,
            'priority': 'high',
            'is_anonymous': False
        }
        response = self.client.post(reverse('feedback-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feedback.objects.count(), 2)
    
    def test_feedback_update(self):
        """Test updating feedback"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'status': 'in_progress',
            'priority': 'high'
        }
        response = self.client.patch(
            reverse('feedback-detail', args=[self.feedback.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.status, 'in_progress')
        self.assertEqual(self.feedback.priority, 'high')
    
    def test_feedback_resolve(self):
        """Test resolving feedback"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse('feedback-resolve', args=[self.feedback.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.status, 'resolved')
    
    def test_feedback_reopen(self):
        """Test reopening feedback"""
        self.feedback.status = 'resolved'
        self.feedback.save()
        
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            reverse('feedback-reopen', args=[self.feedback.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.status, 'in_progress')
    
    def test_feedback_rate(self):
        """Test rating feedback"""
        # First resolve the feedback as admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse('feedback-resolve', args=[self.feedback.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Then rate it as the student
        self.client.force_authenticate(user=self.student)
        data = {
            'rating': 5,
            'comment': 'Great service!'
        }
        response = self.client.post(
            reverse('feedback-rate', args=[self.feedback.id]),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.rating, 5)
    
    def test_comment_list(self):
        """Test listing comments"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(
            reverse('feedback-comment-list', args=[self.feedback.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_comment_create(self):
        """Test creating comment"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'feedback': self.feedback.id,
            'comment': 'New comment',
            'is_internal': False
        }
        response = self.client.post(
            reverse('feedback-comment-list', args=[self.feedback.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FeedbackComment.objects.count(), 2)
    
    def test_history_list(self):
        """Test listing history"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(
            reverse('feedback-history-list', args=[self.feedback.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_permissions(self):
        """Test permissions"""
        # Test student cannot create category
        self.client.force_authenticate(user=self.student)
        data = {
            'name': 'New Category',
            'description': 'New category description',
            'icon': 'fa-star',
            'active': True
        }
        response = self.client.post(reverse('category-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test student cannot update feedback status
        data = {'status': 'resolved'}
        response = self.client.patch(
            reverse('feedback-detail', args=[self.feedback.id]),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test student cannot create internal comments
        data = {
            'feedback': self.feedback.id,
            'comment': 'Internal comment',
            'is_internal': True
        }
        response = self.client.post(
            reverse('feedback-comment-list', args=[self.feedback.id]),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
