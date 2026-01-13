from app.models.game_mode import GameMode
from app.services.matchmaking_strategy_classic_impl import ClassicMatchmakingStrategy
from app.services.matchmaking_strategy_duo_impl import DuoMatchmakingStrategy
# from app.services.matchmaking_strategy_tournament_impl import TournamentMatchmakingStrategy
from app.repositories.waiting_player_repo_impl import WaitingPlayerRepositoryImpl


class StrategyResolver:

    def __init__(self):
        self._repositories = {
            GameMode.CLASSIC: WaitingPlayerRepositoryImpl(),
            GameMode.DUO: WaitingPlayerRepositoryImpl(),
            GameMode.TOURNAMENT: WaitingPlayerRepositoryImpl()
        }

        self._strategies = {
            GameMode.CLASSIC: ClassicMatchmakingStrategy(self._repositories[GameMode.CLASSIC]),
            GameMode.DUO: DuoMatchmakingStrategy(self._repositories[GameMode.DUO])
            # TODO: IMPLEMENT TOURNAMENT
            #   GameMode.TOURNAMENT: TournamentMatchmakingStrategy(self._repositories[GameMode.TOURNAMENT])
        }

    def resolve(self, game_mode: GameMode):
        return self._strategies[game_mode]
