from typing import Optional, List
from app.models.player import Player
from app.models.match import Match
from app.models.game_mode import GameMode
from app.repositories.waiting_player_repo import WaitingPlayerRepository
from app.services.matchmaking_strategy import MatchmakingStrategy


class TournamentMatchmakingStrategy(MatchmakingStrategy):
    def __init__(self, repository: WaitingPlayerRepository, bracket_size: int = 8):
        if bracket_size not in (8, 16, 32):
            raise ValueError("bracket_size must be 8, 16, or 32")
        self._repository = repository
        self._bracket_size = bracket_size

    def remove_player(self, player_id: int) -> None:
        self._repository.remove_by_id(player_id)

    def handle_player(self, player: Player) -> Optional[Match]:
        self._repository.add(player)

        pool: List[Player] = [
            p for p in self._repository.get_all()
            if p.region == player.region
        ]

        if len(pool) < self._bracket_size:
            return None

        selected = pool[: self._bracket_size]
        seeded = sorted(selected, key=lambda p: p.elo, reverse=True)

        for p in selected:
            self._repository.remove_by_id(p.player_id)

        return Match(players=seeded, game_mode=GameMode.TOURNAMENT)
