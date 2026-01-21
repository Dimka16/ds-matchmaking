from flask import Blueprint, request, jsonify
from app.db import db
from app.auth.models import User
from app.auth.utils import hash_password, verify_password, generate_token

bp = Blueprint("auth", __name__, url_prefix="/auth")

def _password_too_long(pw: str) -> bool:
    return len(pw.encode("utf-8")) > 72

@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if _password_too_long(password):
        return jsonify({
            "status": "error",
            "error": "Password is too long (max 72 bytes for bcrypt)."
        }), 400

    if not username or not password:
        return jsonify({"status": "error", "error": "username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "error": "username already exists"}), 409

    user = User(username=username, password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()

    return jsonify({"status": "created", "user_id": user.id, "username": user.username}), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(password, user.password_hash) or _password_too_long(password):
        return jsonify({"status": "error", "error": "invalid credentials"}), 401

    token = generate_token(user.id, user.username)
    return jsonify({"status": "ok", "token": token}), 200
