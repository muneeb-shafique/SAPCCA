from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from database import db

profile_bp = Blueprint("profile", __name__)

@profile_bp.get("/")
@jwt_required()
def profile():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "name": user.display_name,
        "email": user.email,
        "registration_number": user.registration_number,
        "avatar": user.avatar_url,
        "role": user.role,
        "department": user.department,
        "faculty_designation": user.faculty_designation
    }), 200

@profile_bp.post("/update")
@jwt_required()
def update_profile():
    uid = int(get_jwt_identity())
    
    try:
        data = request.json
    except:
        return jsonify({"error": "Invalid request body"}), 400

    user = User.query.get(uid)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Update fields if provided
    if "name" in data:
        user.display_name = data["name"]
    if "avatar" in data:
        user.avatar_url = data["avatar"]

    db.session.commit()
    
    return jsonify({"message": "updated"}), 200
