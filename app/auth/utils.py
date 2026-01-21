import os
import time
import jwt
from functools import wraps
from flask import request, jsonify, g
import bcrypt as _bcrypt

JWT_ALG = "HS256"


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")
    salt = _bcrypt.gensalt(rounds=12)
    return _bcrypt.hashpw(pw, salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    except Exception:
        return False


def generate_token(user_id: int, username: str, ttl_seconds: int = 24 * 3600) -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is not set")

    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "username": username,
        "iat": now,
        "exp": now + ttl_seconds
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALG)


def decode_token(token: str) -> dict:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is not set")
    return jwt.decode(token, secret, algorithms=[JWT_ALG])


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"status": "error", "error": "Missing Bearer token"}), 401

        token = auth.split(" ", 1)[1].strip()
        try:
            claims = decode_token(token)
        except Exception as e:
            return jsonify({"status": "error", "error": "Invalid token", "details": str(e)}), 401

        g.user_id = int(claims["sub"])
        g.username = claims["username"]
        return fn(*args, **kwargs)
    return wrapper
