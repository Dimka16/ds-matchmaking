"""
Domain model representing a finalized matchmaking result.

A Match is a high-level business concept that groups together
one or more players that have been successfully matched
according to a specific game mode.

This abstraction allows the matchmaking system to support
different matchmaking strategies:
- Classic / Duo: 2 players
- Tournament: N players
- Future modes without changing service contracts
"""

from typing import List
from app.models.player import Player
from app.models.game_mode import GameMode


class Match:
    """
    Represents a group of players matched together to start a game session.

    This object is produced by the matchmaking logic and later consumed
    by the Game Session Service to create a persistent game session.
    """

    def __init__(self, players: List[Player], game_mode: GameMode):
        """
        Initialize a Match instance.

        Args:
            players (List[Player]):
                List of players included in the match.
                The size of this list depends on the game mode.
            game_mode (GameMode):
                The game mode for which this match was created.
        """
        self.players = players
        self.game_mode = game_mode

    def __repr__(self) -> str:
        """
        Developer-friendly string representation of the match.
        """
        player_ids = [p.player_id for p in self.players]
        return f"<Match game_mode={self.game_mode.value} players={player_ids}>"
