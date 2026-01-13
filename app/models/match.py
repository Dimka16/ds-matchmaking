

from typing import List
from app.models.player import Player
from app.models.game_mode import GameMode


class Match:

    def __init__(self, players: List[Player], game_mode: GameMode):
        self.players = players
        self.game_mode = game_mode

    def __repr__(self) -> str:
        player_ids = [p.player_id for p in self.players]
        return f"<Match game_mode={self.game_mode.value} players={player_ids}>"
