# Architecture.md — Streaming Ingestion & Observability Platform

## 1. High-Level Flow

```
[Source APIs/Sites]
      |
      v
[Producer CronJobs] --publish(Avro)--> [Kafka topics, per source]
      |                                        |
      | (schema check)                         v
      v                                [Consumer Deployments] --idempotent write--> [Elasticsearch]
[Schema Registry]                              ^
                                                | scaled by
                                          [KEDA ScaledObject]
                                          (trigger: consumer lag)

[Raw/app logs] --> [Logstash: grok + enrich] --> [Elasticsearch: logs index]

[Elasticsearch] --> [Kibana: dashboards + alerts]
```

## 2. Components

| Component | Role | Notes |
|---|---|---|
| Producer CronJobs | Poll/scrape sources on schedule | Python, one image per source or one parametrized image |
| Kafka | Event bus | One topic per source domain, e.g. `epd.raw`, `carbon.raw`, `recalls.raw` |
| Schema Registry (Karapace) | Avro schema versioning | BACKWARD compatibility mode |
| Consumers | Read topic, write to ES | Idempotent via deterministic doc ID (hash of source+content) |
| KEDA | Autoscale consumers | Trigger: Kafka consumer group lag, not CPU |
| Logstash | Parse + enrich raw logs | Grok patterns per log source; static lookup enrichment |
| Elasticsearch | Storage for events + logs | Index-per-day pattern for time-series data |
| Kibana | Dashboards + alerts | Source health, lag over time, alerting on staleness |

## 3. Data Model (Kafka event, pre-Avro-serialization example)
```json
{
  "source": "environdec",
  "record_id": "EPD-IES-0030200:001",
  "event_type": "discovered | updated",
  "content_hash": "sha256...",
  "scraped_at": "2026-07-19T10:00:00Z",
  "payload": { "...source-specific fields..." }
}
```
Avro schema lives in `schemas/<source>/v1.avsc`, versioned; breaking changes bump to
`v2.avsc` and consumers declare which version(s) they support.

## 4. Repo / Folder Structure
```
project1-observability-pipeline/
├── producers/
│   ├── environdec/
│   ├── carbon_intensity/
│   └── recalls/
├── schemas/
│   ├── environdec/v1.avsc
│   ├── carbon_intensity/v1.avsc
│   └── recalls/v1.avsc
├── consumers/
│   ├── es_writer/
│   └── common/           # shared idempotency, kafka client, schema registry client
├── logstash/
│   └── pipeline/*.conf
├── k8s/
│   ├── base/              # Kustomize base or Helm chart
│   │   ├── cronjobs/
│   │   ├── deployments/
│   │   ├── keda-scaledobjects/
│   │   └── configmaps-secrets/
│   └── overlays/
│       ├── dev/
│       └── prod/
├── kibana/
│   ├── dashboards/*.ndjson
│   └── alerts/*.json
├── load-test/
│   └── burst_generator.py
├── docker-compose.yml      # local dev: kafka, zookeeper/kraft, schema-registry, es, kibana, logstash
├── .github/workflows/
│   └── ci-cd.yml
├── docs/
│   ├── PRD.md
│   ├── Architecture.md
│   ├── Rules.md
│   ├── Phases.md
│   ├── Design.md
│   └── Memory.md
└── README.md
```

## 5. Tech Stack
- **Language**: Python 3.11+ (producers, consumers, load generator)
- **Messaging**: Apache Kafka (KRaft mode, no Zookeeper needed for new setups)
- **Schema**: Avro + Karapace schema registry
- **Orchestration**: Kubernetes (kind for local, EKS/GKE for real deploy)
- **Autoscaling**: KEDA
- **Packaging**: Helm (preferred) or Kustomize
- **Log pipeline**: Logstash
- **Storage/Search**: Elasticsearch
- **Dashboards**: Kibana (+ ElastAlert2 if Kibana alerting proves limited on free tier)
- **CI/CD**: GitHub Actions → build/push to a container registry (GHCR or ECR) → deploy
- **Local dev**: Docker Compose

## 6. Key Design Decisions & Why
- **One topic per source, not one shared topic**: isolates schema evolution and
  consumer scaling per source; a burst on one source doesn't starve others.
- **Idempotent consumers over exactly-once**: true exactly-once requires transactional
  outbox patterns disproportionate to this project's scale; deterministic doc IDs in
  ES achieve the same practical outcome (safe reprocessing) more simply.
- **KEDA over plain HPA**: CPU is the wrong signal for a consumer whose bottleneck is
  "how far behind Kafka am I," not compute usage.
- **Logstash kept in the loop deliberately**: most projects bypass it and write
  straight to ES; keeping it forces real grok/enrichment experience.

## 7. Open Questions (update as decided)
- Which 2-3 sources to commit to first (pick sources with a stable, scrapable public
  API/feed to avoid fighting anti-bot measures while learning the stack)
- Managed cluster choice for the "real" deployment demo (EKS vs GKE vs a single
  cheap VPS running k3s) — cost vs realism tradeoff
