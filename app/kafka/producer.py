import json
from typing import Optional


class KafkaProducerClient:
    def __init__(self, producer):
        self._producer = producer

    def send(self, topic: str, message: dict, timeout_seconds: int = 10) -> Optional[dict]:
        """
        Publish a message and confirm delivery.

        Returns metadata dict on success, raises exception on failure.
        """
        payload = json.dumps(message).encode("utf-8")

        # kafka-python returns a FutureRecordMetadata
        future = self._producer.send(topic, value=payload)

        # Block until the broker acknowledges the write (or fails)
        record_metadata = future.get(timeout=timeout_seconds)

        # Force-send any buffered messages (useful for demos / correctness)
        self._producer.flush(timeout=timeout_seconds)

        return {
            "topic": record_metadata.topic,
            "partition": record_metadata.partition,
            "offset": record_metadata.offset,
        }
