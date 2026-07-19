"""
Phase 2 consumer: reads Avro-serialized events from the recalls-raw Kafka
topic (deserializing via the schema registry) and writes them to
Elasticsearch.

Idempotency: the Elasticsearch document ID is a deterministic SHA-256 hash
of (source + record_id), so re-processing the same message overwrites the
same document instead of creating a duplicate.

Offsets are committed only AFTER a successful write, per docs/Rules.md.
"""

import hashlib
import json
import logging
import sys

import httpx
from confluent_kafka import DeserializingConsumer, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [consumer.es_writer] %(message)s",
)
log = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "recalls-raw"
KAFKA_GROUP_ID = "es-writer-recalls"
SCHEMA_REGISTRY_URL = "http://localhost:8081"

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

    # Expand payload_json back into a nested object so it's queryable in ES,
    # rather than sitting there as an opaque string.
    es_document = dict(event)
    try:
        es_document["payload"] = json.loads(event["payload_json"])
        del es_document["payload_json"]
    except (json.JSONDecodeError, TypeError):
        log.warning("Could not parse payload_json for record_id=%s; storing raw.", event.get("record_id"))

    try:
        response = httpx.put(url, json=es_document, timeout=15.0)
        response.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        log.error("Failed to write doc %s to Elasticsearch: %s", doc_id, exc)
        return False


def main() -> int:
    schema_registry_client = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
    avro_deserializer = AvroDeserializer(schema_registry_client)
    string_deserializer = StringDeserializer("utf_8")

    consumer = DeserializingConsumer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": KAFKA_GROUP_ID,
            "key.deserializer": string_deserializer,
            "value.deserializer": avro_deserializer,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,  # we commit manually after a successful write
        }
    )
    consumer.subscribe([KAFKA_TOPIC])

    log.info("Consumer started (Avro mode). Listening on topic '%s'...", KAFKA_TOPIC)

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

            event = msg.value()
            if event is None:
                log.warning("Skipping message with no deserializable value at offset %s", msg.offset())
                consumer.commit(msg)
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
