import time
from typing import Optional, List, Dict

from app.models.player import Player
from app.models.match import Match
from app.models.game_mode import GameMode
from app.repositories.waiting_player_repo import WaitingPlayerRepository
from app.services.matchmaking_strategy import MatchmakingStrategy


class BlitzMatchmakingStrategy(MatchmakingStrategy):
    """
    BLITZ = fast 1v1 with time-based relaxing rules:
    - same region only
    - start with base_threshold
    - after relax_after_seconds, threshold increases every relax_every_seconds by relax_step
    - after force_after_seconds, match oldest with closest ELO regardless of threshold
    """
    def __init__(
        self,
        repository: WaitingPlayerRepository,
        base_threshold: int = 150,
        relax_after_seconds: int = 10,
        relax_every_seconds: int = 5,
        relax_step: int = 50,
        force_after_seconds: int = 45,
    ):
        self._repository = repository
        self._base_threshold = base_threshold
        self._relax_after = relax_after_seconds
        self._relax_every = relax_every_seconds
        self._relax_step = relax_step
        self._force_after = force_after_seconds

        # player_id -> join timestamp
        self._join_ts: Dict[int, float] = {}

    def remove_player(self, player_id: int) -> None:
        self._repository.remove_by_id(player_id)
        self._join_ts.pop(player_id, None)

    def handle_player(self, player: Player) -> Optional[Match]:
        now = time.time()

        self._repository.add(player)
        self._join_ts.setdefault(player.player_id, now)

        pool: List[Player] = [
            p for p in self._repository.get_all()
            if p.region == player.region
        ]
        if len(pool) < 2:
            return None

        # Find oldest waiting player in this region pool
        def ts(pid: int) -> float:
            return self._join_ts.get(pid, now)

        oldest = min(pool, key=lambda p: ts(p.player_id))
        oldest_wait = now - ts(oldest.player_id)

        # FORCE match if too old
        if oldest_wait >= self._force_after:
            candidates = [p for p in pool if p.player_id != oldest.player_id]
            closest = min(candidates, key=lambda p: abs(p.elo - oldest.elo))
            self.remove_player(oldest.player_id)
            self.remove_player(closest.player_id)
            return Match(players=[oldest, closest], game_mode=GameMode.BLITZ)

        # compute relaxed threshold based on oldest wait
        threshold = self._base_threshold
        if oldest_wait >= self._relax_after:
            extra = int((oldest_wait - self._relax_after) // self._relax_every) + 1
            threshold += extra * self._relax_step

        # Try to match oldest with closest within threshold
        candidates = [p for p in pool if p.player_id != oldest.player_id]
        closest = min(candidates, key=lambda p: abs(p.elo - oldest.elo))
        if abs(closest.elo - oldest.elo) <= threshold:
            self.remove_player(oldest.player_id)
            self.remove_player(closest.player_id)
            return Match(players=[oldest, closest], game_mode=GameMode.BLITZ)

        return None
