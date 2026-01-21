from typing import Optional, List
from app.models.player import Player
from app.models.match import Match
from app.models.game_mode import GameMode
from app.repositories.waiting_player_repo import WaitingPlayerRepository
from app.services.matchmaking_strategy import MatchmakingStrategy


class SoloMatchmakingStrategy(MatchmakingStrategy):
    """
    SOLO = 1v1 with stricter rules:
    - same region only
    - lower ELO threshold (default 50)
    - sort by ELO and match adjacent players if within threshold
    """
    def __init__(self, repository: WaitingPlayerRepository, elo_threshold: int = 50):
        self._repository = repository
        self._elo_threshold = elo_threshold

    def remove_player(self, player_id: int) -> None:
        self._repository.remove_by_id(player_id)

    def handle_player(self, player: Player) -> Optional[Match]:
        self._repository.add(player)

        pool: List[Player] = [
            p for p in self._repository.get_all()
            if p.region == player.region
        ]
        if len(pool) < 2:
            return None

        pool_sorted = sorted(pool, key=lambda p: p.elo)

        # adjacent scan
        for i in range(len(pool_sorted) - 1):
            a = pool_sorted[i]
            b = pool_sorted[i + 1]
            if abs(a.elo - b.elo) <= self._elo_threshold:
                self._repository.remove_by_id(a.player_id)
                self._repository.remove_by_id(b.player_id)
                return Match(players=[a, b], game_mode=GameMode.SOLO)

        return None
