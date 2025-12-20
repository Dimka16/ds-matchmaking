"""
Schemas for Matchmaking join requests using Marshmallow.

- MatchmakingJoinSchema: validates and deserializes incoming matchmaking join payloads.
- Maps validated data directly into domain models (Player, GameMode).

Includes pre-load processing to trim string fields.
"""

from marshmallow import (
    Schema,
    fields,
    validate,
    ValidationError,
    EXCLUDE,
    pre_load,
    post_load
)

from app.models.player import Player
from app.models.game_mode import GameMode


class MatchmakingJoinSchema(Schema):
    """
    Schema for incoming matchmaking join payloads.

    - Validates and deserializes client-provided data.
    - Preprocesses string fields: trims whitespace.
    - Enforces numeric constraints on ELO.
    - Validates game mode against supported enum values.
    - Maps payload directly into domain objects.
    """

    class Meta:
        # dropping unknown fields instead of having errors
        unknown = EXCLUDE

    @pre_load
    def strip_strings(self, data, **kwargs):
        """
        Trim leading/trailing whitespace on string fields.
        """
        for key in ("username", "region", "game_mode"):
            val = data.get(key)
            if isinstance(val, str):
                data[key] = val.strip()
        return data

    """
    Player ID:
      - Required
      - Must be a positive integer
    """
    player_id = fields.Int(
        required=True,
        validate=validate.Range(min=1),
        error_messages={
            "required": "Player ID is required.",
            "invalid": "Player ID must be a positive integer."
        }
    )

    """
    Username:
      - Required
      - Trimmed
      - Must be between 1 and 50 characters
    """
    username = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={
            "required": "Username is required.",
            "invalid": "Username must be a non-empty string."
        }
    )

    """
    ELO rating:
      - Required
      - Must be a non-negative integer
    """
    elo = fields.Int(
        required=True,
        validate=validate.Range(min=0),
        error_messages={
            "required": "ELO rating is required.",
            "invalid": "ELO must be a non-negative integer."
        }
    )

    """
    Region:
      - Required
      - Trimmed
      - Must be between 1 and 20 characters
    """
    region = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=20),
        error_messages={
            "required": "Region is required.",
            "invalid": "Region must be a non-empty string."
        }
    )

    """
    Game mode:
      - Required
      - Must be one of the supported game modes
    """
    game_mode = fields.Str(
        required=True,
        error_messages={
            "required": "Game mode is required.",
            "invalid": "Game mode must be a string."
        }
    )

    @staticmethod
    def _validate_game_mode(value: str) -> GameMode:
        try:
            return GameMode(value)
        except ValueError:
            raise ValidationError(f"Unsupported game mode: '{value}'")

    @post_load
    def make_domain_objects(self, data, **kwargs):
        """
        Map validated input data into domain models.
        """
        game_mode = self._validate_game_mode(data["game_mode"])

        player = Player(
            player_id=data["player_id"],
            username=data["username"],
            elo=data["elo"],
            region=data["region"]
        )

        return player, game_mode
