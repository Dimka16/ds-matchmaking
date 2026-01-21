from typing import Optional, List
from app.models.player import Player
from app.models.match import Match
from app.models.game_mode import GameMode
from app.repositories.waiting_player_repo import WaitingPlayerRepository
from app.services.matchmaking_strategy import MatchmakingStrategy


class DuoMatchmakingStrategy(MatchmakingStrategy):
    def __init__(self, repository: WaitingPlayerRepository, team_balance_threshold: int = 200):
        self._repository = repository
        self._team_balance_threshold = team_balance_threshold

    def remove_player(self, player_id: int) -> None:
        self._repository.remove_by_id(player_id)

    def handle_player(self, player: Player) -> Optional[Match]:
        self._repository.add(player)

        pool: List[Player] = [
            p for p in self._repository.get_all()
            if p.region == player.region
        ]

        if len(pool) < 4:
            return None

        # Use top 4 by ELO from same region
        sorted_players = sorted(pool, key=lambda p: p.elo, reverse=True)[:4]
        p1, p2, p3, p4 = sorted_players

        # Simple balancing: 1+4 vs 2+3
        team_a_elo = p1.elo + p4.elo
        team_b_elo = p2.elo + p3.elo

        if abs(team_a_elo - team_b_elo) > self._team_balance_threshold:
            return None

        for p in (p1, p2, p3, p4):
            self._repository.remove_by_id(p.player_id)

        return Match(players=[p1, p2, p3, p4], game_mode=GameMode.DUO)
