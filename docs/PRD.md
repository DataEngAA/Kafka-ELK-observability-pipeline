# PRD.md — Streaming Ingestion & Observability Platform

## 1. Problem Statement
Public sustainability/regulatory data sources (EPD registries, carbon-intensity APIs,
product recall feeds) are unreliable: they go down, change structure, rate-limit, or
silently return stale/malformed data. Most ingestion pipelines fail silently — nobody
notices until a consumer of the data complains. There is no existing lightweight,
open-source reference implementation of a **self-monitoring** ingestion pipeline built
on Kafka + Kubernetes + ELK that a data engineer can point to and say "this is how you
do it properly."

## 2. Goal
Build a pipeline that ingests data from multiple unreliable public sources, moves it
through Kafka reliably, scales itself automatically under load, and gives full
real-time visibility into its own health — so failures are visible within minutes,
not weeks.

## 3. Target "User"
This is a portfolio/reference project. The "user" is:
- **Primary**: Claude/reviewer/interviewer evaluating engineering depth via the repo
  and README.
- **Secondary (design fiction)**: an internal data team that depends on these feeds
  being fresh and needs to know immediately when a source breaks.

## 4. Scope — In
- Multi-source ingestion (minimum 2-3 public sources) via scheduled Kubernetes CronJobs
- Kafka as the central event bus, one topic per source/domain
- Avro schema registry with at least one deliberate, demonstrated schema evolution
- Kafka consumers writing idempotently to Elasticsearch
- Logstash performing real grok parsing + enrichment (not bypassed)
- Kubernetes Deployments for consumers, autoscaled via KEDA on Kafka consumer lag
- Kibana dashboards: source health, pipeline latency, consumer lag over time
- Kibana/ElastAlert alerting: notify when a source goes stale beyond a threshold
- A load-generator script that proves KEDA autoscaling actually triggers
- Docker Compose for local dev; Helm/Kustomize manifests for a real cluster
- CI/CD via GitHub Actions (build/push images, deploy on merge)

## 5. Scope — Out (explicitly not building)
- True exactly-once semantics (idempotent-consumer pattern only — documented as a
  conscious tradeoff, not a gap)
- Full-text search relevance tuning in Elasticsearch (this is a logs/metrics use case,
  not a search product)
- A frontend/UI beyond Kibana dashboards
- Multi-tenancy (single-tenant only — kept for Project 2 or a future iteration)
- Production-grade auth/security hardening beyond basic secrets management

## 6. Success Criteria
- [ ] Pipeline runs end-to-end locally (docker-compose up) and on a real/kind cluster
- [ ] At least one demonstrated schema evolution that doesn't break consumers
- [ ] A recorded before/after showing KEDA scaling consumer pods under simulated burst
- [ ] A Kibana dashboard that would let a stranger tell, within 30 seconds, whether
      each source is healthy right now
- [ ] An alert fires (visibly, e.g. to a webhook/log) when a source is deliberately
      "broken" (simulate a source going stale)
- [ ] README explains the "why" for every major tradeoff (Kafka vs alternatives,
      idempotency vs exactly-once, KEDA vs plain HPA)
- [ ] Git history shows real iteration (no single giant commit)

## 7. Key Risks
- Scope creep — 3+ sources, schema registry, KEDA, Logstash grok, and alerting is a
  lot; build a thin end-to-end slice first (see Phases.md)
- Local resource constraints — Kafka + Elasticsearch + Kubernetes locally is heavy;
  plan for a lightweight local setup (kind + reduced resource requests) and be
  prepared to demo on a small cloud cluster instead
- KEDA demo credibility — must be provably triggered by lag, not CPU, or the
  differentiator claim falls apart in an interview

## 8. Non-Functional Requirements
- Every consumer write to Elasticsearch must be idempotent (deterministic doc ID)
- All services containerized; no "runs on my machine only" steps
- Config via env vars / ConfigMaps — no hardcoded secrets or endpoints
- README must include an architecture diagram (not just prose)
