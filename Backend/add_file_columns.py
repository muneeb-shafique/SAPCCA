"""
Quick fix to add file columns to message table
Run this script to add the missing columns
"""
from app import create_app
from database import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if columns already exist
        result = db.session.execute(text("PRAGMA table_info(message)"))
        columns = [row[1] for row in result]
        
        print("Current columns in message table:", columns)
        
        # Add missing columns
        if 'file_data' not in columns:
            db.session.execute(text("ALTER TABLE message ADD COLUMN file_data TEXT"))
            print("✓ Added file_data column")
        else:
            print("✓ file_data column already exists")
            
        if 'file_name' not in columns:
            db.session.execute(text("ALTER TABLE message ADD COLUMN file_name VARCHAR(255)"))
            print("✓ Added file_name column")
        else:
            print("✓ file_name column already exists")
            
        if 'file_type' not in columns:
            db.session.execute(text("ALTER TABLE message ADD COLUMN file_type VARCHAR(50)"))
            print("✓ Added file_type column")
        else:
            print("✓ file_type column already exists")
            
        if 'file_category' not in columns:
            db.session.execute(text("ALTER TABLE message ADD COLUMN file_category VARCHAR(20)"))
            print("✓ Added file_category column")
        else:
            print("✓ file_category column already exists")
        
        db.session.commit()
        print("\n✅ Database updated successfully!")
        
        # Verify
        result = db.session.execute(text("PRAGMA table_info(message)"))
        columns = [row[1] for row in result]
        print("\nFinal columns:", columns)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()
