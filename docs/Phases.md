# Phases.md — Build Roadmap

Build in this order. Each phase should end in something demonstrably working before
moving to the next — resist the urge to build breadth-first across all phases at once.

## Phase 0 — Local scaffolding
- [ ] Repo structure created (see Architecture.md)
- [ ] `docker-compose.yml` with Kafka (KRaft mode), Schema Registry (Karapace),
      Elasticsearch, Kibana, Logstash — all up and reachable locally
- [ ] `.env.example` with all required config documented
**Done when**: `docker-compose up` gives you a fully running local stack with no
manual post-setup steps.

## Phase 1 — Thin end-to-end slice (ONE source only)
- [ ] One producer (pick the simplest, most stable public source) publishing raw JSON
      to Kafka — no Avro yet, just prove the pipe works
- [ ] One consumer reading from Kafka, writing to Elasticsearch (idempotent doc ID
      from the start — don't retrofit this later)
- [ ] Manually trigger the producer, confirm data appears in Elasticsearch via a
      simple Kibana query
**Done when**: you can run producer → see message in Kafka (via console consumer) →
see document in Elasticsearch, for one source, end to end.

## Phase 2 — Add Avro + schema registry
- [ ] Define `v1.avsc` for the Phase 1 source
- [ ] Producer serializes with Avro, registers/validates against schema registry
- [ ] Consumer deserializes via schema registry client
- [ ] Deliberately evolve the schema (add an optional field) → confirm backward
      compatibility holds and consumer doesn't break
**Done when**: schema evolution demo works and is documented with a before/after.

## Phase 3 — Add remaining sources + multi-topic design
- [ ] Add 1-2 more producers, each with its own topic and schema
- [ ] Confirm consumers correctly route/process per-topic without cross-contamination
**Done when**: 2-3 independent source pipelines run concurrently without interference.

## Phase 4 — Logstash integration
- [ ] Route producer/consumer logs (not the data events — the operational logs)
      through Logstash
- [ ] Write grok patterns to extract structured fields (source, status, duration,
      error type) from raw log lines
- [ ] Add at least one enrichment step (e.g. join with a static manufacturer/source
      metadata lookup)
- [ ] Confirm parsed logs land in a separate Elasticsearch index from the data events
**Done when**: Kibana can filter logs by source/status/duration, not just view raw text.

## Phase 5 — Kubernetes migration
- [ ] Containerize all producers/consumers (Dockerfiles, pinned versions)
- [ ] Write K8s manifests: CronJobs for producers, Deployments for consumers
- [ ] Deploy to a local kind cluster, confirm parity with docker-compose behavior
**Done when**: the full pipeline runs on kind with no docker-compose dependency.

## Phase 6 — KEDA autoscaling
- [ ] Install KEDA on the cluster
- [ ] Define a ScaledObject on the consumer Deployment, trigger = Kafka consumer lag
- [ ] Build `load-test/burst_generator.py` to flood a topic
- [ ] Run the burst, record pod count before/during/after (screenshot or `kubectl get
      pods -w` recording)
**Done when**: you have concrete evidence (logs/recording) that pod count rose with
lag and fell back down after — this is the differentiator, don't skip verifying it.

## Phase 7 — Dashboards & alerting
- [ ] Build Kibana dashboards: source health, lag over time, pipeline latency
- [ ] Configure an alert (Kibana alerting or ElastAlert2) for source staleness
- [ ] Deliberately "break" a source (stop its CronJob) and confirm the alert fires
**Done when**: a stranger looking at the dashboard can tell system health in under
30 seconds, and the alert demonstrably fires on a simulated failure.

## Phase 8 — CI/CD
- [ ] GitHub Actions: lint/test on PR, build+push images on merge to main
- [ ] (Stretch) auto-deploy to a real small cloud cluster on merge
**Done when**: a merged PR results in updated images without manual docker build steps.

## Phase 9 — Polish & documentation
- [ ] Architecture diagram in README (image, not just ASCII)
- [ ] "Why" section covering the key tradeoffs (see Architecture.md §6)
- [ ] Clean commit history review (squash any noisy WIP commits if needed)
- [ ] Record a short demo video/GIF of the KEDA scaling event and dashboard
**Done when**: someone with zero context can read the README and understand what this
proves about your skills within 2 minutes.

## Explicitly deferred (not phases — future work if desired)
- True exactly-once semantics / transactional outbox
- Multi-tenancy
- Production auth/security hardening
