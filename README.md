# Streaming Ingestion & Observability Platform

A self-monitoring data pipeline that ingests from unreliable public sources,
government safety feeds and manufacturer websites, moves the data reliably
through Kafka, and stores it in Elasticsearch, all running on Kubernetes.

## The problem

Public data sources break silently. APIs go down, manufacturer websites
change their HTML structure without notice, and feeds silently return stale
or malformed data. Most ingestion pipelines have no way to notice this:
nobody finds out until a downstream consumer of the data complains, days or
weeks later.

This project builds a pipeline that **catches these failures within minutes**
by combining reliable event streaming (Kafka), governed schema evolution
(a schema registry), real log parsing and enrichment (Logstash), and
container orchestration (Kubernetes), the same building blocks used in
production data platforms, applied to two genuinely different, real-world
ingestion patterns.

## What it actually does

**Source 1: CPSC Product Recalls.** Polls the US Consumer Product Safety
Commission's public API on a schedule and publishes new recalls to Kafka.
A simple, structured-feed ingestion pattern.

**Source 2: Camira Fabrics manufacturer monitoring.** Scrapes a real
manufacturer's product pages and detects *actual changes* via field-level
content hashing, deliberately ignoring page noise (ads, session tokens) so
it only raises an event when something genuinely changed. A harder,
change-detection ingestion pattern, built on top of real scraping experience
rather than a clean API.

Both sources flow through the same architecture: Kafka (with Avro schemas
registered in a schema registry) → a consumer that writes idempotently to
Elasticsearch → Logstash separately parses and enriches the pipeline's own
operational logs, so pipeline health is queryable the same way the data is.

## Architecture

```
 ┌─────────────────┐        ┌─────────────────┐
 │  CPSC public API │        │ Camira Fabrics    │
 │  (structured feed)│        │ (scrape + hash)   │
 └────────┬─────────┘        └────────┬──────────┘
          │  Avro-serialized events            │
          ▼                                     ▼
 ┌──────────────────────────────────────────────────┐
 │                     Kafka                          │
 │        recalls-raw          camira-fabrics-raw     │
 └──────────────────────┬─────────────────────────────┘
                         │  validated against
                         ▼
              ┌────────────────────┐
              │  Schema Registry     │
              │     (Karapace)       │
              └────────────────────┘
                         │
          ┌──────────────┴───────────────┐
          ▼                               ▼
 ┌──────────────────┐          ┌──────────────────────┐
 │  es_writer         │          │  camira_writer         │
 │  consumer           │          │  consumer               │
 │  (idempotent writes)│          │  (idempotent writes)     │
 └─────────┬──────────┘          └───────────┬──────────────┘
           │                                  │
           ▼                                  ▼
 ┌────────────────────────────────────────────────────┐
 │                  Elasticsearch                        │
 │   recalls-events        camira-fabric-events           │
 └────────────────────────────────────────────────────┘
                         ▲
                         │ parsed + enriched logs
              ┌────────────────────┐
              │      Logstash        │
              │  (grok + translate)  │
              └────────────────────┘
                         ▲
              app logs from all 4 producers/consumers
```

Everything above runs on Kubernetes (via `kind`): the two producers as
**CronJobs**, the two consumers as **Deployments**. Kafka, the schema
registry, Elasticsearch, and Kibana run via Docker Compose on the same host,
treated as external managed infrastructure, a common real-world pattern
where application workloads and stateful data infra are deployed separately.

## Tech stack

Kafka (KRaft mode) · Kubernetes (kind) · Elasticsearch · Logstash · Kibana ·
Schema Registry (Karapace, Avro) · Python (confluent-kafka, httpx,
BeautifulSoup4) · Docker & Docker Compose · Git/GitHub

## Why these choices

**Idempotent consumers, not exactly-once.** True exactly-once delivery
requires a transactional outbox pattern disproportionate to this project's
scale. Instead, every write uses a deterministic document ID
(`SHA-256(source + record_id)`), so re-processing a message after a consumer
restart safely overwrites rather than duplicates.

