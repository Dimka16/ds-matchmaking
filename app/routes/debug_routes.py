import os
from flask import Blueprint, render_template, request, jsonify
from app.event_log import list_events, clear_events
from app.auth.utils import require_auth
from app.db import db

bp = Blueprint("debug", __name__, url_prefix="/debug")

@bp.get("")
def index():
    return render_template("dashboard.html")

@bp.get("/events")
def events():
    limit = request.args.get("limit", default=50, type=int)
    return jsonify({"status": "ok", "events": list_events(limit)}), 200

@bp.post("/reset")
@require_auth
def reset():
    """
    Optional dev-only reset endpoint.
    Disabled unless DEBUG_ALLOW_RESET=true.
    """
    if os.getenv("DEBUG_ALLOW_RESET", "false").lower() != "true":
        return jsonify({"status": "error", "error": "Reset disabled"}), 403

    db.session.execute(db.text("TRUNCATE TABLE match_players RESTART IDENTITY CASCADE;"))
    db.session.execute(db.text("TRUNCATE TABLE match_sessions RESTART IDENTITY CASCADE;"))
    db.session.commit()
    clear_events()

    return jsonify({"status": "ok", "message": "Sessions cleared"}), 200
