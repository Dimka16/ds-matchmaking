from abc import ABC, abstractmethod
from typing import Optional

from app.models.player import Player
from app.models.match import Match


class MatchmakingStrategy(ABC):
    """
    Abstract strategy interface for matchmaking algorithms.

    Each implementation of this interface represents a distinct
    matchmaking algorithm for a specific game mode (e.g. Classic,
    Tournament, Blitz).

    The purpose of this abstraction is to:
    - Decouple the matchmaking worker from concrete matchmaking logic
    - Allow different algorithms per game mode
    - Enable clean extensibility without modifying existing code

    Implementations are expected to manage temporary matchmaking state
    (typically via a repository) and decide when a valid match can be formed.
    """

    @abstractmethod
    def handle_player(self, player: Player) -> Optional[Match]:
        """
        Handle a newly queued player and attempt to form a match.

        This method is invoked whenever a player enters the matchmaking
        system for a given game mode. The strategy implementation should:
        - Register the player as waiting (if needed)
        - Apply the matchmaking algorithm specific to the game mode
        - Return a Match when enough compatible players are available

        Args:
            player (Player):
                The player who has entered matchmaking.

        Returns:
            Optional[Match]:
                - A Match object if a valid match is formed
                - None if no match can be formed at this time
        """
        pass

    @abstractmethod
    def remove_player(self, player_id: int) -> None:
        """Remove a player from the waiting pool by id."""
        pass

