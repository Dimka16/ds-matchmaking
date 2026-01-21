from marshmallow import Schema, fields, post_load, ValidationError
from app.models.player import Player
from app.models.game_mode import GameMode


def _validate_game_mode(value: str) -> GameMode:
    try:
        return GameMode(value)
    except Exception:
        allowed = [gm.value for gm in GameMode]
        raise ValidationError(f"Invalid game_mode '{value}'. Allowed: {allowed}")


class MatchmakingJoinSchema(Schema):
    player_id = fields.Int(required=False, allow_none=True)
    username = fields.Str(required=False, allow_none=True)
    elo = fields.Int(required=True)
    region = fields.Str(required=True)
    game_mode = fields.Str(required=True)

    @post_load
    def make_domain_objects(self, data, **kwargs):
        game_mode = _validate_game_mode(data["game_mode"])

        player = Player(
            player_id=int(data.get("player_id") or 0),
            username=str(data.get("username") or ""),
            elo=int(data["elo"]),
            region=str(data["region"]),
        )

        return player, game_mode
