from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, SystemLog, Message, FriendRequest, db
from functools import wraps
import sqlalchemy
import sys
import os

# Ensure Backend root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DSA.performance import generate_performance_graphs
from models import User, SystemLog, Message, FriendRequest, Group, GroupMember, GroupMessage, Class, ClassMember, Assignment, AssignmentSubmission, db

admin_bp = Blueprint("admin", __name__)

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def get_model_map():
    return {
        "user": User,
        "system_log": SystemLog,
        "message": Message,
        "friend_request": FriendRequest,
        "group": Group,
        "group_member": GroupMember,
        "group_message": GroupMessage,
        "class": Class,
        "class_member": ClassMember,
        "assignment": Assignment,
        "assignment_submission": AssignmentSubmission
    }

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Debugging
        master_key = request.headers.get('X-Admin-Key')
        
        # 1. Check for Master Key (God Mode)
        if master_key == "ecbopwgkmml":
            return fn(*args, **kwargs)
        
        # 2. Key failed? Check for Admin JWT
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user and user.is_admin:
                 return fn(*args, **kwargs)
        except:
            pass
            
        return jsonify({"error": "Admin access or Master Key required"}), 403
    return wrapper

@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_stats():
    return jsonify({
        "users": User.query.count(),
        "messages": Message.query.count(),
        "logs": SystemLog.query.count(),
        "friend_requests": FriendRequest.query.count()
    })

@admin_bp.route("/tables", methods=["GET"])
@admin_required
def get_tables():
    # Return keys from our model map + others if inspection needed
    # But for now, sticking to supported models is safer
    return jsonify({"tables": list(get_model_map().keys())})

@admin_bp.route("/table/<table_name>", methods=["GET"])
@admin_required
def get_table_data(table_name):
    model_map = get_model_map()
    model = model_map.get(table_name.lower())
    
    if not model:
        return jsonify({"error": "Table not supported in API"}), 400

    rows = model.query.all()
    # Serialize
    data = []
    for row in rows:
        row_data = {}
        for column in row.__table__.columns:
             # handle binary or complex types if needed, but for now simple serialization
            val = getattr(row, column.name)
            if isinstance(val, (datetime.datetime, datetime.date)):
                val = val.isoformat()
            row_data[column.name] = val
        data.append(row_data)
        
    return jsonify({"data": data, "columns": [c.name for c in model.__table__.columns]})

@admin_bp.route("/table/<table_name>", methods=["POST"])
@admin_required
def create_row(table_name):
    model_map = get_model_map()
    model = model_map.get(table_name.lower())
    if not model:
        return jsonify({"error": "Table not supported"}), 400

    data = request.json
    try:
        new_obj = model()
        for key, value in data.items():
            if hasattr(new_obj, key):
                setattr(new_obj, key, value)
        
        db.session.add(new_obj)
        db.session.commit()
        return jsonify({"message": "Record created"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@admin_bp.route("/table/<table_name>/<id>", methods=["PUT", "DELETE"])
@admin_required
def modify_row(table_name, id):
    model_map = get_model_map()
    model = model_map.get(table_name.lower())
    if not model:
        return jsonify({"error": "Table not supported"}), 400

    obj = model.query.get(id)
    if not obj:
        return jsonify({"error": "Record not found"}), 404

    if request.method == "DELETE":
        try:
            db.session.delete(obj)
            db.session.commit()
            return jsonify({"message": "Record deleted"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    elif request.method == "PUT":
        data = request.json
        try:
            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            db.session.commit()
            return jsonify({"message": "Record updated"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

@admin_bp.route("/logs", methods=["GET"])
@admin_required
def get_logs():
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(100).all()
    data = []
    for log in logs:
        data.append({
            "id": log.id,
            "level": log.level,
            "message": log.message,
            "timestamp": log.timestamp
        })
    return jsonify(data)

@admin_bp.route("/graphs/performance", methods=["GET"])
@admin_required
def get_performance_graphs():
    try:
        graphs = generate_performance_graphs()
        return jsonify(graphs)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
