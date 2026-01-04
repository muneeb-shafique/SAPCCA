from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Group, GroupMember, GroupMessage, ClassMember
from database import db
from datetime import datetime
import sys
import os
import base64



groups_bp = Blueprint("groups", __name__)

# --- Group Management ---

@groups_bp.post("/create")
@jwt_required()
def create_group():
    uid = int(get_jwt_identity())
    data = request.json
    
    name = data.get("name")
    if not name:
        return jsonify({"error": "Group name is required"}), 400
    
    class_id = data.get("class_id")  # Optional parent class
    
    # If creating group in a class, verify moderator permission
    if class_id:
        membership = ClassMember.query.filter_by(class_id=class_id, user_id=uid).first()
        if not membership or not membership.is_moderator:
            return jsonify({"error": "Must be class moderator to create groups"}), 403

    new_group = Group(
        name=name,
        description=data.get("description", ""),
        image_url=data.get("image_url", ""),
        created_by=uid,
        class_id=class_id  # Link to parent class if provided
    )
    db.session.add(new_group)
    db.session.commit()

    # Add creator as admin
    member = GroupMember(group_id=new_group.id, user_id=uid, is_admin=True)
    db.session.add(member)
    db.session.commit()

    return jsonify({"message": "Group created", "group_id": new_group.id}), 201

@groups_bp.get("/list")
@jwt_required()
def list_my_groups():
    uid = int(get_jwt_identity())
    
    # Query groups where user is a member
    memberships = GroupMember.query.filter_by(user_id=uid).all()
    groups = []
    
    for m in memberships:
        g = Group.query.get(m.group_id)
        if g:
            groups.append({
                "id": g.id,
                "name": g.name,
                "description": g.description,
                "image": g.image_url,
                "is_admin": m.is_admin,
                "class_id": g.class_id  # Include parent class info
            })
            
    return jsonify({"groups": groups}), 200

@groups_bp.post("/add-member")
@jwt_required()
def add_member():
    uid = int(get_jwt_identity())
    data = request.json
    
    group_id = data.get("group_id")
    target_email = data.get("email") # Changed from user_id to email for better UX
    
    if not target_email:
        return jsonify({"error": "Email is required"}), 400

    target_user = User.query.filter_by(email=target_email).first()
    if not target_user:
        return jsonify({"error": "User with this email not found"}), 404

    target_user_id = target_user.id

    # Verify requester is admin or member (allow members to add for now)
    requester_membership = GroupMember.query.filter_by(group_id=group_id, user_id=uid).first()
    if not requester_membership:
        return jsonify({"error": "You are not in this group"}), 403

    existing = GroupMember.query.filter_by(group_id=group_id, user_id=target_user_id).first()
    if existing:
        return jsonify({"error": "User already in group"}), 409

    new_member = GroupMember(group_id=group_id, user_id=target_user_id)
    db.session.add(new_member)
    db.session.commit()

    return jsonify({"message": "Member added successfully", "user_id": target_user_id, "name": target_user.display_name}), 200

@groups_bp.post("/join")
@jwt_required()
def join_group():
    """Allow class members to auto-join groups that belong to their class"""
    uid = int(get_jwt_identity())
    data = request.json
    
    group_id = data.get("group_id")
    if not group_id:
        return jsonify({"error": "group_id is required"}), 400
    
    # Get the group
    group = Group.query.get(group_id)
    if not group:
        return jsonify({"error": "Group not found"}), 404
    
    # Check if already a member
    existing = GroupMember.query.filter_by(group_id=group_id, user_id=uid).first()
    if existing:
        return jsonify({"message": "Already a member"}), 200
    
    # If group belongs to a class, verify user is a class member
    if group.class_id:
        class_membership = ClassMember.query.filter_by(class_id=group.class_id, user_id=uid).first()
        if not class_membership:
            return jsonify({"error": "You must be a member of this class to join this group"}), 403
        
        # Auto-join: Add user to group
        new_member = GroupMember(group_id=group_id, user_id=uid, is_admin=False)
        db.session.add(new_member)
        db.session.commit()
        return jsonify({"message": "Successfully joined group"}), 200
    else:
        # For non-class groups, require existing membership to add
        return jsonify({"error": "This group requires an invitation"}), 403

@groups_bp.get("/members/<int:group_id>")
@jwt_required()
def get_group_members(group_id):
    uid = int(get_jwt_identity())
    
    # Check access
    if not GroupMember.query.filter_by(group_id=group_id, user_id=uid).first():
        return jsonify({"error": "Access denied"}), 403
        
    members = GroupMember.query.filter_by(group_id=group_id).all()
    results = []
    
    for m in members:
        u = User.query.get(m.user_id)
        if u:
            results.append({
                "id": u.id,
                "name": u.display_name,
                "email": u.email,
                "avatar": u.avatar_url,
                "role": u.role,
                "is_admin": m.is_admin,
                "joined_at": m.joined_at.isoformat()
            })
            
    return jsonify({"members": results}), 200

# --- Messaging ---

