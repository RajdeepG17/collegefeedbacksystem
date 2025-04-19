from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.core import mail

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'student',
            'student_id': 'AB123456',
            'department': 'Computer Science',
            'year_of_study': 2,
            'phone_number': '+1234567890'
        }
        
        self.admin_data = {
            'email': 'admin@example.com',
            'password': 'AdminPass123!',
            'password2': 'AdminPass123!',
            'first_name': 'Admin',
            'last_name': 'User',
            'user_type': 'admin',
            'admin_category': 'academic',
            'phone_number': '+1234567891'
        }

    def test_user_registration(self):
        """Test user registration endpoint"""
        url = reverse('authentication:register')
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')

    def test_admin_registration(self):
        """Test admin registration endpoint"""
        url = reverse('authentication:register')
        response = self.client.post(url, self.admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().user_type, 'admin')

    def test_user_login(self):
        """Test user login endpoint"""
        # Create user first
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        
        url = reverse('authentication:token_obtain_pair')
        response = self.client.post(url, {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_password_reset_request(self):
        """Test password reset request endpoint"""
        # Create user first
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        
        url = reverse('authentication:password_reset')
        response = self.client.post(url, {'email': 'test@example.com'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], 'test@example.com')

    def test_change_password(self):
        """Test change password endpoint"""
        # Create and authenticate user
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )