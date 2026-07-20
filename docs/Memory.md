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

## 2026-07-20 — Phase 5 complete: Kubernetes migration

**Phase**: Phase 5 — Kubernetes migration ✅ DONE

**Done**:
- Resized EC2 from t3.large (8GB) to t3.xlarge (16GB) before starting —
  running a full kind cluster alongside the existing 5-service docker-compose
  stack needed real headroom. Private IP stayed stable across the resize
  (172.31.43.186), so no ConfigMap changes were needed for that.
- Refactored all 4 scripts (producer.recalls, consumer.es_writer,
  producer.camira, consumer.camira_writer) to read Kafka/Schema
  Registry/Elasticsearch endpoints from environment variables
  (`os.environ.get(..., "localhost:...")` fallback) instead of hardcoded
  localhost URLs — this was a Rules.md requirement from day one that hadn't
  been done yet; Phase 5 was the forcing function.
- Wrote a Dockerfile per script (all install librdkafka-dev, same fix
  needed on the EC2 host directly back in Phase 2).
- Installed kubectl + kind on EC2 (previously only installed locally).
- Created a kind cluster (`observability-pipeline`) on EC2.
- Wrote K8s manifests: a namespace, a ConfigMap pointing pods at the
  docker-compose stack via the EC2 host's private IP (Kafka/ES/Schema
  Registry are treated as external managed infra, not deployed inside the
  cluster — a legitimate, common real-world pattern), 2 CronJobs (recalls
  every 15 min, Camira every 30 min — less frequent since it hits a real
  external site), and 2 Deployments for the long-running consumers.
- Built all 4 images, loaded them into kind via `kind load docker-image`
  (necessary because kind runs its own isolated container runtime — images
  built on the host Docker aren't automatically visible to it).
- **Real bug hit and fixed**: consumers initially failed to connect with
  repeated `Connection refused` on `localhost:9092` — root cause was
  Kafka's `KAFKA_ADVERTISED_LISTENERS` still advertising `localhost:9092`
  for the host listener. Pods could reach the initial bootstrap port fine,
  but Kafka then told them to reconnect to `localhost` for actual
  produce/consume operations — which inside a pod means the pod itself, not
  the EC2 host. Fixed by changing the advertised listener to the EC2
  private IP (`172.31.43.186:9092`). Hit a follow-up typo (dropped the
  port number during a manual edit) that crashed Kafka outright — caught
  via `docker logs kafka` showing an `IllegalArgumentException` on
  startup, fixed with a precise `sed` replacement instead of manual editing.
- **Verified live**: both CronJobs fired on their own schedule
  automatically (not just manually triggered) and completed successfully;
  manually-triggered test jobs also completed; both consumer Deployments
  stayed `1/1 Running` throughout and successfully wrote real data to
  Elasticsearch (confirmed via `200 OK` responses in logs); old ReplicaSets
  correctly scaled to 0 after rollout restarts, demonstrating K8s's
  self-managing behavior.

**Broken / blocked**:
- See the advertised-listener bug above — fully resolved, documented here
  so the reasoning isn't lost. This is a genuinely common real-world Kafka
  gotcha, worth remembering: advertised.listeners must resolve to an
  address reachable by whichever client is connecting, and different
  client types (same-host processes vs. same-docker-network containers vs.
  external K8s pods) may need different listener configs entirely in a
  more complex setup.

**Next**:
- Phase 6: KEDA autoscaling — scale consumer pods based on Kafka consumer
  lag rather than CPU, proven with a load-test burst script.

**Decisions made this session**:
- Kept Kafka/Elasticsearch/Schema Registry/Kibana/Logstash running via
  docker-compose on the EC2 host rather than also moving them into the kind
  cluster. Rationale: this mirrors a common real-world pattern (managed/
  external data infra, separate from the application's own K8s workloads)
  and keeps Phase 5's scope focused on containerizing OUR code, not
  re-platforming infrastructure that already works.
- Resized the EC2 instance proactively before hitting OOM issues, rather
  than waiting for problems — 16GB gives real headroom for the full stack
  (5 docker-compose services + a kind cluster + app pods) running
  simultaneously.

## 2026-07-20 (session 2) — EC2 restart recovery verified

**Phase**: Operational verification, between Phase 5 and Phase 6

**Done**:
- Restarted EC2 after a stop (new public IP each time; private IP stayed
  stable at 172.31.43.186 as expected). Brought docker-compose stack back
  up cleanly (`docker compose up -d`) — all 5 services returned healthy.
- Confirmed the `kind` cluster and all K8s resources survived the EC2
  stop/start intact — no need to recreate the cluster or redeploy manifests.
- Confirmed both CronJobs had kept firing on schedule automatically while
  the instance was stopped and after it restarted (saw completed Jobs from
  scheduled runs, not just manually-triggered ones) — real evidence the
  scheduling is durable, not just a one-time demo behavior.
- Consumer pods initially showed connection failures to Kafka right after
  restart (`Connection refused` on 172.31.43.186:9092) — expected, since
  the pods came up before Kafka had fully finished its own KRaft
  startup/log-loading. Not a config bug this time, just a timing race.
  Fixed by restarting the consumer deployments once Kafka was confirmed
  healthy (`nc -zv` to check the port, then `kubectl rollout restart`).
- Hit one genuine external-source flakiness: a manually-triggered recalls
  producer job failed with "The read operation timed out" against the
  live CPSC API. This is NOT a bug — it's the error handling built in
  since Phase 1 working correctly: the job logged the failure clearly,
  published nothing, and exited cleanly rather than crashing or silently
  losing data. A retry succeeded immediately (20/20 published, all written
  to Elasticsearch).

**Broken / blocked**:
- None outstanding. Everything above was either expected behavior (startup
  race) or handled gracefully by existing error handling (API timeout).

**Next**:
- README.md was added and pushed via GitHub Desktop from local in a
  previous mini-session — need to `git pull` on EC2 to sync it down before
  the next commit (not yet done as of this entry).
- Continue into Phase 6 (KEDA autoscaling) or Phase 7 (dashboards) next.

**Decisions made this session**:
- None new — this was verification/recovery work, not new development.
  Worth keeping as a record though: it's genuine evidence the system
  behaves correctly across real operational events (restarts, timing
  races, transient external failures), which is exactly the kind of
  resilience story worth mentioning in an interview.
