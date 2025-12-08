"""
Quick fix script to add registration_number column to database
Run this with: python add_registration_number_column.py
"""
import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'sapcca.db')

if not os.path.exists(db_path):
    print(f"Database not found at: {db_path}")
    print("Please check the database location.")
    exit(1)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column already exists
    cursor.execute("PRAGMA table_info(user)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'registration_number' in columns:
        print("✅ Column 'registration_number' already exists!")
    else:
        # Add the column
        cursor.execute('ALTER TABLE user ADD COLUMN registration_number VARCHAR(50)')
        conn.commit()
        print("✅ Successfully added 'registration_number' column to user table!")
        
        # Note: SQLite doesn't support adding UNIQUE constraints to existing tables directly
        # We'll handle uniqueness at the application level for now
        print("⚠️  Note: SQLite limitation - UNIQUE constraint will be enforced by the application")
    
except sqlite3.Error as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("\n✅ Done! You can now restart your Flask server and try logging in again.")
