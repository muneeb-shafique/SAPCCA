from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Class, ClassMember, Group, GroupMember, Assignment, AssignmentSubmission, SystemLog, FriendRequest
from database import db
from datetime import datetime, timedelta
import sys
import os

# Ensure Backend root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import db
from datetime import datetime, timedelta
import sys
import os
import io
from flask import send_file

# Ensure Backend root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DSA.performance import generate_performance_graphs
from DSA.report_generator import generate_class_report

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

# ====== TEACHER DASHBOARD ======

@classes_bp.get("/dashboard-stats")
@jwt_required()
def get_teacher_dashboard_stats():
    """Get aggregated stats for the teacher dashboard"""
    uid = int(get_jwt_identity())
    
    # 1. Verify Faculty
    if not validate_faculty(uid):
        return jsonify({"error": "Dashboard restricted to faculty"}), 403

    # 2. Key Metrics
    # Active Classes (created by me or moderator of)
    my_class_ids = [m.class_id for m in ClassMember.query.filter_by(user_id=uid, is_moderator=True).all()]
    active_classes_count = len(my_class_ids)

    # Enrolled Students (unique students in my classes)
    # Get all members of his classes, excluding himself
    all_members = ClassMember.query.filter(ClassMember.class_id.in_(my_class_ids)).filter(ClassMember.user_id != uid).all()
    unique_student_ids = set(m.user_id for m in all_members)
    enrolled_students_count = len(unique_student_ids)

    # Pending Requests (Friend requests for now, or could be class join requests if implemented)
    pending_requests = FriendRequest.query.filter_by(receiver_id=uid, status='pending').count()

    # System Health (Fake/Mock or real uptime if tracked)
    system_health = "99.9%" 

    # 3. Class Performance (DSA Graphs)
    # Generate graphs specific to this teacher
    performance_graphs = generate_performance_graphs(teacher_id=uid)

    # 4. System Alerts (Recent Logs relevant to security/system)
    # define some keywords or levels
    alerts = []
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(10).all()
    for log in logs:
        alerts.append({
            "level": log.level, # INFO, WARNING, ERROR
            "message": log.message,
            "timestamp": log.timestamp.strftime("%H:%M:%S"),
            "time_ago": "Just now" # simplified
        })

    # 5. Live Activity Feed (Mocked based on recent submissions/actions if available, or logs)
    # Let's use recent assignment submissions for this teacher's classes
    activity_feed = []
    if my_class_ids:
        # Find assignments in these classes
        class_assigns = Assignment.query.filter(Assignment.class_id.in_(my_class_ids)).all()
        class_assign_ids = [a.id for a in class_assigns]
        
        # Recent submissions
        recent_subs = AssignmentSubmission.query.filter(AssignmentSubmission.assignment_id.in_(class_assign_ids))\
            .order_by(AssignmentSubmission.submitted_at.desc()).limit(5).all()
        
        for sub in recent_subs:
            student = User.query.get(sub.student_id)
            assign = Assignment.query.get(sub.assignment_id)
            activity_feed.append({
                "time": sub.submitted_at.strftime("%H:%M"),
                "text": f"User {student.display_name if student else 'Unknown'} submitted {assign.title if assign else 'Assignment'}",
                "type": "success"
            })

    return jsonify({
        "metrics": {
            "active_classes": active_classes_count,
            "enrolled_students": enrolled_students_count,
            "pending_requests": pending_requests,
            "system_health": system_health
        },
        "graphs": performance_graphs,
        "alerts": alerts,
        "activity_feed": activity_feed
    })

# ====== QUICK ACTIONS & MODULE DIRECTORY HELPER ======

@classes_bp.post("/enroll-student")
@jwt_required()
def quick_enroll_student():
    """Enroll a student by ID or Email into a class"""
    uid = int(get_jwt_identity())
    data = request.json
    
    if not validate_faculty(uid):
        return jsonify({"error": "Unauthorized"}), 403

    class_code = data.get('class_code') # e.g. "CS-201" (assuming name is code or mapping exists)
    student_identifier = data.get('student_id') # ID or Email

    # 1. Find Class
    # Simplification: We'll assume class name matches code for now or try to finding loosely
    target_class = Class.query.filter(Class.name.ilike(f"%{class_code}%")).first()
    if not target_class:
        return jsonify({"error": f"Class '{class_code}' not found"}), 404
        
    # Check if teacher owns or mods this class
    if not is_class_moderator(target_class.id, uid):
        return jsonify({"error": "You do not manage this class"}), 403

    # 2. Find Student
    student = User.query.filter((User.id == student_identifier) | (User.email == student_identifier)).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    # 3. Add Member
    existing = ClassMember.query.filter_by(class_id=target_class.id, user_id=student.id).first()
    if existing:
        return jsonify({"error": "Student already enrolled"}), 400

    new_member = ClassMember(class_id=target_class.id, user_id=student.id)
    db.session.add(new_member)
    db.session.commit()

    return jsonify({"message": f"Successfully enrolled {student.display_name} into {target_class.name}"}), 200

@classes_bp.get("/generate-report/<int:class_id>")
@jwt_required()
def generate_report(class_id):
    """Generate PDF report for a class"""
    uid = int(get_jwt_identity())
    
    # Validate
    if not is_class_moderator(class_id, uid):
        return jsonify({"error": "Unauthorized"}), 403
    
    c = Class.query.get(class_id)
    members = [User.query.get(m.user_id) for m in ClassMember.query.filter_by(class_id=class_id).all()]
    assignments = Assignment.query.filter_by(class_id=class_id).all()
    
    # Calculate simple stats
    submissions = AssignmentSubmission.query.filter(AssignmentSubmission.assignment_id.in_([a.id for a in assignments])).all() if assignments else []
    avg_grade = sum(s.grade or 0 for s in submissions) / len(submissions) if submissions else 0
    
    perf_data = {"average_grade": f"{avg_grade:.2f}"}

    pdf_buffer = generate_class_report(c, members, assignments, perf_data)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Report_{c.name}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mimetype='application/pdf'
    )

@classes_bp.post("/broadcast-alert")
@jwt_required()
def broadcast_alert():
    """Create a System Log entry as an 'Alert' (Mock broadcast)"""
    uid = int(get_jwt_identity())
    if not validate_faculty(uid): return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    msg = data.get("message")
    level = data.get("level", "WARNING")
    
    if not msg: return jsonify({"error": "Message required"}), 400
    
    new_log = SystemLog(level=level, message=f"[BROADCAST by User {uid}]: {msg}")
    db.session.add(new_log)
    db.session.commit()
    
    return jsonify({"message": "Alert broadcasted to system logs"}), 200

@classes_bp.post("/revoke-access")
@jwt_required()
def revoke_access():
    """Revoke a user's access to a class"""
    uid = int(get_jwt_identity())
    if not validate_faculty(uid): return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    student_id = data.get('student_id')
    class_code = data.get('class_code')
    
    target_class = Class.query.filter(Class.name.ilike(f"%{class_code}%")).first()
    if not target_class: return jsonify({"error": "Class not found"}), 404
    
    if not is_class_moderator(target_class.id, uid): return jsonify({"error": "Unauthorized"}), 403
    
    member = ClassMember.query.filter_by(class_id=target_class.id, user_id=student_id).first()
    if not member: return jsonify({"error": "Student not in class"}), 404
    
    db.session.delete(member)
    db.session.commit()
    
    return jsonify({"message": "Access revoked successfully"}), 200
