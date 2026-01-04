from database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    display_name = db.Column(db.String(100))
    registration_number = db.Column(db.String(50), unique=True, nullable=True)
    avatar_url = db.Column(db.String(300), default="")
    otp_code = db.Column(db.String(10), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    # New fields added here:
    role = db.Column(db.String(20), default="student")
    department = db.Column(db.String(100), nullable=True)
    faculty_designation = db.Column(db.String(100), nullable=True)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    image_url = db.Column(db.String(300))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Optional parent class (for subject groups within a class)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)

class Class(db.Model):
    """Represents a class/community containing multiple subject groups"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon_url = db.Column(db.String(500), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ClassMember(db.Model):
    """Represents membership in a class"""
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_moderator = db.Column(db.Boolean, default=False)  # Can create groups, manage members
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

class GroupMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.Text)
    file_data = db.Column(db.Text, nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    file_type = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # Voice message fields
    voice_data = db.Column(db.Text, nullable=True)  # Base64 encoded audio
    voice_duration = db.Column(db.Integer, nullable=True)  # Duration in seconds
    # Reply/threading field
    reply_to_id = db.Column(db.Integer, db.ForeignKey('group_message.id'), nullable=True)

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20))  # INFO, WARNING, ERROR
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer)
    receiver_id = db.Column(db.Integer)
    status = db.Column(db.String(20), default="pending")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer)
    receiver_id = db.Column(db.Integer)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # File attachment fields
    file_data = db.Column(db.Text, nullable=True)  # Base64 encoded file
    file_name = db.Column(db.String(255), nullable=True)  # Original filename
    file_type = db.Column(db.String(50), nullable=True)  # MIME type
    file_category = db.Column(db.String(20), nullable=True)  # document/photo/video/audio
    # Voice message fields
    voice_data = db.Column(db.Text, nullable=True)  # Base64 encoded audio
    voice_duration = db.Column(db.Integer, nullable=True)  # Duration in seconds
    # Reply/threading field
    reply_to_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)

class Assignment(db.Model):
    """Represents an assignment created by faculty for a class"""
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    total_points = db.Column(db.Integer, default=100)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_data = db.Column(db.Text, nullable=True)  # Optional assignment file
    file_name = db.Column(db.String(200), nullable=True)
    file_type = db.Column(db.String(100), nullable=True)

class AssignmentSubmission(db.Model):
    """Represents a student's submission for an assignment"""
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_data = db.Column(db.Text)  # Base64 encoded submission file
    file_name = db.Column(db.String(200))
    file_type = db.Column(db.String(100))
    text_response = db.Column(db.Text)  # Text submission
    grade = db.Column(db.Integer)  # Out of total_points
    feedback = db.Column(db.Text)  # Teacher feedback
    graded_at = db.Column(db.DateTime)
    graded_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class CallLog(db.Model):
    """Represents a call record between two users"""
    id = db.Column(db.Integer, primary_key=True)
    caller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    call_type = db.Column(db.String(20))  # 'outgoing', 'incoming'
    call_status = db.Column(db.String(20))  # 'answered', 'missed', 'rejected', 'cancelled'
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # in seconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
