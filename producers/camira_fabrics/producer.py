"""
Phase 3 producer: Camira fabric change-detection.

Unlike the CPSC source (Phase 1/2), Camira doesn't tell us when something
changes — we have to detect it ourselves. Approach:

  1. Scrape each fabric's detail page (reusing the data-testid based
     extraction proven in the user's existing CamiraMain.py scraper).
  2. Pull out only the fields worth monitoring: specifications, features,
     colourway count, and download count. We deliberately do NOT hash the
     whole page — manufacturer pages carry noise (ads, session tokens,
     "related products" ordering) that changes on every load and would
     cause false "updated" events if hashed wholesale.
  3. Hash those monitored fields (SHA-256) and compare against the last
     known hash for this product, stored in a dedicated Elasticsearch
     index (camira-fabric-state).
  4. Only publish to Kafka if the hash is new (first time = "discovered")
     or different from what we had on file ("updated"). No change = no
     event published — keeps the pipeline quiet unless something real
     happened, which is the whole point of this source.

See schemas/camira_fabrics/v1.avsc and docs/Architecture.md.
"""

import hashlib
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [producer.camira] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/app.log")],
)
log = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "camira-fabrics-raw")
SCHEMA_REGISTRY_URL = os.environ.get("SCHEMA_REGISTRY_URL", "http://localhost:8081")
SCHEMA_PATH = os.environ.get("SCHEMA_PATH", "schemas/camira_fabrics/v1.avsc")

ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
STATE_INDEX = os.environ.get("STATE_INDEX", "camira-fabric-state")

SOURCE_NAME = "camira_fabrics"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}

# Small seed list for the demo — a subset of real products from the user's
# own CamiraFabric.json (66 products total there; kept small here so the
# demo runs quickly). In a real deployment this would be read from a
# feed/database rather than hardcoded.
SEED_PRODUCTS = [
    {"Product ID": "CAM001", "Product Name": "247 Plus", "Product URL": "https://www.camirafabrics.com/en-uk/contract/fabrics/247-plus"},
    {"Product ID": "CAM002", "Product Name": "247 Flax", "Product URL": "https://www.camirafabrics.com/en-uk/contract/fabrics/247-flax"},
    {"Product ID": "CAM003", "Product Name": "Advantage", "Product URL": "https://www.camirafabrics.com/en-uk/contract/fabrics/advantage"},
    {"Product ID": "CAM005", "Product Name": "Aquarius", "Product URL": "https://www.camirafabrics.com/en-uk/contract/fabrics/aquarius"},
    {"Product ID": "CAM006", "Product Name": "Aspect", "Product URL": "https://www.camirafabrics.com/en-uk/contract/fabrics/aspect"},
]


def scrape_monitored_fields(session: httpx.Client, url: str) -> dict | None:
    """Fetch a fabric's detail page and extract only the fields we monitor
    for change (specifications, features, colourway count, download count).
    Reuses the data-testid selector approach from the existing scraper."""
    try:
        resp = session.get(url, timeout=30.0)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        log.error("Failed to fetch %s: %s", url, exc)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Specifications
    specifications = {}
    for spec_div in soup.find_all(attrs={"data-testid": "fabric-specification-list"}):
        for row in spec_div.find_all("div", class_=re.compile(r"grid.*gap|gap.*grid")):
            children = row.find_all("div", recursive=False)
            if len(children) >= 2:
                label = children[0].get_text(strip=True)
                value = children[1].get_text(strip=True)
                if label and value:
                    specifications[label] = value

    # Features
    features = []
    features_tag = soup.find(attrs={"data-testid": "fabric-features"})
    if features_tag:
        items = features_tag.find_all(["div", "span", "p"], recursive=False)
        src = items if items else features_tag.get_text(separator="\n", strip=True).splitlines()
        for item in src:
            text = item.get_text(strip=True) if hasattr(item, "get_text") else item.strip()
            if text:
                features.append(text)

    # Colourway count
    header = soup.find(attrs={"data-testid": "fabric-colourways-header"})
    total_match = re.match(r"(\d+)", header.get_text(strip=True)) if header else None
    colourways_total = int(total_match.group(1)) if total_match else 0

    # Download count (just the count, not every URL — URLs can be
    # regenerated/re-signed without the actual document changing)
    downloads_count = 0
    dl_section = soup.find(attrs={"data-testid": "fabric-downloads"})
    if dl_section:
        for group in dl_section.find_all("div", class_=lambda c: c and "flex-col" in c and "gap-y-4" in c):
            downloads_count += len(group.find_all("div", class_=lambda c: c and "justify-between" in c))

    return {
        "specifications": specifications,
        "features": sorted(features),  # sort so ordering changes alone don't trigger a false "updated"
        "colourways_total": colourways_total,
        "downloads_count": downloads_count,
    }


