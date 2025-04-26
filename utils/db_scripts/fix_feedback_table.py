import sqlite3
import os
import sys
from pathlib import Path

# Add the parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Get database path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / 'db.sqlite3'

def fix_feedback_table():
    """Fix the feedback table structure to use submitter instead of user"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    print("Connected to the database")
    
    # Check if user field exists
    cursor.execute("PRAGMA table_info(feedback_feedback)")
    columns = cursor.fetchall()
    columns_dict = {col[1]: col for col in columns}
    
    has_user = 'user_id' in columns_dict
    has_submitter = 'submitter_id' in columns_dict
    
    print(f"Current table structure: user_field_exists={has_user}, submitter_field_exists={has_submitter}")
    
    try:
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Add missing fields if needed
        if not has_submitter and has_user:
            print("Creating submitter_id column")
            # Copy user_id to submitter_id
            conn.execute("ALTER TABLE feedback_feedback ADD COLUMN submitter_id INTEGER REFERENCES accounts_user(id)")
            conn.execute("UPDATE feedback_feedback SET submitter_id = user_id")
        
        # Add priority field if it doesn't exist
        cursor.execute("SELECT name FROM pragma_table_info('feedback_feedback') WHERE name='priority'")
        if not cursor.fetchone():
            print("Adding priority field")
            conn.execute("ALTER TABLE feedback_feedback ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'")
        
        # Add resolved_at field if it doesn't exist
        cursor.execute("SELECT name FROM pragma_table_info('feedback_feedback') WHERE name='resolved_at'")
        if not cursor.fetchone():
            print("Adding resolved_at field")
            conn.execute("ALTER TABLE feedback_feedback ADD COLUMN resolved_at DATETIME NULL")
        
        # Add assigned_to field if it doesn't exist
        cursor.execute("SELECT name FROM pragma_table_info('feedback_feedback') WHERE name='assigned_to_id'")
        if not cursor.fetchone():
            print("Adding assigned_to_id field")
            conn.execute("ALTER TABLE feedback_feedback ADD COLUMN assigned_to_id INTEGER REFERENCES accounts_user(id)")
        
        # Change rating to allow NULL
        try:
            print("Modifying rating to allow NULL values")
            conn.execute("ALTER TABLE feedback_feedback RENAME TO feedback_feedback_old")
            conn.execute("""
                CREATE TABLE feedback_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(200) NOT NULL,
                    content TEXT NOT NULL,
                    rating INTEGER NULL,
                    status VARCHAR(20) NOT NULL,
                    is_anonymous BOOL NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    category_id INTEGER NOT NULL REFERENCES feedback_feedbackcategory(id),
                    submitter_id INTEGER NOT NULL REFERENCES accounts_user(id),
                    attachment VARCHAR(100) NULL,
                    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                    resolved_at DATETIME NULL,
                    assigned_to_id INTEGER NULL REFERENCES accounts_user(id)
                )
            """)
            
            # Copy data from old table to new one
            if has_user and not has_submitter:
                print("Copying data with user_id as submitter_id")
                conn.execute("""
                    INSERT INTO feedback_feedback (
                        id, title, content, rating, status, is_anonymous, 
                        created_at, updated_at, category_id, submitter_id, attachment,
                        priority, resolved_at, assigned_to_id
                    )
                    SELECT 
                        id, title, content, rating, status, is_anonymous, 
                        created_at, updated_at, category_id, user_id, attachment,
                        'medium', NULL, NULL
                    FROM feedback_feedback_old
                """)
            else:
                print("Copying data with existing submitter_id")
                conn.execute("""
                    INSERT INTO feedback_feedback (
                        id, title, content, rating, status, is_anonymous, 
                        created_at, updated_at, category_id, submitter_id, attachment,
                        priority, resolved_at, assigned_to_id
                    )
                    SELECT 
                        id, title, content, rating, status, is_anonymous, 
                        created_at, updated_at, category_id, submitter_id, attachment,
                        'medium', NULL, NULL
                    FROM feedback_feedback_old
                """)
            
            # Drop old table
            conn.execute("DROP TABLE feedback_feedback_old")
            
        except sqlite3.OperationalError as e:
            print(f"Error modifying table: {e}")
            conn.rollback()
            raise
        
        # Commit transaction
        conn.commit()
        print("Database updated successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_feedback_table() 