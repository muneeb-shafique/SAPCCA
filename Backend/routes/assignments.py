from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Assignment, AssignmentSubmission, User, ClassMember
from database import db
from datetime import datetime

assignments_bp = Blueprint("assignments", __name__)

# --- Assignment Management ---

@assignments_bp.post("/create")
@jwt_required()
def create_assignment():
    """Faculty creates an assignment for their class"""
    uid = int(get_jwt_identity())
    data = request.json
    
    class_id = data.get("class_id")
    title = data.get("title")
    description = data.get("description", "")
    due_date_str = data.get("due_date")
    total_points = data.get("total_points", 100)
    
    if not all([class_id, title, due_date_str]):
        return jsonify({"error": "class_id, title, and due_date are required"}), 400
    
    # Verify user is a moderator of this class
    membership = ClassMember.query.filter_by(class_id=class_id, user_id=uid).first()
    if not membership or not membership.is_moderator:
        return jsonify({"error": "Must be class moderator to create assignments"}), 403
    
    # Parse due date
    try:
        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
    except:
        return jsonify({"error": "Invalid due_date format. Use ISO format"}), 400
    
    new_assignment = Assignment(
        class_id=class_id,
        title=title,
        description=description,
        due_date=due_date,
        total_points=total_points,
        created_by=uid,
        file_data=data.get("file_data"),
        file_name=data.get("file_name"),
        file_type=data.get("file_type")
    )
    
    db.session.add(new_assignment)
    db.session.commit()
    
    return jsonify({"message": "Assignment created", "assignment_id": new_assignment.id}), 201

@assignments_bp.get("/class/<int:class_id>")
@jwt_required()
def list_class_assignments(class_id):
    """Get all assignments for a class"""
    uid = int(get_jwt_identity())
    
    # Verify user is a member of this class
    membership = ClassMember.query.filter_by(class_id=class_id, user_id=uid).first()
    if not membership:
        return jsonify({"error": "Access denied"}), 403
    
    assignments = Assignment.query.filter_by(class_id=class_id).order_by(Assignment.due_date.asc()).all()
    
    results = []
    for a in assignments:
        # Check if current user has submitted
        submission = AssignmentSubmission.query.filter_by(assignment_id=a.id, student_id=uid).first()
        
        results.append({
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "due_date": a.due_date.isoformat(),
            "total_points": a.total_points,
            "created_at": a.created_at.isoformat(),
            "has_file": bool(a.file_data),
            "file_name": a.file_name,
            # Student-specific fields
            "submitted": bool(submission),
            "grade": submission.grade if submission else None,
            "submission_time": submission.submitted_at.isoformat() if submission else None
        })
    
    return jsonify({"assignments": results}), 200

@assignments_bp.get("/<int:assignment_id>")
@jwt_required()
def get_assignment_details(assignment_id):
    """Get detailed information about an assignment"""
    uid = int(get_jwt_identity())
    
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404
    
    # Verify access
    membership = ClassMember.query.filter_by(class_id=assignment.class_id, user_id=uid).first()
    if not membership:
        return jsonify({"error": "Access denied"}), 403
    
    # Get submission if student
    submission = AssignmentSubmission.query.filter_by(assignment_id=assignment_id, student_id=uid).first()
    
    return jsonify({
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "due_date": assignment.due_date.isoformat(),
        "total_points": assignment.total_points,
        "created_at": assignment.created_at.isoformat(),
        "file_data": assignment.file_data,
        "file_name": assignment.file_name,
        "file_type": assignment.file_type,
        "submission": {
            "submitted": bool(submission),
            "grade": submission.grade if submission else None,
            "feedback": submission.feedback if submission else None,
            "submitted_at": submission.submitted_at.isoformat() if submission else None
        } if submission else None
    }), 200

# --- Submissions ---

@assignments_bp.post("/<int:assignment_id>/submit")
@jwt_required()
def submit_assignment(assignment_id):
    """Student submits work for an assignment"""
    uid = int(get_jwt_identity())
    data = request.json
    
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404
    
    # Verify student is in class
    membership = ClassMember.query.filter_by(class_id=assignment.class_id, user_id=uid).first()
    if not membership:
        return jsonify({"error": "Access denied"}), 403
    
    # Check if already submitted
    existing = AssignmentSubmission.query.filter_by(assignment_id=assignment_id, student_id=uid).first()
    if existing:
        # Update existing submission
        existing.file_data = data.get("file_data")
        existing.file_name = data.get("file_name")
        existing.file_type = data.get("file_type")
        existing.text_response = data.get("text_response", "")
        existing.submitted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"message": "Submission updated"}), 200
    
    # Create new submission
    submission = AssignmentSubmission(
        assignment_id=assignment_id,
        student_id=uid,
        file_data=data.get("file_data"),
        file_name=data.get("file_name"),
        file_type=data.get("file_type"),
        text_response=data.get("text_response", "")
    )
    
    db.session.add(submission)
    db.session.commit()
    
    return jsonify({"message": "Assignment submitted successfully"}), 201

