from flask import Blueprint, request, jsonify, g
from app.kafka.producer_factory import create_kafka_producer
from app.kafka.producer import KafkaProducerClient
from app.auth.utils import require_auth
from app.models.player import Player
from app.models.game_mode import GameMode
from app.services.matchmaking_service_impl import MatchmakingServiceImpl
from app.event_log import add_event

bp = Blueprint("matchmaking", __name__, url_prefix="/matchmaking")

_kafka_producer = KafkaProducerClient(create_kafka_producer())
_service = MatchmakingServiceImpl(_kafka_producer)


@bp.post("/join")
@require_auth
def join():
    payload = request.get_json(silent=True) or {}
    if "game_mode" not in payload:
        return jsonify({"status": "error", "error": "game_mode is required"}), 400

    try:
        game_mode = GameMode(payload["game_mode"])
    except Exception:
        return jsonify({"status": "error", "error": "Invalid game_mode"}), 400

    player = Player(
        player_id=int(g.user_id),
        username=str(g.username),
        elo=int(payload.get("elo", 0)),
        region=str(payload.get("region", "")),
    )

    try:
        event = _service.enqueue_player(player, game_mode, action="join")
        add_event("queue_join", {
            "user_id": g.user_id,
            "game_mode": game_mode.value,
            "elo": player.elo,
            "region": player.region,
            "event_id": event.event_id,
        })
        return jsonify({"status": "queued", "event_id": event.event_id, "topic_game_mode": game_mode.value}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": "Failed to publish matchmaking event to Kafka", "details": str(e)}), 503


@bp.post("/leave")
@require_auth
def leave():
    payload = request.get_json(silent=True) or {}
    if "game_mode" not in payload:
        return jsonify({"status": "error", "error": "game_mode is required"}), 400

    try:
        game_mode = GameMode(payload["game_mode"])
    except Exception:
        return jsonify({"status": "error", "error": "Invalid game_mode"}), 400

    player = Player(
        player_id=int(g.user_id),
        username=str(g.username),
        elo=int(payload.get("elo", 0)),
        region=str(payload.get("region", "")),
    )

    try:
        event = _service.enqueue_player(player, game_mode, action="leave")
        add_event("queue_leave", {
            "user_id": g.user_id,
            "game_mode": game_mode.value,
            "event_id": event.event_id,
        })
        return jsonify({"status": "queued", "event_id": event.event_id, "topic_game_mode": game_mode.value}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": "Failed to publish leave event", "details": str(e)}), 503
