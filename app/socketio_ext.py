import os
from flask_socketio import SocketIO

socketio = SocketIO(
    cors_allowed_origins="*",
    message_queue=os.getenv("REDIS_URL", "redis://redis:6379/0"),
)