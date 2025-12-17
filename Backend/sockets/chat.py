from flask_socketio import emit, join_room, leave_room
from models import Message, GroupMessage, GroupMember, User
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

    @socketio.on("send_group_message")
    def send_group_message(data):
        try:
            sender_id = data.get("sender_id")
            group_id = data.get("group_id")
            text = data.get("message", "")
            
            # Simple validation (production should be more robust)
            if not sender_id or not group_id:
                print("Invalid group message data")
                return

            # Save to DB
            msg = GroupMessage(
                group_id=group_id,
                sender_id=sender_id,
                text=text,
                file_data=data.get("file_data"),
                file_name=data.get("file_name"),
                file_type=data.get("file_type"),
                file_category=data.get("file_category")
            )
            db.session.add(msg)
            db.session.commit()
            
            # Get sender info for the client
            sender = User.query.get(sender_id)
            sender_name = sender.display_name if sender else "Unknown"
            sender_avatar = sender.avatar_url if sender else ""
            
            # Broadcast
            emit("new_group_message", {
                "id": msg.id,
                "group_id": group_id,
                "sender_id": sender_id,
                "sender_name": sender_name,
                "sender_avatar": sender_avatar,
                "text": text,
                "time": msg.timestamp.isoformat(),
                "file_data": data.get("file_data"),
                "file_name": data.get("file_name"),
                "file_type": data.get("file_type"),
                "file_category": data.get("file_category")
            }, room=str(group_id))
            
            print(f"Group message sent in room {group_id}")
            
        except Exception as e:
            print(f"Error sending group message: {e}")
            db.session.rollback()
