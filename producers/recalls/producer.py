"""
Phase 1 producer (thin slice): fetches recent product recalls from the
CPSC (US Consumer Product Safety Commission) public API and publishes each
recall as a raw JSON message to Kafka.

No Avro / schema registry yet — that's Phase 2. This script proves the
basic pipe works: source -> Kafka.

Per docs/Rules.md: failures for one record must not crash the whole run,
and every failure should be logged with context.
"""

import json
import logging
import sys
from datetime import datetime, timezone

import httpx
from confluent_kafka import Producer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [producer.recalls] %(message)s",
)
log = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "recalls-raw"
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
    """Wrap a raw CPSC record in our standard event envelope."""
    record_id = record.get("RecallID") or record.get("RecallNumber")
    if not record_id:
        log.warning("Skipping record with no RecallID/RecallNumber: %s", record)
        return None

    return {
        "source": SOURCE_NAME,
        "record_id": str(record_id),
        "event_type": "discovered",
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "payload": record,
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
    producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})

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
                value=json.dumps(event),
                callback=delivery_report,
            )
            published += 1
        except BufferError:
            log.warning("Local producer queue full, flushing and retrying...")
            producer.flush()
            producer.produce(
                topic=KAFKA_TOPIC,
                key=event["record_id"],
                value=json.dumps(event),
                callback=delivery_report,
            )
            published += 1

    producer.flush(timeout=30)
    log.info("Run complete. Published %s/%s records.", published, len(records))
    return 0


if __name__ == "__main__":
    sys.exit(main())
