from abc import ABC, abstractmethod
from app.models.player import Player
from app.models.game_mode import GameMode
from app.models.matchmaking_event import MatchmakingEvent


class MatchmakingService(ABC):
    """
    Contract for matchmaking enqueue operations.
    Responsible for placing players into matchmaking queues.
    """

    @abstractmethod
    def enqueue_player(
            self,
            player: Player,
            game_mode: GameMode
    ) -> MatchmakingEvent:
        """
        Enqueue a player for matchmaking.

        Args:
            player (Player): Player requesting matchmaking
            game_mode (GameMode): Desired game mode

        Returns:
            MatchmakingEvent: The event that was published
        """
        pass
