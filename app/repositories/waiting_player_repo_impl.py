from typing import List
from app.models.player import Player
from app.repositories.waiting_player_repo import WaitingPlayerRepository


class WaitingPlayerRepositoryImpl(WaitingPlayerRepository):

    def __init__(self):
        self._waiting_players: List[Player] = []

    def add(self, player: Player) -> None:
        self._waiting_players.append(player)

    def get_all(self) -> List[Player]:
        return list(self._waiting_players)

    def remove(self, player: Player) -> None:
        if player in self._waiting_players:
            self._waiting_players.remove(player)
