from typing import Optional, List

from app.models.player import Player
from app.models.match import Match
from app.models.game_mode import GameMode
from app.repositories.waiting_player_repo import WaitingPlayerRepository
from app.services.matchmaking_strategy import MatchmakingStrategy


class ClassicMatchmakingStrategy(MatchmakingStrategy):

    def __init__(self, repository: WaitingPlayerRepository, elo_threshold: int = 100):
        self._repository = repository
        self._elo_threshold = elo_threshold

    def handle_player(self, player: Player) -> Optional[Match]:
        self._repository.add(player)

        players: List[Player] = self._repository.get_all()

        for waiting_player in players:
            if waiting_player.player_id == player.player_id:
                continue

            if abs(waiting_player.elo - player.elo) <= self._elo_threshold:
                self._repository.remove(waiting_player)
                self._repository.remove(player)

                return Match(
                    players=[waiting_player, player],
                    game_mode=GameMode.CLASSIC
                )

        return None
