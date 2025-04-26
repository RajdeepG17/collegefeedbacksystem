import os
import sys
import django
from pathlib import Path
import random

# Add the parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_feedback_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Department, UserProfile
from django.db import transaction

User = get_user_model()

def create_test_users(count=10):
    """
    Create test users for development and testing.
    
    Args:
        count: Number of test users to create per role
    """
    print(f"Creating {count} test users per role...")
    
    # Get departments
    try:
        departments = list(Department.objects.all())
        if not departments:
            print("No departments found. Please run initialize_db.py first.")
            return
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return
    
    # User roles
    roles = ['student', 'faculty', 'staff']
    
    # Create users for each role
    with transaction.atomic():
        for role in roles:
            print(f"Creating {role} users...")
            for i in range(1, count + 1):
                email = f"test_{role}{i}@example.com"
                
                # Skip if user already exists
                if User.objects.filter(email=email).exists():
                    print(f"User {email} already exists. Skipping.")
                    continue
                
                # Create the user
                user = User.objects.create_user(
                    email=email,
                    password=f"Test{role.capitalize()}123!",
                    first_name=f"{role.capitalize()}",
                    last_name=f"User{i}",
                    is_active=True
                )
                
                # Assign a random department
                department = random.choice(departments)
                
                # Create user profile
                UserProfile.objects.create(
                    user=user,
                    department=department,
                    role=role,
                    phone_number=f"+123456789{i}",
                    bio=f"This is a test {role} user for development purposes."
                )
                
                print(f"Created {role} user: {email}")
    
    print("Test users creation complete!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create test users for development')
    parser.add_argument('--count', type=int, default=5, help='Number of test users to create per role')
    
    args = parser.parse_args()
    create_test_users(args.count) 