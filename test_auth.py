import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_feedback_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_superuser_login():
    try:
        # Get the superuser
        user = User.objects.get(email='pgdca2025@gmail.com')
        print(f"User found: {user.email}")
        print(f"Is superuser: {user.is_superuser}")
        print(f"Is staff: {user.is_staff}")
        
        # Test login
        client = APIClient()
        response = client.post('/api/auth/login/', {
            'email': 'pgdca2025@gmail.com',
            'password': '12345678'
        })
        
        print("\nLogin Response:")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Login successful!")
            print(f"Access Token: {response.data.get('access')[:20]}...")
            print(f"Refresh Token: {response.data.get('refresh')[:20]}...")
        else:
            print(f"Login failed: {response.data}")
            
    except User.DoesNotExist:
        print("Superuser not found!")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    test_superuser_login() 