**Payload kept as a JSON string inside Avro, not fully modeled.** The CPSC
API's record shape varies between recall types. Rather than tightly
coupling the Avro schema to an unstable external structure, the envelope
(source, record ID, timestamps) is strongly typed, and the raw record rides
along as a JSON-encoded string field.

**Change detection via field-level hashing, not whole-page hashing.**
Manufacturer pages carry noise (ads, session tokens, "related products"
ordering) that changes on every page load. Hashing the whole page would
produce constant false "updated" events. Hashing only the fields that
actually matter (specifications, features, colourway count) means the
pipeline stays quiet unless something real changed.

**Kafka/Elasticsearch run outside the Kubernetes cluster.** This project
containerizes and orchestrates the *application* code, the part that
changes and needs scaling, while treating the data infrastructure as
already-managed, matching how many real platforms are actually deployed.

## A real bug, and what it taught

Early in the Kubernetes migration, consumer pods failed to connect to Kafka
with `Connection refused` on `localhost:9092`, even though the same code
worked fine as a plain process on the host. The cause: Kafka's
`advertised.listeners` config was telling every client to reconnect to
`localhost` for actual read/write operations, which inside a pod resolves to
the pod itself, not the host. Fixed by advertising the host's real address
instead. A genuine, common Kafka gotcha: advertised listeners have to
resolve to an address reachable by *whichever* client is connecting, and
that can differ between same-host processes, same-Docker-network
containers, and external Kubernetes pods.

## Project structure

```
producers/          # Kafka producers (one folder per source)
consumers/           # Kafka consumers (one folder per source)
schemas/             # Avro schemas, versioned per source
logstash/pipeline/   # Logstash grok/enrichment config
k8s/base/            # Kubernetes manifests (namespace, configmap, cronjobs, deployments)
docs/                # Planning docs: PRD, Architecture, Rules, Phases, Memory
docker-compose.yml   # Kafka, Schema Registry, Elasticsearch, Kibana, Logstash
```

## Running it locally

Requires Docker, `kubectl`, and `kind`.

```bash
# 1. Bring up Kafka, Schema Registry, Elasticsearch, Kibana, Logstash
docker compose up -d

# 2. Create a local Kubernetes cluster
kind create cluster --name observability-pipeline

# 3. Build and load the application images
docker build -f producers/recalls/Dockerfile -t recalls-producer:latest .
docker build -f consumers/es_writer/Dockerfile -t es-writer-consumer:latest .
docker build -f producers/camira_fabrics/Dockerfile -t camira-producer:latest .
docker build -f consumers/camira_writer/Dockerfile -t camira-writer-consumer:latest .

kind load docker-image recalls-producer:latest --name observability-pipeline
kind load docker-image es-writer-consumer:latest --name observability-pipeline
kind load docker-image camira-producer:latest --name observability-pipeline
kind load docker-image camira-writer-consumer:latest --name observability-pipeline

# 4. Deploy
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/configmaps-secrets/pipeline-config.yaml
kubectl apply -f k8s/base/cronjobs/
kubectl apply -f k8s/base/deployments/
```

> **Note:** `k8s/base/configmaps-secrets/pipeline-config.yaml` currently
> points at a specific host IP for Kafka/Elasticsearch, since this project
> was built and demoed on a single EC2 instance running both the
> Docker Compose stack and the `kind` cluster. Update that IP for your own
> environment.

## Status

Actively in progress. See [`docs/Phases.md`](docs/Phases.md) for the full
build roadmap and [`docs/Memory.md`](docs/Memory.md) for a session-by-session
log of what's been built, tested, and decided.

| Phase | Status |
|---|---|
| 0 - Infrastructure | ✅ |
| 1 - End-to-end slice | ✅ |
| 2 - Avro + schema registry | ✅ |
| 3 - Second source (multi-topic) | ✅ |
| 4 - Logstash parsing + enrichment | ✅ |
| 5 - Kubernetes migration | ✅ |
| 6 - KEDA autoscaling | ⏭️ |
| 7 - Dashboards & alerting | Not started |
| 8 - CI/CD | Not started |
| 9 - Polish & documentation | Not started |
