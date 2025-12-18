from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from database import db, migrate
from config import Config
import os

# socket server
socketio = SocketIO(cors_allowed_origins="*", max_http_buffer_size=5 * 1024 * 1024)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    JWTManager(app)

    # database init
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import models so SQLAlchemy knows what to create
        from models import User, SystemLog, FriendRequest, Message, Group, GroupMember, GroupMessage, Class, ClassMember
        db.create_all()


    # register routes
    from routes.auth import auth_bp
    from routes.friends import friends_bp
    from routes.messages import messages_bp
    from routes.profile import profile_bp
    from routes.groups import groups_bp
    from routes.classes import classes_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(friends_bp, url_prefix="/api/friends")
    app.register_blueprint(messages_bp, url_prefix="/api/messages")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")
    app.register_blueprint(groups_bp, url_prefix="/api/groups")
    app.register_blueprint(classes_bp, url_prefix="/api/classes")
    
    from routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # socket events
    from sockets.chat import register_socket_events
    register_socket_events(socketio)

    # Serve frontend
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Frontend')
    
    @app.route('/')
    def serve_welcome():
        return send_from_directory(frontend_dir, 'welcome.html')
    
    @app.route('/<path:filename>')
    def serve_static(filename):
        return send_from_directory(frontend_dir, filename)

    return app


if __name__ == "__main__":
    app = create_app()
    socketio.init_app(app)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
