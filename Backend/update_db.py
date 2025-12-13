from app import create_app
from database import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Checking database schema...")
    
    # 1. Add SystemLog table
    print("Creating SystemLog table if not exists...")
    db.create_all() # This creates any missing tables (like SystemLog)
    
    # 2. Add is_admin column to User if missing
    print("Checking for is_admin column...")
    inspector = db.inspect(db.engine)
    columns = [c['name'] for c in inspector.get_columns('user')]
    
    if 'is_admin' not in columns:
        print("Adding is_admin column to user table...")
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
            conn.commit()
        print("Column added.")
    else:
        print("is_admin column already exists.")

    print("Database update complete.")
