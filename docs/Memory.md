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

## 2026-07-19 — Phase 2 complete: Avro + schema registry

**Phase**: Phase 2 — Add Avro + schema registry ✅ DONE

**Done**:
- `schemas/cpsc_recalls/v1.avsc` — Avro schema for the event envelope. Design
  decision: envelope fields (source, record_id, event_type, scraped_at) are
  strongly typed; the CPSC record itself is kept as a JSON string in
  `payload_json` rather than fully modeled, since CPSC's record shape varies
  between recall types (documented in the schema's own `doc` field and in
  Architecture.md).
- `producer.py` rewritten to use `SerializingProducer` + `AvroSerializer`,
  publishing against the schema registry (Karapace) instead of raw JSON.
  Schema auto-registered on first publish — confirmed via
  `GET /subjects` returning `["recalls-raw-value"]`.
- `consumer.py` rewritten to use `DeserializingConsumer` + `AvroDeserializer`.
  Still writes idempotently to Elasticsearch (unchanged doc-ID logic from
  Phase 1), now expanding `payload_json` back into a nested object before
  indexing so it stays queryable in Kibana.
- **Schema evolution demo**: created `schemas/cpsc_recalls/v2.avsc`, adding
  one new optional field `content_hash` (`["null","string"]`, `default: null`
  — additive, backward-compatible change). Built a standalone
  `producer_v2_demo.py` that publishes using v2. Ran it against the SAME,
  UNMODIFIED consumer.py — confirmed via live logs that all v2 messages
  were processed with zero errors (`200 OK` on every ES write) despite the
  consumer never being told about `content_hash`. Verified in Kibana Dev
  Tools that `content_hash` field exists only on the 20 new v2 documents,
  and `GET /subjects/recalls-raw-value/versions` shows both `[1, 2]`
  coexisting.

**Broken / blocked**:
- None. `confluent-kafka[avro]` needed `librdkafka-dev` installed at the OS
  level before it would build (pip build error: `fatal error:
  librdkafka/rdkafka.h: No such file or directory`) — fixed with
  `sudo apt install -y librdkafka-dev`, documented here so it's not
  rediscovered from scratch next time.

**Next**:
- Move to Phase 3: add 1-2 more producers (different public sources), each
  with its own Kafka topic and Avro schema, proving the multi-topic design
  holds up with concurrent independent pipelines.

**Decisions made this session**:
- Payload stored as JSON string within Avro rather than deeply modeled —
  tradeoff of schema flexibility vs. full type safety, chosen because CPSC's
  record structure isn't stable enough to justify strict Avro modeling.
- Schema evolution demo built as a SEPARATE script (`producer_v2_demo.py`)
  rather than modifying the real producer.py, so the "before/after" comparison
  stays clean and the main pipeline isn't disrupted by demo-only code.

## 2026-07-19 — Phase 3 complete: second source (Camira fabric change-detection)

**Phase**: Phase 3 — Add 1-2 more sources, multi-topic design ✅ DONE (first addition)

**Done**:
- Added a second, genuinely different ingestion pattern: Camira Fabrics
  manufacturer site monitoring via change-detection (as opposed to CPSC's
  simple polling of a structured feed). Ties directly to the user's real
  scraping experience/work — reused the data-testid-based extraction
  approach from their existing CamiraMain.py/CamiraOV.py scrapers.
- New schema: `schemas/camira_fabrics/v1.avsc` — content_hash and
  previous_hash are first-class fields since change-detection is the point
  of this source.
- New producer: `producers/camira_fabrics/producer.py`. Scrapes only the
  fields worth monitoring (specifications, features, colourway count,
  download count) — deliberately NOT the whole page, to avoid false
  positives from ad/session-token noise. Hashes those fields, compares
  against last known hash stored in a dedicated ES index
  (`camira-fabric-state`), and only publishes to Kafka if something
  actually changed. Seeded with 5 real products from the user's own
  CamiraFabric.json for the demo.
- New consumer: `consumers/camira_writer/consumer.py` — same idempotent
  pattern as Phase 1/2's es_writer, writing to `camira-fabric-events`.
  Doc ID includes content_hash (unlike the CPSC consumer) so each real
  change gets its own document — a history of changes per product, not
  just latest-state-overwritten.
