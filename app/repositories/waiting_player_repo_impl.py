from typing import List, Optional

from app.models.player import Player
from app.models.match import Match
from app.models.game_mode import GameMode
from app.repositories.waiting_player_repo import WaitingPlayerRepository


class WaitingPlayerRepositoryImpl(WaitingPlayerRepository):

    def __init__(self, elo_threshold: int = 100):
        self._waiting_players: List[Player] = []
        self._elo_threshold = elo_threshold

    def add(self, player: Player) -> None:
        self._waiting_players.append(player)

    def try_match(self, player: Player) -> Optional[Match]:
        for waiting_player in self._waiting_players:
            if waiting_player.player_id == player.player_id:
                continue

            if abs(waiting_player.elo - player.elo) <= self._elo_threshold:
                self._waiting_players.remove(waiting_player)
                self._waiting_players.remove(player)

                return Match(
                    players=[waiting_player, player],
                    game_mode=GameMode.CLASSIC
                )

        return None

    def get_all(self) -> List[Player]:
        return list(self._waiting_players)

    def remove(self, player: Player) -> None:
        if player in self._waiting_players:
            self._waiting_players.remove(player)
