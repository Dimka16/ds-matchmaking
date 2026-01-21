import os
from app.kafka.consumer import KafkaConsumerClient
from app.services.strategy_resolver import StrategyResolver
from app.services.game_session_client import GameSessionClient
from app.models.player import Player
from app.models.game_mode import GameMode
from app.kafka.topic_resolver import TopicResolver


class MatchmakingWorker:
    def __init__(self, game_mode: GameMode):
        self._game_mode = game_mode
        bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

        topic = TopicResolver.resolve(game_mode)
        group_id = f"{game_mode.value}-workers"

        self._consumer = KafkaConsumerClient(
            topic=topic,
            group_id=group_id,
            bootstrap_servers=bootstrap
        )

        self._resolver = StrategyResolver()
        self._strategy = self._resolver.resolve(game_mode)
        self._game_service = GameSessionClient()

    def start(self):
        print(f"{self._game_mode.value.upper()} Matchmaking Worker started...")

        for event in self._consumer.listen():

            # ---- hardening: avoid crashing on malformed messages ----
            if not isinstance(event, dict) or "player" not in event or "game_mode" not in event:
                print(f"[{self._game_mode.value}] Skipping malformed event: {event}")
                continue

            # ---- observability: log what we received ----
            event_id = event.get("event_id", "n/a")
            player_id = event.get("player", {}).get("player_id", "n/a")
            print(f"[{self._game_mode.value}] event_id={event_id} player_id={player_id}")

            action = (event.get("action") or "join").lower()

            p = event.get("player") or {}
            required = {"player_id", "username", "elo", "region"}
            if not required.issubset(p.keys()):
                print(f"[{self._game_mode.value}] malformed player payload: {p}")
                continue

            player = Player(**p)
            game_mode = GameMode(event["game_mode"])

            if game_mode != self._game_mode:
                continue

            strategy = self._resolver.resolve(game_mode)

            if action == "leave":
                if hasattr(self._strategy, "remove_player"):
                    self._strategy.remove_player(player.player_id)
                else:
                    try:
                        self._strategy._repository.remove_by_id(player.player_id)
                    except Exception:
                        pass
                continue

            # default action == "join"
            match = strategy.handle_player(player)
            if match:
                self._game_service.create_session(match)
