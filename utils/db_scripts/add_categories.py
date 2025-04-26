import os
import sys
import django
from pathlib import Path

# Add the parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_feedback_system.settings')
django.setup()

from feedback.models import FeedbackCategory

def add_categories():
    """
    Add or update feedback categories in the database.
    """
    print("Adding feedback categories...")
    
    categories = [
        {"name": "Academic", "description": "Issues related to academics, courses, and teaching"},
        {"name": "Infrastructure", "description": "Issues related to college buildings, classrooms, labs"},
        {"name": "Administration", "description": "Issues related to administrative processes and staff"},
        {"name": "Canteen", "description": "Issues related to food quality, prices and canteen facilities"},
        {"name": "Transportation", "description": "Issues related to college buses and transportation facilities"},
        {"name": "Facilities", "description": "Issues related to general facilities like library, gym, etc."},
        {"name": "Sports", "description": "Issues related to sports facilities and equipment"},
        {"name": "Events", "description": "Feedback on college events and cultural activities"},
        {"name": "Security", "description": "Issues related to campus security and safety measures"},
        {"name": "Technology", "description": "Issues related to IT infrastructure and digital resources"},
    ]
    
    for cat_data in categories:
        category, created = FeedbackCategory.objects.get_or_create(
            name=cat_data["name"],
            defaults={"description": cat_data["description"]}
        )
        if created:
            print(f"Created category: {category.name}")
        else:
            # Update description if it's different
            if category.description != cat_data["description"]:
                category.description = cat_data["description"]
                category.save()
                print(f"Updated category: {category.name}")
            else:
                print(f"Category already exists: {category.name}")
    
    print("Categories setup complete!")

if __name__ == "__main__":
    add_categories() 