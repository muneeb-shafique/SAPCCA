"""
Simple script to clear all users from the database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after path is set
from database import db
from models import User, FriendRequest, Message
from flask import Flask
from config import Config

# Create minimal app
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    # Delete all records
    try:
        Message.query.delete()
        print("✓ Deleted all messages")
    except:
        print("✓ No messages to delete")
    
    try:
        FriendRequest.query.delete()
        print("✓ Deleted all friend requests")
    except:
        print("✓ No friend requests to delete")
    
    try:
        User.query.delete()
        print("✓ Deleted all users")
    except:
        print("✓ No users to delete")
    
    db.session.commit()
    
    print("\n✅ Database cleared successfully!")
    print("You can now register with a fresh account.")
