from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.player import Player


class WaitingPlayerRepository(ABC):
    @abstractmethod
    def add(self, player: Player) -> None:
        """Add or update a player in the waiting pool (idempotent by player_id)."""
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[Player]:
        """Return a copy snapshot of waiting players."""
        raise NotImplementedError

    @abstractmethod
    def remove(self, player: Player) -> None:
        """Remove a player from the pool (should work even if object instance differs)."""
        raise NotImplementedError

    @abstractmethod
    def remove_by_id(self, player_id: int) -> None:
        """Remove a player from the pool by their id (recommended for leave events)."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, player_id: int) -> Optional[Player]:
        """Optional helper: retrieve a player by id if present."""
        raise NotImplementedError
