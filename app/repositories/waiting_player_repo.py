from abc import ABC, abstractmethod
from typing import List
from app.models.player import Player


class WaitingPlayerRepository(ABC):
    """
    Contract for repositories that manage players waiting for matchmaking.

    This repository represents an in-memory (or distributed) waiting lobby
    owned by a single matchmaking worker. It stores ONLY state and must not
    contain any matchmaking logic such as ELO rules, team balancing, or
    match creation.

    All matchmaking decisions belong to Strategy classes, not here.
    """

    @abstractmethod
    def add(self, player: Player) -> None:
        """
        Add a player to the waiting pool.

        This method simply registers the player as waiting for a match.
        No matchmaking logic is allowed here.

        Args:
            player (Player): The player entering the matchmaking queue.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Player]:
        """
        Retrieve all players currently waiting for matchmaking.

        This method is used by matchmaking strategies (Classic, Duo,
        Tournament) to inspect the current lobby and decide whether
        a valid match can be formed.

        The returned list MUST be a copy so that external code cannot
        modify the repository state directly.

        Returns:
            List[Player]: A snapshot of all players currently waiting.
        """
        pass

    @abstractmethod
    def remove(self, player: Player) -> None:
        """
        Remove a specific player from the waiting pool.

        This method is typically called after a match has been created,
        so that matched players are no longer considered for future matches.

        Args:
            player (Player): The player to remove from the waiting pool.
        """
        pass
