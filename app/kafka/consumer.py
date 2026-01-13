import json
from kafka import KafkaConsumer


class KafkaConsumerClient:

    def __init__(self, topic: str, group_id: str, bootstrap_servers: str):
        self._consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode("utf-8"))
        )

    def listen(self):
        for message in self._consumer:
            yield message.value
