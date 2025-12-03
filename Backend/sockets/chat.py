from flask_socketio import emit, join_room, leave_room
from models import Message
from database import db
from datetime import datetime

def register_socket_events(socketio):
    @socketio.on("join_room")
    def join(data):
        room = data["room"]
        join_room(room)

    @socketio.on("leave_room")
    def leave(data):
        leave_room(data["room"])

    @socketio.on("send_message")
    def send_message(data):
        msg = Message(
            sender_id=data["sender"],
            receiver_id=data["receiver"],
            content=data["text"]
        )
        db.session.add(msg)
        db.session.commit()

        room = data["room"]
        emit("new_message", data, room=room)
