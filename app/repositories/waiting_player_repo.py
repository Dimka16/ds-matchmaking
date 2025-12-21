from abc import ABC, abstractmethod
from typing import Optional, List

from app.models.player import Player
from app.models.match import Match


class WaitingPlayerRepository(ABC):
    """
    Contract for repositories that manage players waiting for matchmaking.

    This repository stores ephemeral matchmaking state and provides
    operations needed by different matchmaking strategies (Classic, Duo,
    Tournament). It intentionally does NOT persist data or communicate
    with external systems.
    """

    @abstractmethod
    def add(self, player: Player) -> None:
        """
        Add a player to the waiting pool.

        This method registers the player as waiting for matchmaking.
        No matching logic should be performed here.

        Args:
            player (Player): The player entering the matchmaking queue.
        """
        pass

    @abstractmethod
    def try_match(self, player: Player) -> Optional[Match]:
        """
        Attempt to form a match that includes the given player.

        This method is primarily used by matchmaking strategies that
        perform incremental matching (e.g. Classic / 1v1).

        Implementations should:
        - Inspect currently waiting players
        - Apply matchmaking constraints (e.g. ELO threshold)
        - Remove matched players from the waiting pool
        - Return a Match if successful

        Args:
            player (Player): The player for whom a match attempt is made.

        Returns:
            Optional[Match]:
                A Match object if a valid match is formed, otherwise None.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Player]:
        """
        Retrieve all players currently waiting for matchmaking.

        This method is useful for matchmaking strategies that require
        batch-based matching (e.g. Duo or Tournament), where a match
        is formed only after a minimum number of players has accumulated.

        Returns:
            List[Player]:
                A list of all players currently waiting in the repository.
                The returned list should be a copy to prevent external
                modification of internal state.
        """
        pass

    @abstractmethod
    def remove(self, player: Player) -> None:
        """
        Remove a specific player from the waiting pool.

        This method is typically used after a match has been formed,
        to ensure matched players are no longer considered for future
        matchmaking attempts.

        Args:
            player (Player): The player to remove from the waiting pool.
        """
        pass
