from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Message, User
from database import db



messages_bp = Blueprint("messages", __name__)

@messages_bp.post("/send")
@jwt_required()
def send_msg():
    uid = int(get_jwt_identity())
    
    try:
        data = request.json
        receiver_id = int(data["receiver_id"])
        message_content = data.get("message", "")
        
        # File upload fields (optional)
        file_data = data.get("file_data")
        file_name = data.get("file_name")
        file_type = data.get("file_type")
        file_category = data.get("file_category")
        
    except (TypeError, KeyError, ValueError):
        return jsonify({"error": "Invalid request body"}), 400

    # Verify receiver exists
    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({"error": "Receiver not found"}), 404

    # Validate file size (5MB limit for base64)
    if file_data:
        # Base64 encoded size is ~4/3 of original
        # 5MB * 1.33 = ~6.65MB base64
        if len(file_data) > 6_650_000:
            return jsonify({"error": "File too large. Maximum size is 5MB"}), 400

    msg = Message(
        sender_id=uid,
        receiver_id=receiver_id,
        content=message_content,
        file_data=file_data,
        file_name=file_name,
        file_type=file_type,
        file_category=file_category
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({
        "message": "sent",
        "id": msg.id,
        "timestamp": msg.timestamp.isoformat()
    }), 200

@messages_bp.get("/chat/<int:friend_id>")
@jwt_required()
def chat_history(friend_id):
    uid = int(get_jwt_identity())

    # Verify friend exists
    friend = User.query.get(friend_id)
    if not friend:
        return jsonify({"error": "User not found"}), 404

    history = Message.query.filter(
        ((Message.sender_id == uid) & (Message.receiver_id == friend_id)) |
        ((Message.sender_id == friend_id) & (Message.receiver_id == uid))
    ).order_by(Message.timestamp.asc()).all()

    return jsonify({
        "messages": [
            {
                "id": m.id,  # Include message ID
                "from": m.sender_id, 
                "text": m.content, 
                "time": m.timestamp.isoformat() if m.timestamp else None,
                "file_data": m.file_data,
                "file_name": m.file_name,
                "file_type": m.file_type,
                "file_category": m.file_category
            }
            for m in history
        ]
    }), 200

@messages_bp.delete("/delete/<int:message_id>")
@jwt_required()
def delete_message(message_id):
    uid = int(get_jwt_identity())
    
    msg = Message.query.get(message_id)
    
    if not msg:
        return jsonify({"error": "Message not found"}), 404
        
    if msg.sender_id != uid:
        return jsonify({"error": "Unauthorized"}), 403
        
    db.session.delete(msg)
    db.session.commit()
    
    return jsonify({"message": "Message deleted"}), 200
