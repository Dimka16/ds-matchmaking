import os
import requests


class GameSessionClient:
    def __init__(self):
        self._api_base = os.getenv("API_BASE_URL", "http://api:5000")

    def create_session(self, match):
        payload = {
            "game_mode": match.game_mode.value,
            "players": [
                {
                    "player_id": p.player_id,
                    "username": p.username,
                    "elo": p.elo,
                    "region": p.region
                }
                for p in match.players
            ]
        }

        url = f"{self._api_base}/sessions"
        r = requests.post(url, json=payload, timeout=5)
        r.raise_for_status()
        return r.json()
