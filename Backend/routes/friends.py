from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, FriendRequest

friends_bp = Blueprint("friends", __name__)

# --- Helper function for fetching the current user's ID ---
def get_current_user_id():
    # Return as int for DB operations
    return int(get_jwt_identity())

# -----------------------------------------------------------------
# 1. SEND REQUEST (Supports ID, email, username, or registration_number)
# -----------------------------------------------------------------
@friends_bp.post("/request")
@jwt_required()
def send_friend_request():
    sender_id = get_current_user_id()
    
    # Use try-except for robust JSON parsing
    try:
        data = request.json
        identifier = str(data["identifier"]).strip()
    except (TypeError, KeyError, ValueError):
        return jsonify({"error": "Invalid or missing 'identifier' in request body"}), 400

    # Try to find the receiver by different methods
    receiver = None
    
    # Try as ID (numeric)
    if identifier.isdigit():
        receiver = User.query.get(int(identifier))
    
    # Try as email
    if not receiver:
        receiver = User.query.filter_by(email=identifier).first()
    
    # Try as display_name
    if not receiver:
        receiver = User.query.filter_by(display_name=identifier).first()
    
    # Try as registration_number
    if not receiver:
        receiver = User.query.filter_by(registration_number=identifier).first()
    
    # If still not found, return error
    if not receiver:
        return jsonify({"error": "User not found with the provided identifier"}), 404
    
    receiver_id = receiver.id

    # Basic checks
    if sender_id == receiver_id:
        return jsonify({"error": "Cannot send request to self"}), 400

    # Check for existing request (pending, accepted, or reversed)
    # A single query checks for any relationship/request between the two users
    existing_request = FriendRequest.query.filter(
        ((FriendRequest.sender_id == sender_id) & (FriendRequest.receiver_id == receiver_id)) |
        ((FriendRequest.sender_id == receiver_id) & (FriendRequest.receiver_id == sender_id))
    ).first()

    if existing_request:
        status_message = existing_request.status
        if status_message == 'pending':
            return jsonify({"message": "Friend request already pending"}), 409
        elif status_message == 'accepted':
            return jsonify({"message": "Users are already friends"}), 409
        # For rejected status, you might allow resending, but for simplicity, we prevent duplicate records.
        return jsonify({"message": f"Existing relationship found with status: {status_message}"}), 409


    # Create and commit new request with default status 'pending'
    # NOTE: The FriendRequest model must define status as a column with 'pending' as default.
    new_request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id, status='pending')
    db.session.add(new_request)
    db.session.commit()

    return jsonify({"message": "Friend request sent"}), 201

# -----------------------------------------------------------------
# 2. VIEW PENDING REQUESTS (Only shows requests with status='pending')
# -----------------------------------------------------------------
@friends_bp.get("/pending")
@jwt_required()
def get_pending_requests():
    user_id = get_current_user_id()
    
    # Filter for requests where user is the receiver AND status is 'pending'
    pending_requests = FriendRequest.query.filter_by(receiver_id=user_id, status='pending').all()
    
    requests_list = []
    for req in pending_requests:
        sender = User.query.get(req.sender_id)
        requests_list.append({
            "request_id": req.id,
            "sender_id": req.sender_id,
            "sender_name": sender.display_name if sender else "Unknown User",
            "sender_avatar": sender.avatar_url if sender else "",
            "timestamp": req.timestamp.isoformat() if req.timestamp else None
        })

    return jsonify({"requests": requests_list})

# -----------------------------------------------------------------
# 3. VIEW OUTGOING REQUESTS (Requests sent by current user)
# -----------------------------------------------------------------
@friends_bp.get("/outgoing")
@jwt_required()
def get_outgoing_requests():
    user_id = get_current_user_id()
    
    # Filter for requests where user is the sender AND status is 'pending'
    outgoing_requests = FriendRequest.query.filter_by(sender_id=user_id, status='pending').all()
    
    requests_list = []
    for req in outgoing_requests:
        receiver = User.query.get(req.receiver_id)
        requests_list.append({
            "request_id": req.id,
            "receiver_id": req.receiver_id,
            "receiver_name": receiver.display_name if receiver else "Unknown User",
            "receiver_avatar": receiver.avatar_url if receiver else "",
            "timestamp": req.timestamp.isoformat() if req.timestamp else None
        })

    return jsonify({"requests": requests_list})

# -----------------------------------------------------------------
# 4. REJECT REQUEST (Marks request as 'rejected' instead of deleting)
# -----------------------------------------------------------------
@friends_bp.post("/reject")
@jwt_required()
def reject_friend_request():
    user_id = get_current_user_id()
    
    try:
        request_id = request.json["request_id"]
    except (TypeError, KeyError):
        return jsonify({"error": "Missing 'request_id' in request body"}), 400

    request_to_reject = FriendRequest.query.get(request_id)

    if not request_to_reject:
        return jsonify({"error": "Friend request not found"}), 404

    # Security check: Ensure the current user is the intended receiver
    if request_to_reject.receiver_id != user_id:
        return jsonify({"error": "Unauthorized action on this request"}), 403
    
    # Mark as rejected instead of deleting
    request_to_reject.status = 'rejected'
    db.session.commit()

    return jsonify({"message": "Friend request rejected"}), 200

