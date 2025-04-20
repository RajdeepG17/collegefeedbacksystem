import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_feedback_system.settings')
django.setup()

from feedback.models import FeedbackCategory

# Define categories to create
categories = [
    {
        'name': 'Academic',
        'description': 'Issues related to courses, curriculum, teaching methods, and academic resources',
        'is_active': True
    },
    {
        'name': 'Infrastructure',
        'description': 'Feedback about buildings, classrooms, labs, wifi, and other physical facilities',
        'is_active': True
    },
    {
        'name': 'Administrative',
        'description': 'Issues with administration, enrollment, fees, or general management',
        'is_active': True
    },
    {
        'name': 'Faculty',
        'description': 'Feedback about professors, teaching assistants, and academic staff',
        'is_active': True
    },
    {
        'name': 'Student Services',
        'description': 'Comments about student support services, counseling, and extracurricular activities',
        'is_active': True
    },
    {
        'name': 'Other',
        'description': 'Any other feedback that doesn\'t fit into the above categories',
        'is_active': True
    }
]

# Create categories if they don't exist
for category_data in categories:
    category, created = FeedbackCategory.objects.get_or_create(
        name=category_data['name'],
        defaults=category_data
    )
    if created:
        print(f"Created category: {category.name}")
    else:
        print(f"Category already exists: {category.name}")

print("Feedback categories setup complete!") 