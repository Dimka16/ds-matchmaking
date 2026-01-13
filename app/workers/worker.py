from app.kafka.consumer import KafkaConsumerClient
from app.services.strategy_resolver import StrategyResolver
from app.services.game_session_client import GameSessionClient
from app.models.player import Player
from app.models.game_mode import GameMode


class MatchmakingWorker:

    def __init__(self):
        self._consumer = KafkaConsumerClient(
            topic="matchmaking",
            group_id="matchmaking-workers",
            bootstrap_servers="localhost:9092"
        )

        self._resolver = StrategyResolver()
        self._game_service = GameSessionClient()

    def start(self):
        print("Matchmaking Worker started...")

        for event in self._consumer.listen():
            player = Player(**event["player"])
            game_mode = GameMode(event["game_mode"])

            strategy = self._resolver.resolve(game_mode)
            match = strategy.handle_player(player)

            if match:
                self._game_service.create_session(match)
