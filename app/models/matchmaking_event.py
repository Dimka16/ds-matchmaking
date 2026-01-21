from dataclasses import dataclass
from typing import Any
import time
import uuid

@dataclass
class MatchmakingEvent:
    player: Any
    game_mode: Any
    action: str = "join"
    event_id: str = ""
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = time.time()

    def to_dict(self) -> dict:
        # game_mode might be Enum
        gm = self.game_mode.value if hasattr(self.game_mode, "value") else self.game_mode

        # player might be Player object
        if hasattr(self.player, "to_dict"):
            p = self.player.to_dict()
        elif isinstance(self.player, dict):
            p = self.player
        else:
            # last resort
            p = {
                "player_id": getattr(self.player, "player_id", None),
                "username": getattr(self.player, "username", None),
                "elo": getattr(self.player, "elo", None),
                "region": getattr(self.player, "region", None),
            }

        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "action": self.action,
            "game_mode": gm,
            "player": p,
        }
