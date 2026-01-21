import os
from kafka import KafkaProducer


def create_kafka_producer() -> KafkaProducer:
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        acks="all",          # broker acknowledges write
        retries=5,           # retry transient failures
        linger_ms=5,         # small batching without big latency
        request_timeout_ms=10000,
        max_block_ms=10000
    )
