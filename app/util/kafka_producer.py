import json


class KafkaProducerClient:

    def __init__(self, producer):
        self._producer = producer

    def send(self, topic: str, message: dict):
        payload = json.dumps(message).encode("utf-8")
        self._producer.send(topic, payload)
