"""
SCHEMA EVOLUTION DEMO — not part of the normal pipeline, run manually once
to prove backward compatibility.

Publishes a few records using the v2 schema (which adds an optional
content_hash field) to the SAME topic as the v1 producer. The point: the
existing, unmodified consumer.py (still pointed at v1 in spirit, but really
just deserializing via the schema registry generically) should read these
v2 messages without any code changes and without erroring — proving the
schema change was truly backward compatible.

See docs/Phases.md Phase 2 and schemas/cpsc_recalls/v2.avsc.
"""

import hashlib
import json
import logging
import sys
from datetime import datetime, timezone

import httpx
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [producer.recalls] %(message)s",
)
log = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "recalls-raw"
SCHEMA_REGISTRY_URL = "http://localhost:8081"
SCHEMA_PATH = "schemas/cpsc_recalls/v2.avsc"

CPSC_API_URL = "https://www.saferproducts.gov/RestWebServices/Recall"
SOURCE_NAME = "cpsc_recalls"


def fetch_recent_recalls(limit: int = 20) -> list[dict]:
    """Fetch the most recent recalls from the CPSC public API."""
    params = {"format": "json", "RecallDateStart": "2026-06-01"}
    try:
        response = httpx.get(CPSC_API_URL, params=params, timeout=30.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        log.error("Failed to fetch recalls from CPSC API: %s", exc)
        return []

    try:
        data = response.json()
    except ValueError as exc:
        log.error("Failed to parse CPSC API response as JSON: %s", exc)
        return []

    if not isinstance(data, list):
        log.error("Unexpected CPSC API response shape (expected list)")
        return []

    return data[:limit]


def build_event(record: dict) -> dict | None:
    """Wrap a raw CPSC record in our Avro-typed event envelope."""
    record_id = record.get("RecallID") or record.get("RecallNumber")
    if not record_id:
        log.warning("Skipping record with no RecallID/RecallNumber: %s", record)
        return None

    payload_json = json.dumps(record)
    content_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

    return {
        "source": SOURCE_NAME,
        "record_id": str(record_id),
        "event_type": "discovered",
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "payload_json": payload_json,
        "content_hash": content_hash,  # NEW in v2
    }


def delivery_report(err, msg):
    if err is not None:
        log.error("Delivery failed for record %s: %s", msg.key(), err)
    else:
        log.info(
            "Delivered to %s [partition %s] offset %s",
            msg.topic(),
            msg.partition(),
            msg.offset(),
        )


def main() -> int:
    with open(SCHEMA_PATH, "r") as f:
        schema_str = f.read()

    schema_registry_client = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
    avro_serializer = AvroSerializer(schema_registry_client, schema_str)
    string_serializer = StringSerializer("utf_8")

    producer = SerializingProducer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "key.serializer": string_serializer,
            "value.serializer": avro_serializer,
        }
    )

    records = fetch_recent_recalls()
    if not records:
        log.warning("No records fetched this run — nothing to publish.")
        return 0

    published = 0
    for record in records:
        event = build_event(record)
        if event is None:
            continue

        try:
            producer.produce(
                topic=KAFKA_TOPIC,
                key=event["record_id"],
                value=event,
                on_delivery=delivery_report,
            )
            published += 1
        except BufferError:
            log.warning("Local producer queue full, flushing and retrying...")
            producer.flush()
            producer.produce(
                topic=KAFKA_TOPIC,
                key=event["record_id"],
                value=event,
                on_delivery=delivery_report,
            )
            published += 1
        except Exception as exc:
            log.error("Failed to serialize/produce record_id=%s: %s", event["record_id"], exc)

    producer.flush(timeout=30)
    log.info("Run complete. Published %s/%s records.", published, len(records))
    return 0


if __name__ == "__main__":
    sys.exit(main())
