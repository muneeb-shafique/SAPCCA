from app import create_app
from models import User
from database import db
import sys

def promote_user(email):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_admin = True
            db.session.commit()
            print(f"Successfully promoted {email} to admin.")
        else:
            print(f"User with email {email} not found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <email>")
        print("Existing Users:")
        # List users
        app = create_app()
        with app.app_context():
            users = User.query.all()
            for u in users:
                print(f" - {u.email} (Admin: {u.is_admin})")
    else:
        promote_user(sys.argv[1])
