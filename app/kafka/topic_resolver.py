from app.models.game_mode import GameMode


class TopicResolver:
    _TOPIC_MAP = {
        GameMode.CLASSIC: "match.classic",
        GameMode.SOLO: "match.solo",
        GameMode.DUO: "match.duo",
        GameMode.BLITZ: "match.blitz",
        GameMode.TOURNAMENT: "match.tournament",
    }

    @classmethod
    def resolve(cls, game_mode: GameMode) -> str:
        if game_mode not in cls._TOPIC_MAP:
            raise ValueError(f"Unsupported game mode: {game_mode}")
        return cls._TOPIC_MAP[game_mode]
