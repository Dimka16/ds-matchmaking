class Player:
    def __init__(self, player_id: int, username: str, elo: int, region: str):
        self.player_id = player_id
        self.username = username
        self.elo = elo
        self.region = region

    def to_dict(self) -> dict:
        return {
            "player_id": self.player_id,
            "username": self.username,
            "elo": self.elo,
            "region": self.region,
        }
