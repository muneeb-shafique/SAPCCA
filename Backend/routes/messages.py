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
        message_content = data["message"]
    except (TypeError, KeyError, ValueError):
        return jsonify({"error": "Invalid request body"}), 400

    # Verify receiver exists
    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({"error": "Receiver not found"}), 404

    msg = Message(
        sender_id=uid,
        receiver_id=receiver_id,
        content=message_content
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({"message": "sent"}), 200

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
                "from": m.sender_id, 
                "text": m.content, 
                "time": m.timestamp.isoformat() if m.timestamp else None
            }
            for m in history
        ]
    }), 200
