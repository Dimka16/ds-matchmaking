from typing import Optional, List

from app.models.player import Player
from app.models.match import Match
from app.models.game_mode import GameMode
from app.repositories.waiting_player_repo import WaitingPlayerRepository
from app.services.matchmaking_strategy import MatchmakingStrategy


class DuoMatchmakingStrategy(MatchmakingStrategy):

    def __init__(self, repository: WaitingPlayerRepository, team_size: int = 4):
        self._repository = repository
        self._team_size = team_size

    def handle_player(self, player: Player) -> Optional[Match]:
        self._repository.add(player)

        players = self._repository.get_all()
        if len(players) < self._team_size:
            return None

        matched_players: List[Player] = players[: self._team_size]

        for p in matched_players:
            self._repository.remove(p)

        return Match(
            players=matched_players,
            game_mode=GameMode.DUO
        )
