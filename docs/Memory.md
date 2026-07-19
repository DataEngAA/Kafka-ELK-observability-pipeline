# Memory.md — Progress Log (Template)

> **Don't fill this in until you start coding.** This file is the AI's "working
> memory" across sessions/chats — instead of re-reading the whole codebase or
> guessing what's done, you (or the AI) update this file after each work session so
> the next session starts with full context in a few hundred tokens instead of a full
> repo scan.

## How to use this file
1. At the **end of every coding session**, add a dated entry below summarizing what
   was done, what's still broken, and what's next.
2. At the **start of a new chat/session**, paste this file's contents (or the last
   2-3 entries) to the AI before asking it to continue work — this replaces "please
   re-read the whole repo."
3. Keep entries short and factual. This is a log, not a journal — bullet points, not
   prose.
4. When a phase in `Phases.md` is completed, note it here with the date and a link to
   the relevant commit/PR if applicable.

## Format for each entry
```
## YYYY-MM-DD — <short session title>
**Phase**: <current Phases.md phase number/name>
**Done**:
- ...
**Broken / blocked**:
- ...
**Next**:
- ...
**Decisions made this session** (if any — also mirror into Architecture.md if
significant):
- ...
```

---

## Example entry (delete once real entries start)
```
## 2026-07-22 — Phase 1 thin slice
**Phase**: Phase 1 — thin end-to-end slice
**Done**:
- docker-compose stack up and stable (kafka, schema-registry, es, kibana, logstash)
- environdec producer publishing raw JSON to `environdec-raw` topic (no Avro yet)
- es_writer consumer reading topic, writing to ES with deterministic doc ID
  (sha256 of record_id + content)
- Verified end-to-end manually: triggered producer, confirmed doc in ES via Kibana
  Dev Tools query
**Broken / blocked**:
- Consumer occasionally double-processes on restart — doc ID dedup handled it
  correctly (no duplicates in ES), but want to add a test for this explicitly
**Next**:
- Move to Phase 2: define v1.avsc for environdec, wire up schema registry
**Decisions made this session**:
- Chose Environdec as first source over carbon-intensity API — simpler auth,
  more stable response format, better for de-risking Phase 1
```

---

## Real entries start here
<!-- Add new entries above this line, most recent at top or bottom — pick one and
     stay consistent -->
## 2026-07-19 — Phase 1 complete: thin end-to-end slice

**Phase**: Phase 1 — thin end-to-end slice ✅ DONE

**Done**:
- EC2 instance provisioned (t3.large, Ubuntu 26.04, ap-south-1) — see docs/Architecture.md
  for why we moved off local (8GB RAM insufficient for the full stack)
- Docker Compose stack running on EC2: Kafka (KRaft mode), Schema Registry (Karapace),
  Elasticsearch, Kibana, Logstash — all healthy
- Kafka topic `recalls-raw` created (3 partitions, replication factor 1)
- `producers/recalls/producer.py` — fetches recent recalls from CPSC public API
  (no auth needed), publishes raw JSON to Kafka. No Avro yet (that's Phase 2).
- `consumers/es_writer/consumer.py` — reads from `recalls-raw`, writes idempotently
  to Elasticsearch index `recalls-events` using SHA-256(source+record_id) as doc ID.
  Offsets commit only after a successful ES write.
- Verified end-to-end: ran producer (published 20/20 records) → ran consumer
  (wrote 20/20 to ES, all `201 Created`) → queried via Kibana Dev Tools
  (`GET recalls-events/_search`) → confirmed `"total": {"value": 20}` with real
  recall data correctly structured under `payload`.
- Kibana reachable locally via SSH tunnel (`-L 5601:localhost:5601`).
- .gitignore added (venv/, *.pem, __pycache__/, etc.) before first real commit —
  avoided committing the virtual environment.

**Broken / blocked**:
- None currently. Docker Compose showed `docker-compose.yml: the attribute 'version'
  is obsolete` warning — cosmetic only, not fixed yet (low priority cleanup).

**Next**:
- Move to Phase 2: define `schemas/cpsc_recalls/v1.avsc`, wire producer/consumer to
  serialize/deserialize via the schema registry (Karapace) instead of raw JSON.
- Demonstrate one backward-compatible schema evolution (add an optional field) and
  confirm the consumer doesn't break.

**Decisions made this session**:
- Chose CPSC (US Consumer Product Safety Commission) recalls as the first data
  source — public, no API key required, stable JSON shape, fits the project's
  regulatory-data theme.
- Fixed docker-compose.yml: correct Karapace image is `ghcr.io/aiven/karapace:latest`
  (not `ghcr.io/aiven-open/karapace:4.3.0`, which doesn't exist), and the correct
  startup command is `./start.sh registry`, not the Confluent-style command
  originally drafted.
- Deliberately did NOT install/use Claude Code for this project — sticking to
  manual, hands-on step-by-step development per user preference.
## 2026-07-19 — Phase 1 complete: thin end-to-end slice

**Phase**: Phase 1 — thin end-to-end slice ✅ DONE

**Done**:
- EC2 instance provisioned (t3.large, Ubuntu 26.04, ap-south-1) — see docs/Architecture.md
  for why we moved off local (8GB RAM insufficient for the full stack)
- Docker Compose stack running on EC2: Kafka (KRaft mode), Schema Registry (Karapace),
  Elasticsearch, Kibana, Logstash — all healthy
- Kafka topic `recalls-raw` created (3 partitions, replication factor 1)
- `producers/recalls/producer.py` — fetches recent recalls from CPSC public API
  (no auth needed), publishes raw JSON to Kafka. No Avro yet (that's Phase 2).
- `consumers/es_writer/consumer.py` — reads from `recalls-raw`, writes idempotently
  to Elasticsearch index `recalls-events` using SHA-256(source+record_id) as doc ID.
  Offsets commit only after a successful ES write.
- Verified end-to-end: ran producer (published 20/20 records) → ran consumer
  (wrote 20/20 to ES, all `201 Created`) → queried via Kibana Dev Tools
  (`GET recalls-events/_search`) → confirmed `"total": {"value": 20}` with real
  recall data correctly structured under `payload`.
- Kibana reachable locally via SSH tunnel (`-L 5601:localhost:5601`).
- .gitignore added (venv/, *.pem, __pycache__/, etc.) before first real commit —
  avoided committing the virtual environment.

**Broken / blocked**:
- None currently. Docker Compose showed `docker-compose.yml: the attribute 'version'
  is obsolete` warning — cosmetic only, not fixed yet (low priority cleanup).

**Next**:
- Move to Phase 2: define `schemas/cpsc_recalls/v1.avsc`, wire producer/consumer to
  serialize/deserialize via the schema registry (Karapace) instead of raw JSON.
- Demonstrate one backward-compatible schema evolution (add an optional field) and
  confirm the consumer doesn't break.

**Decisions made this session**:
- Chose CPSC (US Consumer Product Safety Commission) recalls as the first data
  source — public, no API key required, stable JSON shape, fits the project's
  regulatory-data theme.
- Fixed docker-compose.yml: correct Karapace image is `ghcr.io/aiven/karapace:latest`
  (not `ghcr.io/aiven-open/karapace:4.3.0`, which doesn't exist), and the correct
  startup command is `./start.sh registry`, not the Confluent-style command
  originally drafted.
- Deliberately did NOT install/use Claude Code for this project — sticking to
  manual, hands-on step-by-step development per user preference.
