from flask import Blueprint, request, jsonify
from models import User
from database import db
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random

auth_bp = Blueprint("auth", __name__)

# In-memory storage for pending registrations (before OTP verification)
pending_registrations = {}

@auth_bp.post("/register")
def register():
    try:
        data = request.json
        email = data["email"]
        
        # Check if user already exists and is verified
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.is_verified:
            return jsonify({"error": "Email already registered"}), 409
        
        # Generate 5-digit OTP
        otp_code = str(random.randint(10000, 99999))
        otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        
        # Store registration data temporarily (NOT in database yet)
        pending_registrations[email] = {
            "name": data["name"],
            "registration_number": data.get("registration_number"),  # Optional field
            "password": data["password"],  # Will be hashed on verification
            "otp_code": otp_code,
            "otp_expiry": otp_expiry
        }
        
        # Print OTP to console (in production, send via email)
        print(f"\n{'='*50}")
        print(f"OTP for {email}: {otp_code}")
        print(f"Expires at: {otp_expiry}")
        print(f"{'='*50}\n")
        
        return jsonify({
            "message": "OTP sent to console (check terminal)",
            "email": email
        }), 201
        
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.post("/verify-otp")
def verify_otp():
    try:
        data = request.json
        email = data["email"]
        otp = data["otp"]
        
        # Check if registration is pending
        if email not in pending_registrations:
            return jsonify({"error": "No pending registration for this email"}), 404
        
        pending = pending_registrations[email]
        
        # Check OTP expiry
        if datetime.utcnow() > pending["otp_expiry"]:
            del pending_registrations[email]
            return jsonify({"error": "OTP expired. Please register again."}), 400
        
        # Verify OTP
        if pending["otp_code"] != otp:
            return jsonify({"error": "Invalid OTP"}), 400
        
        # OTP is valid - NOW create the user account
        hashed_password = generate_password_hash(pending["password"])
        
        # Delete old unverified account if exists
        old_user = User.query.filter_by(email=email).first()
        if old_user:
            db.session.delete(old_user)
        
        user = User(
            email=email,
            password=hashed_password,
            display_name=pending["name"],
            registration_number=pending.get("registration_number"),
            is_verified=True,
            otp_code=None,
            otp_expiry=None
        )
        db.session.add(user)
        db.session.commit()
        
        # Remove from pending
        del pending_registrations[email]
        
        # Generate token
        token = create_access_token(identity=str(user.id))
        
        return jsonify({
            "message": "Account created successfully",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.display_name,
                "email": user.email
            }
        }), 200
        
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.post("/login")
def login():
    try:
        data = request.json
        user = User.query.filter_by(email=data["email"]).first()

        if not user or not check_password_hash(user.password, data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401
        
        if not user.is_verified:
            return jsonify({"error": "Account not verified. Please verify your OTP."}), 403

        token = create_access_token(identity=str(user.id))
        return jsonify({
            "token": token, 
            "user": {
                "id": user.id, 
                "name": user.display_name,
                "email": user.email
            }
        }), 200
        
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
