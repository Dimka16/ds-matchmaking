import os
from flask import Flask
from app.db import db

from app.routes.matchmaking_routes import bp as matchmaking_bp
from app.routes.debug_routes import bp as debug_bp
from app.routes.session_routes import bp as sessions_bp
from app.socketio_ext import socketio
from app.auth.routes import bp as auth_bp


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    socketio.init_app(app, async_mode="eventlet")

    with app.app_context():
        db.create_all()

    app.register_blueprint(matchmaking_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(auth_bp)

    return app
