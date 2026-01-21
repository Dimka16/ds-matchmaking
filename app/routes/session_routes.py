from flask import Blueprint, request, jsonify, g
from flask_socketio import join_room
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

from app.db import db
from app.db_models import MatchSession, MatchPlayer
from app.socketio_ext import socketio
from app.auth.utils import require_auth
from app.event_log import add_event

bp = Blueprint("sessions", __name__, url_prefix="/sessions")

@bp.post("")
def create_session():
    payload = request.get_json(silent=True) or {}
    game_mode = payload.get("game_mode")
    players = payload.get("players")

    if not game_mode or not isinstance(players, list) or len(players) == 0:
        return jsonify({"status": "error", "error": "Invalid session payload"}), 400

    session = MatchSession(game_mode=game_mode)
    db.session.add(session)
    db.session.flush()  # ensures session.id is available

    for idx, p in enumerate(players):
        db.session.add(MatchPlayer(
            match_id=session.id,
            player_id=int(p["player_id"]),
            username=str(p["username"]),
            elo=int(p["elo"]),
            region=str(p["region"]),
            seed_order=idx
        ))

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "error": "Duplicate player in match (match_id, player_id must be unique)"
        }), 409

    add_event("session_created", {
        "id": session.id,
        "game_mode": game_mode,
        "players_count": len(players),
        "player_ids": [int(p["player_id"]) for p in players],
    })

    # Emit to each player room
    for p in players:
        room = f"player:{p['player_id']}"
        socketio.emit("match_found", {
            "id": session.id,
            "match_id": session.id,  # optional alias
            "game_mode": game_mode,
            "players": players
        }, room=room)

    return jsonify({
        "status": "created",
        "id": session.id,
        "match_id": session.id,  # optional alias
        "game_mode": game_mode,
        "players_count": len(players)
    }), 201

@bp.get("/<session_id>")
@require_auth
def get_session(session_id: str):
    session = MatchSession.query.get(session_id)
    if not session:
        return jsonify({"status": "error", "error": "Match session not found"}), 404

    allowed = (MatchPlayer.query
               .filter_by(match_id=session_id, player_id=g.user_id)
               .first()) is not None
    if not allowed:
        return jsonify({"status": "error", "error": "Forbidden"}), 403

    players = (MatchPlayer.query
               .filter_by(match_id=session_id)
               .order_by(MatchPlayer.seed_order.asc())
               .all())

    return jsonify({
        "status": "ok",
        "session": {
            "id": session.id,
            "game_mode": session.game_mode,
            "created_at": session.created_at.isoformat() if getattr(session, "created_at", None) else None,
            "players": [
                {
                    "player_id": p.player_id,
                    "username": p.username,
                    "elo": p.elo,
                    "region": p.region,
                    "seed_order": p.seed_order
                } for p in players
            ]
        }
    }), 200

@bp.get("")
@require_auth
def list_sessions():
    limit = request.args.get("limit", default=20, type=int)
    offset = request.args.get("offset", default=0, type=int)

    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    query = (MatchSession.query
             .join(MatchPlayer, MatchPlayer.match_id == MatchSession.id)
             .filter(MatchPlayer.player_id == g.user_id)
             .distinct())

    if hasattr(MatchSession, "created_at"):
        query = query.order_by(desc(MatchSession.created_at))
    else:
        query = query.order_by(desc(MatchSession.id))

    sessions = query.limit(limit).offset(offset).all()

    return jsonify({
        "status": "ok",
        "user_id": g.user_id,
        "limit": limit,
        "offset": offset,
        "sessions": [
            {
                "id": s.id,
                "match_id": s.id,  # optional alias
                "game_mode": s.game_mode,
                "created_at": s.created_at.isoformat() if getattr(s, "created_at", None) else None
            } for s in sessions
        ]
    }), 200

@socketio.on("register_player")
def register_player(data):
    try:
        player_id = int((data or {}).get("player_id"))
    except Exception:
        return

    join_room(f"player:{player_id}")
    socketio.emit("registered", {"player_id": player_id}, room=request.sid)
