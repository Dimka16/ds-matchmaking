from app.models.game_mode import GameMode
from app.repositories.waiting_player_repo_impl import WaitingPlayerRepositoryImpl

from app.services.matchmaking_strategy_classic_impl import ClassicMatchmakingStrategy
from app.services.matchmaking_strategy_solo_impl import SoloMatchmakingStrategy
from app.services.matchmaking_strategy_duo_impl import DuoMatchmakingStrategy
from app.services.matchmaking_strategy_blitz_impl import BlitzMatchmakingStrategy
from app.services.matchmaking_strategy_tournament_impl import TournamentMatchmakingStrategy


class StrategyResolver:
    def __init__(self):
        self._repositories = {
            GameMode.CLASSIC: WaitingPlayerRepositoryImpl(),
            GameMode.SOLO: WaitingPlayerRepositoryImpl(),
            GameMode.DUO: WaitingPlayerRepositoryImpl(),
            GameMode.BLITZ: WaitingPlayerRepositoryImpl(),
            GameMode.TOURNAMENT: WaitingPlayerRepositoryImpl(),
        }

        self._strategies = {
            GameMode.CLASSIC: ClassicMatchmakingStrategy(self._repositories[GameMode.CLASSIC]),
            GameMode.SOLO: SoloMatchmakingStrategy(self._repositories[GameMode.SOLO]),
            GameMode.DUO: DuoMatchmakingStrategy(self._repositories[GameMode.DUO]),
            GameMode.BLITZ: BlitzMatchmakingStrategy(self._repositories[GameMode.BLITZ]),
            GameMode.TOURNAMENT: TournamentMatchmakingStrategy(self._repositories[GameMode.TOURNAMENT]),
        }

    def resolve(self, game_mode: GameMode):
        return self._strategies[game_mode]
