from flask_socketio import emit, join_room, leave_room
from models import Message, GroupMessage, GroupMember, User
from database import db
from datetime import datetime
import sys
import os
import base64



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
        # 1. Content Moderation Check - REMOVED
        # text = data.get("text", "")
        # file_data = data.get("file_data")
        # file_type = data.get("file_type", "")
        
        # Check Text Sentiment
        # if text:
        #     is_safe, reason = moderator.check_text(text)
        #     if not is_safe:
        #         emit("error", {"message": reason})
        #         return

        # Check Image NSFW
        # if file_data and "image" in file_type:
        #     # Handle potential base64 header
        #     try:
        #         if "," in file_data:
        #             _, encoded = file_data.split(",", 1)
        #         else:
        #             encoded = file_data
        #         image_bytes = base64.b64decode(encoded)
        #         
        #         is_safe, reason = moderator.check_image(image_bytes)
        #         if not is_safe:
        #             emit("error", {"message": reason})
        #             return
        #     except Exception as e:
        #         print(f"Moderation Error for Image: {e}")
        #         pass # Fail open or closed? Let's proceed if check fails to avoid blocking valid images on error

        # Save message to database
        msg = Message(
            sender_id=data["sender"],
            receiver_id=data["receiver"],
            content=data.get("text", ""),
            file_data=data.get("file_data"),
            file_name=data.get("file_name"),
            file_type=data.get("file_type"),
            file_category=data.get("file_category"),
            voice_data=data.get("voice_data"),
            voice_duration=data.get("voice_duration"),
            reply_to_id=data.get("reply_to_id")
        )
        db.session.add(msg)
        db.session.commit()

        # Broadcast to room (both sender and receiver will receive)
        room = data["room"]
        emit("new_message", {
            "id": msg.id,
            "from": data["sender"],
            "to": data["receiver"],
            "text": data.get("text", ""),
            "time": msg.timestamp.isoformat(),
            "file_data": data.get("file_data"),
            "file_name": data.get("file_name"),
            "file_type": data.get("file_type"),
            "file_category": data.get("file_category"),
            "voice_data": data.get("voice_data"),
            "voice_duration": data.get("voice_duration"),
            "reply_to_id": data.get("reply_to_id")
        }, room=room)
        
        msg_preview = data.get('text', '')[:30] if data.get('text') else f"[File: {data.get('file_name', 'attachment')}]"
        print(f"Message sent in room {room}: {msg_preview}...")

    @socketio.on("send_group_message")
    def send_group_message(data):
        try:
            sender_id = data.get("sender_id")
            group_id = data.get("group_id")
            text = data.get("message", "")
            file_data = data.get("file_data")
            file_type = data.get("file_type", "")
            
            # 1. Moderation Check - REMOVED
            # if text:
            #     is_safe, reason = moderator.check_text(text)
            #     if not is_safe:
            #         emit("error", {"message": reason})
            #         return

            # if file_data and "image" in file_type:
            #     try:
            #         if "," in file_data:
            #             _, encoded = file_data.split(",", 1)
            #         else:
            #             encoded = file_data
            #         image_bytes = base64.b64decode(encoded)
            #         
            #         is_safe, reason = moderator.check_image(image_bytes)
            #         if not is_safe:
            #             emit("error", {"message": reason})
            #             return
            #     except Exception as e:
            #         print(f"Group Img Mod Error: {e}")
            
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
                file_category=data.get("file_category"),
                voice_data=data.get("voice_data"),
                voice_duration=data.get("voice_duration"),
                reply_to_id=data.get("reply_to_id")
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
                "file_category": data.get("file_category"),
                "voice_data": data.get("voice_data"),
                "voice_duration": data.get("voice_duration"),
                "reply_to_id": data.get("reply_to_id")
            }, room=str(group_id))
            
            print(f"Group message sent in room {group_id}")
            
        except Exception as e:
            print(f"Error sending group message: {e}")
            db.session.rollback()

    @socketio.on("delete_message")
    def delete_message(data):
        """Real-time message deletion for DMs"""
        try:
            message_id = data.get("message_id")
            user_id = data.get("user_id")
            room = data.get("room")
            
            if not message_id or not user_id:
                return
            
            msg = Message.query.get(message_id)
            if msg and msg.sender_id == user_id:
                db.session.delete(msg)
                db.session.commit()
                
                # Broadcast deletion to room
                emit("message_deleted", {
                    "message_id": message_id,
                    "chat_type": "dm"
                }, room=room)
                
                print(f"Message {message_id} deleted in room {room}")
        except Exception as e:
            print(f"Error deleting message: {e}")
            db.session.rollback()

    @socketio.on("delete_group_message")
    def delete_group_message(data):
        """Real-time message deletion for groups"""
        try:
            message_id = data.get("message_id")
            user_id = data.get("user_id")
            group_id = data.get("group_id")
            
            if not message_id or not user_id or not group_id:
                return
            
            msg = GroupMessage.query.get(message_id)
            if msg and msg.sender_id == user_id:
                db.session.delete(msg)
                db.session.commit()
                
                # Broadcast deletion to group
                emit("message_deleted", {
                    "message_id": message_id,
                    "chat_type": "group"
                }, room=str(group_id))
                
                print(f"Group message {message_id} deleted in group {group_id}")
        except Exception as e:
            print(f"Error deleting group message: {e}")
            db.session.rollback()

    # ===== WEBRTC AUDIO CALL SIGNALING =====
    
    @socketio.on("call_initiate")
    def call_initiate(data):
        """Initiate an audio call to another user"""
        try:
            caller_id = data.get("caller_id")
            recipient_id = data.get("recipient_id")
            caller_name = data.get("caller_name")
            caller_avatar = data.get("caller_avatar")
            
            if not caller_id or not recipient_id:
                return
            
            # Create a unique room for this call
            call_room = f"call_{min(caller_id, recipient_id)}_{max(caller_id, recipient_id)}"
            
            # Notify recipient of incoming call
            emit("call_ringing", {
                "caller_id": caller_id,
                "caller_name": caller_name,
                "caller_avatar": caller_avatar,
                "call_room": call_room,
                "call_type": data.get("call_type", "audio")
            }, room=str(recipient_id))
            
            print(f"Call initiated: {caller_id} -> {recipient_id}, room: {call_room}")
        except Exception as e:
            print(f"Error initiating call: {e}")
    
    @socketio.on("call_accept")
    def call_accept(data):
        """Accept an incoming call"""
        try:
            caller_id = data.get("caller_id")
            recipient_id = data.get("recipient_id")
            recipient_name = data.get("recipient_name")
            recipient_avatar = data.get("recipient_avatar")
            call_room = data.get("call_room")
            
            if not caller_id or not recipient_id or not call_room:
                return
            
            # Join both users to the call room
            join_room(call_room)
            
            # Notify caller that call was accepted
            emit("call_accepted", {
                "recipient_id": recipient_id,
                "recipient_name": recipient_name,
                "recipient_avatar": recipient_avatar,
                "call_room": call_room
            }, room=str(caller_id))
            
            print(f"Call accepted: {caller_id} <-> {recipient_id}, room: {call_room}")
        except Exception as e:
            print(f"Error accepting call: {e}")
    
    @socketio.on("call_reject")
    def call_reject(data):
        """Reject an incoming call"""
        try:
            caller_id = data.get("caller_id")
            recipient_id = data.get("recipient_id")
            
            if not caller_id or not recipient_id:
                return
            
            # Notify caller that call was rejected
            emit("call_rejected", {
                "recipient_id": recipient_id
            }, room=str(caller_id))
            
            print(f"Call rejected: {caller_id} -> {recipient_id}")
        except Exception as e:
            print(f"Error rejecting call: {e}")
    
    @socketio.on("call_end")
    def call_end(data):
        """End an active call"""
        try:
            user_id = data.get("user_id")
            peer_id = data.get("peer_id")
            call_room = data.get("call_room")
            
            if not user_id or not peer_id or not call_room:
                return
            
            # Notify peer that call ended (broadcast to room AND specific peer to be safe)
            emit("call_ended", {
                "user_id": user_id
            }, room=call_room)
            
            if peer_id:
                emit("call_ended", {
                    "user_id": user_id
                }, room=str(peer_id))
            
            # Leave the call room
            leave_room(call_room)
            
            print(f"Call ended: {user_id} with {peer_id}, room: {call_room}")
        except Exception as e:
            print(f"Error ending call: {e}")
    
    @socketio.on("webrtc_offer")
    def webrtc_offer(data):
        """Forward WebRTC offer from caller to recipient"""
        try:
            offer = data.get("offer")
            recipient_id = data.get("recipient_id")
            caller_id = data.get("caller_id")
            
            if not offer or not recipient_id or not caller_id:
                return
            
            # Forward offer to recipient
            emit("webrtc_offer", {
                "offer": offer,
                "caller_id": caller_id
            }, room=str(recipient_id))
            
            print(f"WebRTC offer forwarded: {caller_id} -> {recipient_id}")
        except Exception as e:
            print(f"Error forwarding WebRTC offer: {e}")
    
    @socketio.on("webrtc_answer")
    def webrtc_answer(data):
        """Forward WebRTC answer from recipient to caller"""
        try:
            answer = data.get("answer")
            caller_id = data.get("caller_id")
            recipient_id = data.get("recipient_id")
            
            if not answer or not caller_id or not recipient_id:
                return
            
            # Forward answer to caller
            emit("webrtc_answer", {
                "answer": answer,
                "recipient_id": recipient_id
            }, room=str(caller_id))
            
            print(f"WebRTC answer forwarded: {recipient_id} -> {caller_id}")
        except Exception as e:
            print(f"Error forwarding WebRTC answer: {e}")
    
    @socketio.on("webrtc_ice_candidate")
    def webrtc_ice_candidate(data):
        """Forward ICE candidate between peers"""
        try:
            candidate = data.get("candidate")
            peer_id = data.get("peer_id")
            sender_id = data.get("sender_id")
            
            if not candidate or not peer_id or not sender_id:
                return
            
            # Forward ICE candidate to peer
            emit("webrtc_ice_candidate", {
                "candidate": candidate,
                "sender_id": sender_id
            }, room=str(peer_id))
            
            print(f"ICE candidate forwarded: {sender_id} -> {peer_id}")
        except Exception as e:
            print(f"Error forwarding ICE candidate: {e}")
