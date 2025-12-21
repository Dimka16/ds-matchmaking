from typing import Optional

from app.models.player import Player
from app.models.match import Match
from app.repositories.waiting_player_repo import WaitingPlayerRepository
from app.services.matchmaking_strategy import MatchmakingStrategy


class ClassicMatchmakingStrategy(MatchmakingStrategy):

    def __init__(self, repository: WaitingPlayerRepository):
        self._repository = repository

    def handle_player(self, player: Player) -> Optional[Match]:
        self._repository.add(player)
        return self._repository.try_match(player)