def compute_hash(fields: dict) -> str:
    normalized = json.dumps(fields, sort_keys=True)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def get_last_known_hash(es_client: httpx.Client, record_id: str) -> str | None:
    doc_id = hashlib.sha256(f"{SOURCE_NAME}:{record_id}".encode("utf-8")).hexdigest()
    try:
        resp = es_client.get(f"{ELASTICSEARCH_URL}/{STATE_INDEX}/_doc/{doc_id}", timeout=10.0)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()["_source"].get("content_hash")
    except httpx.HTTPError as exc:
        log.warning("Could not fetch prior state for %s: %s — treating as unseen.", record_id, exc)
        return None


def store_current_hash(es_client: httpx.Client, record_id: str, content_hash: str) -> None:
    doc_id = hashlib.sha256(f"{SOURCE_NAME}:{record_id}".encode("utf-8")).hexdigest()
    body = {
        "record_id": record_id,
        "content_hash": content_hash,
        "last_checked": datetime.now(timezone.utc).isoformat(),
    }
    try:
        resp = es_client.put(f"{ELASTICSEARCH_URL}/{STATE_INDEX}/_doc/{doc_id}", json=body, timeout=10.0)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        log.error("Failed to store state for %s: %s", record_id, exc)


def delivery_report(err, msg):
    if err is not None:
        log.error("Delivery failed for record %s: %s", msg.key(), err)
    else:
        log.info("Delivered to %s [partition %s] offset %s", msg.topic(), msg.partition(), msg.offset())


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

    scrape_session = httpx.Client(headers=HEADERS)
    es_client = httpx.Client()

    published = 0
    unchanged = 0

    for product in SEED_PRODUCTS:
        record_id = product["Product ID"]
        url = product["Product URL"]
        log.info("Checking %s — %s", record_id, product["Product Name"])

        fields = scrape_monitored_fields(scrape_session, url)
        if fields is None:
            continue

        current_hash = compute_hash(fields)
        previous_hash = get_last_known_hash(es_client, record_id)

        if previous_hash == current_hash:
            log.info("No change for %s (hash unchanged) — skipping publish.", record_id)
            unchanged += 1
            continue

        event_type = "discovered" if previous_hash is None else "updated"
        event = {
            "source": SOURCE_NAME,
            "record_id": record_id,
            "event_type": event_type,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "content_hash": current_hash,
            "previous_hash": previous_hash,
            "fields_json": json.dumps(fields),
        }

        try:
            producer.produce(topic=KAFKA_TOPIC, key=record_id, value=event, on_delivery=delivery_report)
            published += 1
        except Exception as exc:
            log.error("Failed to produce event for %s: %s", record_id, exc)
            continue

        store_current_hash(es_client, record_id, current_hash)
        log.info("%s: %s (hash %s)", record_id, event_type, current_hash[:12])

    producer.flush(timeout=30)
    log.info(
        "Run complete. %s/%s products had changes and were published, %s unchanged.",
        published, len(SEED_PRODUCTS), unchanged,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
