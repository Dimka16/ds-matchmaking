from typing import Dict, List, Optional
from app.models.player import Player
from app.repositories.waiting_player_repo import WaitingPlayerRepository


class WaitingPlayerRepositoryImpl(WaitingPlayerRepository):
    def __init__(self):
        # Keyed by player_id to prevent duplicates and make removals reliable
        self._waiting_players: Dict[int, Player] = {}

    def add(self, player: Player) -> None:
        # idempotent: add/update by id
        self._waiting_players[player.player_id] = player

    def get_all(self) -> List[Player]:
        return list(self._waiting_players.values())

    def get_by_id(self, player_id: int) -> Optional[Player]:
        return self._waiting_players.get(player_id)

    def remove_by_id(self, player_id: int) -> None:
        self._waiting_players.pop(player_id, None)

    def remove(self, player: Player) -> None:
        # remove by id, not by object identity
        self.remove_by_id(player.player_id)
