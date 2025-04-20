#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_feedback_system.settings')
django.setup()

from feedback.models import FeedbackCategory

def create_default_categories():
    """Create default feedback categories if they don't exist."""
    default_categories = [
        {'name': 'Academic', 'description': 'Feedback related to academic matters', 'icon': 'school'},
        {'name': 'Infrastructure', 'description': 'Feedback related to infrastructure', 'icon': 'building'},
        {'name': 'Administrative', 'description': 'Feedback related to administrative matters', 'icon': 'admin_panel_settings'},
        {'name': 'Other', 'description': 'Other types of feedback', 'icon': 'more_horiz'}
    ]
    
    created = 0
    for category_data in default_categories:
        category, was_created = FeedbackCategory.objects.get_or_create(
            name=category_data['name'],
            defaults={
                'description': category_data['description'],
                'icon': category_data['icon'],
                'active': True
            }
        )
        if was_created:
            created += 1
            print(f"Created category: {category.name}")
        else:
            print(f"Category already exists: {category.name}")
    
    print(f"\n{created} new categories created.")
    print(f"{len(default_categories) - created} categories already existed.")
    print(f"Total categories: {FeedbackCategory.objects.count()}")

if __name__ == "__main__":
    print("Creating default feedback categories...")
    create_default_categories()
    print("Done!") 