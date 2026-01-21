import uuid
from datetime import datetime
from app.db import db


class MatchSession(db.Model):
    __tablename__ = "match_sessions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    game_mode = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.Index("ix_match_sessions_created_at", "created_at"),
        db.Index("ix_match_sessions_game_mode", "game_mode"),
    )


class MatchPlayer(db.Model):
    __tablename__ = "match_players"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(36), db.ForeignKey("match_sessions.id"), nullable=False)

    player_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(64), nullable=False)
    elo = db.Column(db.Integer, nullable=False)
    region = db.Column(db.String(32), nullable=False)
    seed_order = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("match_id", "player_id", name="uq_match_players_match_id_player_id"),
        db.Index("ix_match_players_match_id", "match_id"),
        db.Index("ix_match_players_player_id", "player_id"),
    )
