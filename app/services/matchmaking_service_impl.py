# app/services/matchmaking_service_impl.py
from app.models.matchmaking_event import MatchmakingEvent
from app.kafka.topic_resolver import TopicResolver

class MatchmakingServiceImpl:
    def __init__(self, kafka_producer):
        self._kafka_producer = kafka_producer

    def enqueue_player(self, player, game_mode, action="join"):
        event = MatchmakingEvent(player=player, game_mode=game_mode, action=action)
        topic = TopicResolver.resolve(game_mode)

        self._kafka_producer.send(topic=topic, message=event.to_dict())
        return event