@assignments_bp.get("/<int:assignment_id>/submissions")
@jwt_required()
def get_assignment_submissions(assignment_id):
    """Faculty views all submissions for an assignment"""
    uid = int(get_jwt_identity())
    
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404
    
    # Verify user is moderator
    membership = ClassMember.query.filter_by(class_id=assignment.class_id, user_id=uid).first()
    if not membership or not membership.is_moderator:
        return jsonify({"error": "Moderator access required"}), 403
    
    # Get all class members (students)
    class_members = ClassMember.query.filter_by(class_id=assignment.class_id).all()
    
    results = []
    for member in class_members:
        if member.is_moderator:
            continue  # Skip moderators
        
        student = User.query.get(member.user_id)
        submission = AssignmentSubmission.query.filter_by(assignment_id=assignment_id, student_id=member.user_id).first()
        
        results.append({
            "student_id": student.id,
            "student_name": student.display_name,
            "student_email": student.email,
            "submitted": bool(submission),
            "submission_time": submission.submitted_at.isoformat() if submission else None,
            "is_late": (submission.submitted_at > assignment.due_date) if submission else False,
            "grade": submission.grade if submission else None,
            "feedback": submission.feedback if submission else None,
            "file_name": submission.file_name if submission else None
        })
    
    return jsonify({"submissions": results}), 200

@assignments_bp.get("/<int:assignment_id>/submissions/<int:student_id>")
@jwt_required()
def get_student_submission(assignment_id, student_id):
    """Faculty gets a specific student's submission file"""
    uid = int(get_jwt_identity())
    
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404
    
    # Verify user is moderator
    membership = ClassMember.query.filter_by(class_id=assignment.class_id, user_id=uid).first()
    if not membership or not membership.is_moderator:
        return jsonify({"error": "Moderator access required"}), 403
    
    submission = AssignmentSubmission.query.filter_by(assignment_id=assignment_id, student_id=student_id).first()
    if not submission:
        return jsonify({"error": "Submission not found"}), 404
    
    return jsonify({
        "file_data": submission.file_data,
        "file_name": submission.file_name,
        "file_type": submission.file_type,
        "text_response": submission.text_response,
        "submitted_at": submission.submitted_at.isoformat()
    }), 200

@assignments_bp.put("/<int:assignment_id>/submissions/<int:student_id>/grade")
@jwt_required()
def grade_submission(assignment_id, student_id):
    """Faculty grades a student's submission"""
    uid = int(get_jwt_identity())
    data = request.json
    
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404
    
    # Verify user is moderator
    membership = ClassMember.query.filter_by(class_id=assignment.class_id, user_id=uid).first()
    if not membership or not membership.is_moderator:
        return jsonify({"error": "Moderator access required"}), 403
    
    submission = AssignmentSubmission.query.filter_by(assignment_id=assignment_id, student_id=student_id).first()
    if not submission:
        return jsonify({"error": "Submission not found"}), 404
    
    grade = data.get("grade")
    feedback = data.get("feedback", "")
    
    if grade is None:
        return jsonify({"error": "grade is required"}), 400
    
    submission.grade = int(grade)
    submission.feedback = feedback
    submission.graded_at = datetime.utcnow()
    submission.graded_by = uid
    
    db.session.commit()
    
    return jsonify({"message": "Submission graded successfully"}), 200

@assignments_bp.delete("/<int:assignment_id>")
@jwt_required()
def delete_assignment(assignment_id):
    """Faculty deletes an assignment"""
    uid = int(get_jwt_identity())
    
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404
    
    # Verify user is moderator
    membership = ClassMember.query.filter_by(class_id=assignment.class_id, user_id=uid).first()
    if not membership or not membership.is_moderator:
        return jsonify({"error": "Moderator access required"}), 403
    
    # Delete all submissions first
    AssignmentSubmission.query.filter_by(assignment_id=assignment_id).delete()
    
    db.session.delete(assignment)
    db.session.commit()
    
    return jsonify({"message": "Assignment deleted"}), 200