# -----------------------------------------------------------------
# 5. CANCEL REQUEST (For sender to cancel their own outgoing request)
# -----------------------------------------------------------------
@friends_bp.post("/cancel")
@jwt_required()
def cancel_friend_request():
    user_id = get_current_user_id()
    
    try:
        request_id = request.json["request_id"]
    except (TypeError, KeyError):
        return jsonify({"error": "Missing 'request_id' in request body"}), 400

    request_to_cancel = FriendRequest.query.get(request_id)

    if not request_to_cancel:
        return jsonify({"error": "Friend request not found"}), 404

    # Security check: Ensure the current user is the sender
    if request_to_cancel.sender_id != user_id:
        return jsonify({"error": "Unauthorized action on this request"}), 403
    
    # Delete the request
    db.session.delete(request_to_cancel)
    db.session.commit()

    return jsonify({"message": "Friend request cancelled"}), 200

# -----------------------------------------------------------------
# 6. ACCEPT REQUEST (Sets status to 'accepted')
# -----------------------------------------------------------------
@friends_bp.post("/accept")
@jwt_required()
def accept_friend_request():
    user_id = get_current_user_id()
    
    try:
        request_id = request.json["request_id"]
    except (TypeError, KeyError):
        return jsonify({"error": "Missing 'request_id' in request body"}), 400

    request_to_accept = FriendRequest.query.get(request_id)

    if not request_to_accept:
        return jsonify({"error": "Friend request not found"}), 404

    # Security check: Ensure the current user is the intended receiver
    if request_to_accept.receiver_id != user_id:
        return jsonify({"error": "Unauthorized action on this request"}), 403
    
    # Ensure the request is still pending
    if request_to_accept.status != 'pending':
        return jsonify({"error": f"Request is not pending (status: {request_to_accept.status})"}), 409

    # Update the FriendRequest status to 'accepted'
    request_to_accept.status = 'accepted'
    db.session.commit()
    
    return jsonify({"message": "Friend request accepted"}), 200

# -----------------------------------------------------------------
# 7. LIST FRIENDS (Returns list of accepted friends)
# -----------------------------------------------------------------
@friends_bp.get("/list")
@jwt_required()
def get_friends_list():
    user_id = get_current_user_id()

    # Query for all accepted friend requests where the user is either sender or receiver
    friends_query = FriendRequest.query.filter(
        ((FriendRequest.sender_id == user_id) | (FriendRequest.receiver_id == user_id)) &
        (FriendRequest.status == 'accepted')
    ).all()

    friends_data = []
    
    for req in friends_query:
        # Determine who the friend is (the other person in the pair)
        if req.sender_id == user_id:
            friend_id = req.receiver_id
        else:
            friend_id = req.sender_id
            
        friend = User.query.get(friend_id)
        
        if friend:
            friends_data.append({
                "id": friend.id,
                "display_name": friend.display_name,
                "avatar_url": friend.avatar_url,
                "email": friend.email
            })

    return jsonify(friends_data), 200

# -----------------------------------------------------------------
# 8. LIST IGNORED/REJECTED REQUESTS
# -----------------------------------------------------------------
@friends_bp.get("/ignored")
@jwt_required()
def get_ignored_requests():
    user_id = get_current_user_id()
    
    # Filter for requests where user is the receiver AND status is 'rejected'
    ignored_requests = FriendRequest.query.filter_by(receiver_id=user_id, status='rejected').all()
    
    requests_list = []
    for req in ignored_requests:
        sender = User.query.get(req.sender_id)
        requests_list.append({
            "request_id": req.id,
            "sender_id": req.sender_id,
            "sender_name": sender.display_name if sender else "Unknown User",
            "sender_avatar": sender.avatar_url if sender else "",
            "timestamp": req.timestamp.isoformat() if req.timestamp else None
        })

    return jsonify({"requests": requests_list})

# -----------------------------------------------------------------
# 9. DELETE IGNORED REQUEST (Permanently removes rejected request)
# -----------------------------------------------------------------
@friends_bp.post("/delete")
@jwt_required()
def delete_friend_request():
    user_id = get_current_user_id()
    
    try:
        request_id = request.json["request_id"]
    except (TypeError, KeyError):
        return jsonify({"error": "Missing 'request_id' in request body"}), 400

    request_to_delete = FriendRequest.query.get(request_id)

    if not request_to_delete:
        return jsonify({"error": "Friend request not found"}), 404

    # Security check: Ensure the current user is the intended receiver
    if request_to_delete.receiver_id != user_id:
        return jsonify({"error": "Unauthorized action on this request"}), 403
    
    # Delete the request
    db.session.delete(request_to_delete)
    db.session.commit()

    return jsonify({"message": "Friend request deleted"}), 200