- New Kafka topic: `camira-fabrics-raw` (3 partitions, replication 1).
- **Verified live, twice**: first run against the real camirafabrics.com
  site — all 5 products correctly logged as "discovered" (404 on state
  lookup = never seen before), published, state stored. Second run
  immediately after — all 5 correctly logged "No change... skipping
  publish" (200 on state lookup, hash matched) — proving the system stays
  quiet when nothing changed, which is the actual point of a monitoring
  pipeline. Confirmed final state in Kibana: `camira-fabric-events` holds
  5 documents with real scraped specifications, content_hash populated,
  previous_hash null (first-time discovery).

**Broken / blocked**:
- None.

**Next**:
- Phase 3 technically only needs one more source to be "complete" per
  Phases.md, but Camira alone already proves the multi-topic /
  multi-pattern goal strongly. Could add a third source later, or move on
  to Phase 4 (Logstash real grok parsing) — user's call next session.

**Decisions made this session**:
- Kept camira_writer as a separate consumer script rather than
  generalizing es_writer into a shared/parametrized consumer. Rationale:
  the doc-ID strategy differs meaningfully (CPSC overwrites one doc per
  record; Camira keeps one doc per distinct change), so forcing them into
  one generic consumer now would add abstraction before it's earned.
  Worth revisiting as a refactor once a 3rd source exists and the pattern
  is clearer.
- Seeded the Camira producer with a hardcoded list of 5 real products
  rather than reading the full 66-product CamiraFabric.json, to keep demo
  runtime fast. In a real deployment this would come from a feed/DB.

## 2026-07-19 — Phase 4 complete: Logstash real grok parsing + enrichment

**Phase**: Phase 4 — Logstash integration ✅ DONE

**Done**:
- All 4 scripts (producer.recalls, consumer.es_writer, producer.camira,
  consumer.camira_writer) now write to a shared `logs/app.log` file in
  addition to the console, via a second `logging.FileHandler`.
- `logstash/pipeline/pipeline.conf` — real pipeline, not bypassed:
  - `file` input reads `logs/app.log` (mounted into the Logstash container
    via a new docker-compose volume: `./logs:/usr/share/logstash/app_logs:ro`)
  - `grok` filter parses the log line format into `log_timestamp`,
    `log_level`, `component`, `log_message`
  - second `grok` splits `component` (e.g. "producer.recalls") into
    `pipeline_role` + `pipeline_source`
  - `translate` filter enriches each line with `source_owner` — a static
    lookup of which pipeline/team owns that source (e.g. "recalls" →
    "CPSC Recalls Pipeline"). This is the enrichment step called for in
    Phases.md — genuinely joins in data not present in the original log line.
  - `date` filter sets `@timestamp` from the log's own timestamp
  - output goes to a new Elasticsearch index: `pipeline-logs-%{+YYYY.MM.dd}`
- Removed the obsolete `version:` line from docker-compose.yml (was
  producing a warning on every run).
- **Verified live**: ran the CPSC producer, confirmed `logs/app.log` was
  written, restarted Logstash to pick up the new pipeline config and volume
  mount, confirmed `pipeline-logs-2026.07.19` index created automatically
  with 22 documents. Queried it directly and confirmed every enriched field
  present and correct: log_level, component, pipeline_role, pipeline_source,
  source_owner, log_message, @timestamp.

**Broken / blocked**:
- None. Had to `docker compose up -d --force-recreate logstash` to pick up
  the new volume mount + pipeline config, since a plain restart doesn't
  reload docker-compose.yml changes — noting this here so it's not
  re-discovered from scratch next time.

**Next**:
- Phase 5: Kubernetes migration — containerize the producer/consumer
  scripts themselves (they currently run as plain Python processes in a
  venv on the EC2 host), write K8s manifests (CronJobs for producers,
  Deployments for consumers), deploy to a real cluster.
- Also still pending from earlier: push the repo to GitHub (deferred by
  user, not yet done as of this entry).

**Decisions made this session**:
- Used a single shared `logs/app.log` file for all 4 scripts rather than
  one log file per script. Simpler for Logstash to tail one file input,
  and the `component` field already disambiguates which script wrote each
  line — a per-script file would add config complexity without adding
  real value at this scale.
- `sincedb_path => "/dev/null"` in the Logstash file input — means
  Logstash re-reads the whole log file from the start on every container
  restart, rather than remembering its position. Documented in the config
  itself as a deliberate demo-only simplification, not a production
  pattern (a real deployment would use a persistent sincedb).
