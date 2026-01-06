from typing import Optional

from app.models.player import Player
from app.models.match import Match
from app.models.game_mode import GameMode
from app.repositories.waiting_player_repo import WaitingPlayerRepository
from app.services.matchmaking_strategy import MatchmakingStrategy


class DuoMatchmakingStrategy(MatchmakingStrategy):

    def __init__(self, repository: WaitingPlayerRepository, team_balance_threshold: int = 200):
        self._repository = repository
        self._team_balance_threshold = team_balance_threshold

    def handle_player(self, player: Player) -> Optional[Match]:
        self._repository.add(player)

        players = self._repository.get_all()
        if len(players) < 4:
            return None

        sorted_players = sorted(players, key=lambda p: p.elo)

        p1 = sorted_players[0]
        p2 = sorted_players[1]
        p3 = sorted_players[2]
        p4 = sorted_players[3]

        team_a_elo = p1.elo + p4.elo
        team_b_elo = p2.elo + p3.elo

        if abs(team_a_elo - team_b_elo) > self._team_balance_threshold:
            return None

        self._repository.remove(p1)
        self._repository.remove(p2)
        self._repository.remove(p3)
        self._repository.remove(p4)

        return Match(
            players=[p1, p2, p3, p4],
            game_mode=GameMode.DUO
        )
