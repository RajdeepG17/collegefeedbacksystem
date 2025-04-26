import os
import sys
import django
from pathlib import Path
import sqlite3

# Add the parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_feedback_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Department, UserProfile
from feedback.models import FeedbackCategory

User = get_user_model()

def initialize_database():
    """
    Initialize the database with default data for College Feedback System.
    """
    print("Starting database initialization...")
    
    # Create departments
    departments = [
        {"name": "Computer Science", "code": "CS"},
        {"name": "Information Technology", "code": "IT"},
        {"name": "Electronics", "code": "EC"},
        {"name": "Mechanical Engineering", "code": "ME"},
        {"name": "Civil Engineering", "code": "CE"},
    ]
    
    for dept_data in departments:
        dept, created = Department.objects.get_or_create(
            code=dept_data["code"],
            defaults={"name": dept_data["name"]}
        )
        if created:
            print(f"Created department: {dept.name}")
    
    # Create admin user if it doesn't exist
    if not User.objects.filter(email="admin@example.com").exists():
        admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="Admin@123",
            first_name="Admin",
            last_name="User"
        )
        UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                "department": Department.objects.get(code="CS"),
                "role": "admin"
            }
        )
        print("Created admin user")
    
    # Create feedback categories
    categories = [
        {"name": "Academic", "description": "Issues related to academics, courses, and teaching"},
        {"name": "Infrastructure", "description": "Issues related to college buildings, classrooms, labs"},
        {"name": "Administration", "description": "Issues related to administrative processes and staff"},
        {"name": "Canteen", "description": "Issues related to food quality, prices and canteen facilities"},
        {"name": "Transportation", "description": "Issues related to college buses and transportation facilities"},
        {"name": "Facilities", "description": "Issues related to general facilities like library, gym, etc."},
    ]
    
    for cat_data in categories:
        category, created = FeedbackCategory.objects.get_or_create(
            name=cat_data["name"],
            defaults={"description": cat_data["description"]}
        )
        if created:
            print(f"Created feedback category: {category.name}")
    
    print("Database initialization complete!")

if __name__ == "__main__":
    initialize_database() 