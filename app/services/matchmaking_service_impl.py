from app.services.matchmaking_service import MatchmakingService
from app.models.matchmaking_event import MatchmakingEvent
from app.models.player import Player
from app.models.game_mode import GameMode
from app.util.topic_resolver import TopicResolver
from app.util.kafka_producer import KafkaProducerClient


class MatchmakingServiceImpl(MatchmakingService):

    def __init__(self, kafka_producer: KafkaProducerClient):
        self._kafka_producer = kafka_producer

    def enqueue_player(
            self,
            player: Player,
            game_mode: GameMode
    ) -> MatchmakingEvent:
        event = MatchmakingEvent(
            player=player,
            game_mode=game_mode
        )

        topic = TopicResolver.resolve(game_mode)

        self._kafka_producer.send(
            topic=topic,
            message=event.to_dict()
        )

        return event