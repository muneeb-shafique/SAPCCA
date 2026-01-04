import sys
import os

# Add Backend directory to system path to allow importing app
sys.path.append(os.path.join(os.path.dirname(__file__), 'Backend'))

from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app)
