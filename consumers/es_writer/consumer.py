"""
Phase 1 consumer (thin slice): reads events from the recalls-raw Kafka
topic and writes them to Elasticsearch.

Idempotency: the Elasticsearch document ID is a deterministic SHA-256 hash
of (source + record_id), so re-processing the same message (e.g. after a
consumer restart) overwrites the same document instead of creating a
duplicate. This is the idempotent-consumer pattern documented in
docs/Architecture.md section 6, chosen over true exactly-once semantics.

Offsets are committed only AFTER a successful write, per docs/Rules.md.
"""

import hashlib
import json
import logging
import sys

import httpx
from confluent_kafka import Consumer, KafkaError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [consumer.es_writer] %(message)s",
)
log = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "recalls-raw"
KAFKA_GROUP_ID = "es-writer-recalls"

ELASTICSEARCH_URL = "http://localhost:9200"
ELASTICSEARCH_INDEX = "recalls-events"


def deterministic_doc_id(source: str, record_id: str) -> str:
    """Same (source, record_id) always produces the same ES document ID,
    making writes safe to repeat (idempotent)."""
    raw = f"{source}:{record_id}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def write_to_elasticsearch(event: dict) -> bool:
    doc_id = deterministic_doc_id(event["source"], event["record_id"])
    url = f"{ELASTICSEARCH_URL}/{ELASTICSEARCH_INDEX}/_doc/{doc_id}"

    try:
        response = httpx.put(url, json=event, timeout=15.0)
        response.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        log.error("Failed to write doc %s to Elasticsearch: %s", doc_id, exc)
        return False


def main() -> int:
    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": KAFKA_GROUP_ID,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,  # we commit manually after a successful write
        }
    )
    consumer.subscribe([KAFKA_TOPIC])

    log.info("Consumer started. Listening on topic '%s'...", KAFKA_TOPIC)

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                log.error("Kafka error: %s", msg.error())
                continue

            try:
                event = json.loads(msg.value())
            except (json.JSONDecodeError, TypeError) as exc:
                log.error("Skipping unparseable message at offset %s: %s", msg.offset(), exc)
                consumer.commit(msg)  # don't retry a permanently broken message forever
                continue

            success = write_to_elasticsearch(event)
            if success:
                consumer.commit(msg)
                log.info(
                    "Wrote record_id=%s to Elasticsearch (offset %s)",
                    event.get("record_id"),
                    msg.offset(),
                )
            else:
                log.warning(
                    "Write failed for record_id=%s — NOT committing offset, will retry on next poll.",
                    event.get("record_id"),
                )

    except KeyboardInterrupt:
        log.info("Shutting down consumer...")
    finally:
        consumer.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
