import uuid
import time
from app.models.player import Player
from app.models.game_mode import GameMode


class MatchmakingEvent:
    def __init__(
            self,
            player: Player,
            game_mode: GameMode,
            timestamp: int | None = None,
            event_id: str | None = None
    ):
        self.event_id = event_id or str(uuid.uuid4())
        self.player = player
        self.game_mode = game_mode
        self.timestamp = timestamp or int(time.time())

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "player": {
                "player_id": self.player.player_id,
                "username": self.player.username,
                "elo": self.player.elo,
                "region": self.player.region
            },
            "game_mode": self.game_mode.value,
            "timestamp": self.timestamp
        }
