from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Class, ClassMember, Group, GroupMember
from database import db
from datetime import datetime

classes_bp = Blueprint("classes", __name__)

# ====== HELPER FUNCTIONS ======

def validate_faculty(user_id):
    """Check if user is faculty"""
    user = User.query.get(user_id)
    return user and user.role in ['faculty', 'teacher', 'professor', 'admin']

def is_class_moderator(class_id, user_id):
    """Check if user is a moderator of the class"""
    membership = ClassMember.query.filter_by(class_id=class_id, user_id=user_id).first()
    return membership and (membership.is_moderator or validate_faculty(user_id))

# ====== CLASS MANAGEMENT ======

@classes_bp.post("/create")
@jwt_required()
def create_class():
    """Create a new class (faculty only)"""
    uid = int(get_jwt_identity())
    
    # Validate faculty permission
    if not validate_faculty(uid):
        return jsonify({"error": "Only faculty can create classes"}), 403
    
    data = request.json
    name = data.get("name")
    
    if not name:
        return jsonify({"error": "Class name is required"}), 400
    
    # Create class
    new_class = Class(
        name=name,
        description=data.get("description", ""),
        icon_url=data.get("icon_url", ""),
        created_by=uid
    )
    db.session.add(new_class)
    db.session.commit()
    
    # Add creator as moderator
    creator_member = ClassMember(
        class_id=new_class.id,
        user_id=uid,
        is_moderator=True
    )
    db.session.add(creator_member)
    db.session.commit()
    
    return jsonify({
        "message": "Class created successfully",
        "class_id": new_class.id,
        "name": new_class.name
    }), 201

@classes_bp.get("/list")
@jwt_required()
def list_classes():
    """List all classes user is a member of"""
    uid = int(get_jwt_identity())
    
    # Get user's class memberships
    memberships = ClassMember.query.filter_by(user_id=uid).all()
    classes = []
    
    for m in memberships:
        c = Class.query.get(m.class_id)
        if not c:
            continue
            
        # Count groups in this class
        group_count = Group.query.filter_by(class_id=c.id).count()
        
        # Count members
        member_count = ClassMember.query.filter_by(class_id=c.id).count()
        
        classes.append({
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "icon": c.icon_url,
            "created_by": c.created_by,
            "created_at": c.created_at.isoformat(),
            "is_moderator": m.is_moderator,
            "group_count": group_count,
            "member_count": member_count
        })
    
    return jsonify({"classes": classes}), 200

@classes_bp.get("/<int:class_id>")
@jwt_required()
def get_class_details(class_id):
    """Get detailed information about a class"""
    uid = int(get_jwt_identity())
    
    # Check membership
    membership = ClassMember.query.filter_by(class_id=class_id, user_id=uid).first()
    if not membership:
        return jsonify({"error": "Access denied"}), 403
    
    c = Class.query.get(class_id)
    if not c:
        return jsonify({"error": "Class not found"}), 404
    
    # Get groups in this class
    groups = Group.query.filter_by(class_id=class_id).all()
    group_list = []
    for g in groups:
        member_count = GroupMember.query.filter_by(group_id=g.id).count()
        # Check if user is member of this group
        user_membership = GroupMember.query.filter_by(group_id=g.id, user_id=uid).first()
        
        group_list.append({
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "image": g.image_url,
            "member_count": member_count,
            "is_member": user_membership is not None,
            "is_admin": user_membership.is_admin if user_membership else False
        })
    
    # Get members
    members = ClassMember.query.filter_by(class_id=class_id).all()
    member_list = []
    for m in members:
        user = User.query.get(m.user_id)
        if user:
            member_list.append({
                "id": user.id,
                "name": user.display_name,
                "email": user.email,
                "role": user.role,
                "is_moderator": m.is_moderator,
                "joined_at": m.joined_at.isoformat()
            })
    
    return jsonify({
        "class": {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "icon": c.icon_url,
            "created_by": c.created_by,
            "created_at": c.created_at.isoformat(),
            "is_moderator": membership.is_moderator
        },
        "groups": group_list,
        "members": member_list
    }), 200

@classes_bp.put("/<int:class_id>")
@jwt_required()
def update_class(class_id):
    """Update class information (moderators only)"""
    uid = int(get_jwt_identity())
    
    # Check moderator permission
    if not is_class_moderator(class_id, uid):
        return jsonify({"error": "Moderator access required"}), 403
    
    c = Class.query.get(class_id)
    if not c:
        return jsonify({"error": "Class not found"}), 404
    
    data = request.json
    
    if "name" in data:
        c.name = data["name"]
    if "description" in data:
        c.description = data["description"]
    if "icon_url" in data:
        c.icon_url = data["icon_url"]
    
    db.session.commit()
    
    return jsonify({"message": "Class updated successfully"}), 200

@classes_bp.post("/add-members")
@jwt_required()
def add_class_members():
    """Add multiple members to a class"""
    uid = int(get_jwt_identity())
    data = request.json
    
    class_id = data.get("class_id")
    emails = data.get("emails", [])
    make_moderator = data.get("is_moderator", False)
    
    if not class_id:
        return jsonify({"error": "class_id required"}), 400
    
    # Check moderator permission
    if not is_class_moderator(class_id, uid):
        return jsonify({"error": "Moderator access required"}), 403
    
    added_count = 0
    errors = []
    
    for email in emails:
        user = User.query.filter_by(email=email.strip()).first()
        if not user:
            errors.append(f"User not found: {email}")
            continue
        
        # Check if already member
        existing = ClassMember.query.filter_by(class_id=class_id, user_id=user.id).first()
        if existing:
            errors.append(f"Already member: {email}")
            continue
        
        # Add member
        new_member = ClassMember(
            class_id=class_id,
            user_id=user.id,
            is_moderator=make_moderator
        )
        db.session.add(new_member)
        added_count += 1
    
    db.session.commit()
    
    return jsonify({
        "message": f"Added {added_count} member(s)",
        "added": added_count,
        "errors": errors
    }), 200

@classes_bp.delete("/<int:class_id>/members/<int:user_id>")
@jwt_required()
def remove_class_member(class_id, user_id):
    """Remove a member from a class"""
    uid = int(get_jwt_identity())
    
    # Check moderator permission or self-removal
    if not is_class_moderator(class_id, uid) and uid != user_id:
        return jsonify({"error": "Moderator access required"}), 403
    
    member = ClassMember.query.filter_by(class_id=class_id, user_id=user_id).first()
    if not member:
        return jsonify({"error": "Member not found"}), 404
    
    db.session.delete(member)
    db.session.commit()
    
    return jsonify({"message": "Member removed successfully"}), 200

@classes_bp.delete("/<int:class_id>")
@jwt_required()
def delete_class(class_id):
    """Delete a class (creator only)"""
    uid = int(get_jwt_identity())
    
    c = Class.query.get(class_id)
    if not c:
        return jsonify({"error": "Class not found"}), 404
    
    # Only creator can delete
    if c.created_by != uid:
        return jsonify({"error": "Only creator can delete class"}), 403
    
    # Delete all members
    ClassMember.query.filter_by(class_id=class_id).delete()
    
    # Delete all groups in class (and their members)
    groups = Group.query.filter_by(class_id=class_id).all()
    for g in groups:
        GroupMember.query.filter_by(group_id=g.id).delete()
        db.session.delete(g)
    
    # Delete class
    db.session.delete(c)
    db.session.commit()
    
    return jsonify({"message": "Class deleted successfully"}), 200
