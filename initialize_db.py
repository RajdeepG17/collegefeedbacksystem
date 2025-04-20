import sqlite3
import os
from pathlib import Path
from datetime import datetime

# Get the base directory of your Django project
BASE_DIR = Path(__file__).resolve().parent

# Connect to the SQLite database
db_path = os.path.join(BASE_DIR, 'db.sqlite3')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# First, let's check if the table exists and its schema
cursor.execute("PRAGMA table_info(feedback_feedbackcategory)")
columns = cursor.fetchall()
print("Table schema:", columns)

# Get the column names
column_names = [col[1] for col in columns]
print("Columns:", column_names)

# Define the categories to create
categories = [
    ('Academic', 'Issues related to courses, curriculum, teaching methods, and academic resources', 'school'),
    ('Infrastructure', 'Feedback about buildings, classrooms, labs, wifi, and other physical facilities', 'building'),
    ('Administrative', 'Issues with administration, enrollment, fees, or general management', 'admin_panel_settings'),
    ('Faculty', 'Feedback about professors, teaching assistants, and academic staff', 'people'),
    ('Student Services', 'Comments about student support services, counseling, and extracurricular activities', 'support'),
    ('Other', 'Any other feedback that doesn\'t fit into the above categories', 'more_horiz')
]

# Current timestamp in ISO format for SQLite
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Insert categories based on the existing table schema
if 'name' in column_names and 'description' in column_names:
    # Check for existing categories to avoid duplicates
    cursor.execute("SELECT name FROM feedback_feedbackcategory")
    existing_categories = [row[0] for row in cursor.fetchall()]
    
    for name, description, icon in categories:
        if name not in existing_categories:
            # Insert with all required fields
            cursor.execute(
                """
                INSERT INTO feedback_feedbackcategory 
                (name, description, icon, active, created_at, updated_at) 
                VALUES (?, ?, ?, ?, ?, ?)
                """, 
                (name, description, icon, True, now, now)
            )
            print(f"Added category: {name}")
        else:
            print(f"Category already exists: {name}")

    # Commit the changes
    conn.commit()
    print("Categories added successfully!")
else:
    print("Required columns (name, description) not found in the table.")

# Close the connection
conn.close() 