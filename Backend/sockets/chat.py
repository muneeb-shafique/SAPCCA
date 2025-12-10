from flask_socketio import emit, join_room, leave_room
from models import Message
from database import db
from datetime import datetime

def register_socket_events(socketio):
    @socketio.on("join_room")
    def join(data):
        room = data["room"]
        join_room(room)
        print(f"User joined room: {room}")

    @socketio.on("leave_room")
    def leave(data):
        room = data["room"]
        leave_room(room)
        print(f"User left room: {room}")

    @socketio.on("send_message")
    def send_message(data):
        # Save message to database
        msg = Message(
            sender_id=data["sender"],
            receiver_id=data["receiver"],
            content=data.get("text", ""),
            file_data=data.get("file_data"),
            file_name=data.get("file_name"),
            file_type=data.get("file_type"),
            file_category=data.get("file_category")
        )
        db.session.add(msg)
        db.session.commit()

        # Broadcast to room (both sender and receiver will receive)
        room = data["room"]
        emit("new_message", {
            "from": data["sender"],
            "to": data["receiver"],
            "text": data.get("text", ""),
            "time": msg.timestamp.isoformat(),
            "file_data": data.get("file_data"),
            "file_name": data.get("file_name"),
            "file_type": data.get("file_type"),
            "file_category": data.get("file_category")
        }, room=room)
        
        msg_preview = data.get('text', '')[:30] if data.get('text') else f"[File: {data.get('file_name', 'attachment')}]"
        print(f"Message sent in room {room}: {msg_preview}...")