@groups_bp.get("/messages/<int:group_id>")
@jwt_required()
def get_messages(group_id):
    uid = int(get_jwt_identity())
    
    # Check membership
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=uid).first()
    if not membership:
        return jsonify({"error": "Access denied"}), 403

    msgs = GroupMessage.query.filter_by(group_id=group_id).order_by(GroupMessage.timestamp.asc()).all()
    
    results = []
    for m in msgs:
        sender = User.query.get(m.sender_id)
        
        # Get reply-to message if exists
        reply_data = None
        if m.reply_to_id:
            reply_msg = GroupMessage.query.get(m.reply_to_id)
            if reply_msg:
                reply_sender = User.query.get(reply_msg.sender_id)
                reply_data = {
                    "id": reply_msg.id,
                    "text": reply_msg.text,
                    "sender_name": reply_sender.display_name if reply_sender else "Unknown",
                    "has_voice": bool(reply_msg.voice_data),
                    "has_file": bool(reply_msg.file_data)
                }
        
        results.append({
            "id": m.id,
            "text": m.text,
            "sender_id": m.sender_id,
            "sender_name": sender.display_name if sender else "Unknown",
            "sender_avatar": sender.avatar_url if sender else "",
            "time": m.timestamp.isoformat(),
            "file_data": m.file_data,
            "file_name": m.file_name,
            "file_type": m.file_type,
            "voice_data": m.voice_data,
            "voice_duration": m.voice_duration,
            "reply_to": reply_data
        })

    return jsonify({"messages": results}), 200

@groups_bp.post("/send")
@jwt_required()
def send_message():
    uid = int(get_jwt_identity())
    data = request.json
    
    group_id = data.get("group_id")
    text = data.get("message")
    file_data = data.get("file_data")
    file_type = data.get("file_type")
    
    # --- ML CONTENT MODERATION - REMOVED ---
    # moderator.initialize() # Ensure models are loaded
    
    # Text Check
    # if text:
    #     is_safe, reason = moderator.check_text(text)
    #     if not is_safe:
    #         return jsonify({"error": reason}), 400

    # Image Check
    # if file_data and file_type and ("image" in file_type):
    #     try:
    #         if "," in file_data:
    #             _, encoded = file_data.split(",", 1)
    #         else:
    #             encoded = file_data
    #         image_bytes = base64.b64decode(encoded)
    #         
    #         is_safe, reason = moderator.check_image(image_bytes)
    #         if not is_safe:
    #             return jsonify({"error": reason}), 400
    #     except Exception as e:
    #         print(f"Group Image Mod Error: {e}")
    # -----------------------------
    
    # Check membership
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=uid).first()
    if not membership:
        return jsonify({"error": "Access denied"}), 403

    msg = GroupMessage(
        group_id=group_id,
        sender_id=uid,
        text=text,
        file_data=data.get("file_data"),
        file_name=data.get("file_name"),
        file_type=data.get("file_type"),
        voice_data=data.get("voice_data"),
        voice_duration=data.get("voice_duration"),
        reply_to_id=data.get("reply_to_id")
    )
    
    db.session.add(msg)
    db.session.commit()
    

    return jsonify({"message": "Sent", "id": msg.id}), 201

# --- Advanced Management ---

@groups_bp.put("/<int:group_id>")
@jwt_required()
def update_group(group_id):
    uid = int(get_jwt_identity())
    data = request.json
    
    # Check Admin Access
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=uid).first()
    if not membership or not membership.is_admin:
        return jsonify({"error": "Admin access required"}), 403

    group = Group.query.get(group_id)
    if not group:
        return jsonify({"error": "Group not found"}), 404
        
    if "name" in data:
        group.name = data["name"]
    if "description" in data:
        group.description = data["description"]
    if "image_url" in data:
        group.image_url = data["image_url"]
        
    db.session.commit()
    return jsonify({"message": "Group updated"}), 200

@groups_bp.delete("/<int:group_id>/members/<int:user_id>")
@jwt_required()
def remove_member(group_id, user_id):
    uid = int(get_jwt_identity())
    
    # Check Requester Admin Access
    requester = GroupMember.query.filter_by(group_id=group_id, user_id=uid).first()
    if not requester or not requester.is_admin:
        # Allow self-leave (if uid == user_id)
        if uid != user_id:
            return jsonify({"error": "Admin access required"}), 403

    member_to_remove = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member_to_remove:
        return jsonify({"error": "Member not found"}), 404
        
    db.session.delete(member_to_remove)
    db.session.commit()
    return jsonify({"message": "Member removed"}), 200

@groups_bp.delete("/messages/<int:message_id>")
@jwt_required()
def delete_group_message(message_id):
    """Delete a group message (only sender can delete)"""
    uid = int(get_jwt_identity())
    
    msg = GroupMessage.query.get(message_id)
    if not msg:
        return jsonify({"error": "Message not found"}), 404
    
    # Verify sender
    if msg.sender_id != uid:
        return jsonify({"error": "Unauthorized"}), 403
    
    db.session.delete(msg)
    db.session.commit()
    
    return jsonify({"message": "Message deleted"}), 200
