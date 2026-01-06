from app.kafka.consumer import KafkaConsumerClient
from app.services.matchmaking_strategy_duo_impl import DuoMatchmakingStrategy
from app.repositories.waiting_player_repo_impl import WaitingPlayerRepositoryImpl
from app.services.game_session_client import GameSessionClient
from app.models.player import Player


class DuoMatchmakingWorker:

    def __init__(self):
        self._consumer = KafkaConsumerClient(
            topic="match.duo",
            group_id="duo-workers",
            bootstrap_servers="localhost:9092"
        )

        self._repository = WaitingPlayerRepositoryImpl()
        self._strategy = DuoMatchmakingStrategy(self._repository)
        self._game_service = GameSessionClient()

    def start(self):
        print("Duo Matchmaking Worker started...")

        for event in self._consumer.listen():
            player = Player(**event["player"])
            match = self._strategy.handle_player(player)

            if match:
                self._game_service.create_session(match)
