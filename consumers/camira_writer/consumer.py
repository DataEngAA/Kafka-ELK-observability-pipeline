"""
Phase 3 consumer: reads Camira fabric change-detection events from Kafka
and writes them to Elasticsearch. Same idempotent-write pattern as
consumers/es_writer (deterministic doc ID, commit-after-write) — see that
file's docstring for the reasoning. Kept as a separate consumer rather than
a shared generic one for now; see docs/Memory.md decision log.
"""

import hashlib
import json
import logging
import os
import sys
import signal

import httpx
from confluent_kafka import DeserializingConsumer, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [consumer.camira_writer] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/app.log")],
)
log = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "camira-fabrics-raw")
KAFKA_GROUP_ID = os.environ.get("KAFKA_GROUP_ID", "es-writer-camira")
SCHEMA_REGISTRY_URL = os.environ.get("SCHEMA_REGISTRY_URL", "http://localhost:8081")

ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
ELASTICSEARCH_INDEX = os.environ.get("ELASTICSEARCH_INDEX", "camira-fabric-events")


def deterministic_doc_id(source: str, record_id: str, event_type: str, content_hash: str) -> str:
    """Include content_hash in the ID (unlike the CPSC consumer) because for
    this source, each distinct change IS a distinct event worth keeping —
    we want a history of changes per product, not one overwritten doc."""
    raw = f"{source}:{record_id}:{event_type}:{content_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def write_to_elasticsearch(event: dict) -> bool:
    doc_id = deterministic_doc_id(
        event["source"], event["record_id"], event["event_type"], event["content_hash"]
    )
    url = f"{ELASTICSEARCH_URL}/{ELASTICSEARCH_INDEX}/_doc/{doc_id}"

    es_document = dict(event)
    try:
        es_document["fields"] = json.loads(event["fields_json"])
        del es_document["fields_json"]
    except (json.JSONDecodeError, TypeError):
        log.warning("Could not parse fields_json for record_id=%s; storing raw.", event.get("record_id"))

    try:
        response = httpx.put(url, json=es_document, timeout=15.0)
        response.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        log.error("Failed to write doc %s to Elasticsearch: %s", doc_id, exc)
        return False


class GracefulShutdown(Exception):
    pass


def _handle_sigterm(signum, frame):
    raise GracefulShutdown()


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
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([KAFKA_TOPIC])
    signal.signal(signal.SIGTERM, _handle_sigterm)

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

            event = msg.value()
            if event is None:
                log.warning("Skipping message with no deserializable value at offset %s", msg.offset())
                consumer.commit(msg)
                continue

            success = write_to_elasticsearch(event)
            if success:
                consumer.commit(msg)
                log.info(
                    "Wrote %s event for record_id=%s to Elasticsearch (offset %s)",
                    event.get("event_type"), event.get("record_id"), msg.offset(),
                )
            else:
                log.warning(
                    "Write failed for record_id=%s — NOT committing offset, will retry on next poll.",
                    event.get("record_id"),
                )

    except (KeyboardInterrupt, GracefulShutdown):
        log.info("Shutting down consumer...")
    finally:
        consumer.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
