import sqlite3
import os
from pathlib import Path
from datetime import datetime
from django.utils.crypto import get_random_string
import hashlib
import binascii

# Get the base directory of your Django project
BASE_DIR = Path(__file__).resolve().parent

# Connect to the SQLite database
db_path = os.path.join(BASE_DIR, 'db.sqlite3')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Function to hash password (simplified version)
def hash_password(password):
    # This is a simplified hash for demonstration
    # In production, you should use Django's password hasher
    salt = get_random_string(length=12)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 36000)
    hashed = binascii.hexlify(dk).decode()
    return f"pbkdf2_sha256$36000${salt}${hashed}"

# Get current timestamp
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Check if users already exist
cursor.execute("SELECT email FROM accounts_user WHERE email IN (?, ?)", 
               ('student@example.com', 'admin@example.com'))
existing_users = [row[0] for row in cursor.fetchall()]

# Create student user if not exists
if 'student@example.com' not in existing_users:
    cursor.execute("""
    INSERT INTO accounts_user 
    (password, last_login, is_superuser, first_name, last_name, is_staff, is_active, date_joined,
     email, user_type, admin_category, created_at, updated_at, is_staff_member) 
    VALUES 
    (?, NULL, 0, 'Test', 'Student', 0, 1, ?, 'student@example.com', 'student', 'none', ?, ?, 0)
    """, (hash_password('student123'), now, now, now))
    print("Created user: student@example.com")
else:
    print("User student@example.com already exists")

# Create admin user if not exists
if 'admin@example.com' not in existing_users:
    cursor.execute("""
    INSERT INTO accounts_user 
    (password, last_login, is_superuser, first_name, last_name, is_staff, is_active, date_joined,
     email, user_type, admin_category, created_at, updated_at, is_staff_member) 
    VALUES 
    (?, NULL, 0, 'Test', 'Admin', 1, 1, ?, 'admin@example.com', 'admin', 'academic', ?, ?, 1)
    """, (hash_password('admin123'), now, now, now))
    print("Created user: admin@example.com")
else:
    print("User admin@example.com already exists")

# Commit the changes
conn.commit()
print("User creation completed!")

# Close the connection
conn.close() 