from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Message, User
from database import db
import sys
import os
import base64





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

    # --- ML CONTENT MODERATION - REMOVED ---
    # moderator.initialize() # Ensure models are loaded
    
    # Text Check
    # if message_content:
    #     is_safe, reason = moderator.check_text(message_content)
    #     if not is_safe:
    #         return jsonify({"error": reason}), 400

    # Image Check
    # if file_data and file_type and  ("image" in file_type):
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
    #         print(f"DM Image Mod Error: {e}")
    #         # Fail open or closed? Proceed if error to avoid blocking valid
    # -----------------------------

    msg = Message(
        sender_id=uid,
        receiver_id=receiver_id,
        content=message_content,
        file_data=file_data,
        file_name=file_name,
        file_type=file_type,
        file_category=file_category,
        voice_data=data.get("voice_data"),
        voice_duration=data.get("voice_duration"),
        reply_to_id=data.get("reply_to_id")
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
                "file_category": m.file_category,
                "voice_data": m.voice_data,
                "voice_duration": m.voice_duration,
                "reply_to": get_reply_data_dm(m.reply_to_id) if m.reply_to_id else None
            }
            for m in history
        ]
    }), 200

def get_reply_data_dm(reply_to_id):
    """Helper to get reply message data for DMs"""
    reply_msg = Message.query.get(reply_to_id)
    if not reply_msg:
        return None
    sender = User.query.filter_by(id=reply_msg.sender_id).first()
    return {
        "id": reply_msg.id,
        "text": reply_msg.content,
        "sender_name": sender.display_name if sender else "Unknown",
        "has_voice": bool(reply_msg.voice_data),
        "has_file": bool(reply_msg.file_data)
    }

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
