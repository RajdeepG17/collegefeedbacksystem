import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_feedback_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# Create test users directly
def create_user(email, password, **kwargs):
    try:
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            print(f"User with email {email} already exists")
            return None
            
        # Create user
        user = User.objects.create_user(
            email=email,
            password=password,
            **kwargs
        )
        print(f"Created user: {email}")
        return user
    except Exception as e:
        print(f"Error creating user {email}: {e}")
        return None

# Create a student user
create_user(
    email='student@example.com',
    password='student123',
    first_name='Test',
    last_name='Student',
    is_active=True,
    is_staff=False,
    is_superuser=False,
    user_type='student',
    admin_category='none',
)

# Create an admin user
create_user(
    email='admin@example.com',
    password='admin123',
    first_name='Test',
    last_name='Admin',
    is_active=True,
    is_staff=True,
    is_superuser=False,
    user_type='admin',
    admin_category='academic',
)

print("User creation completed!") 