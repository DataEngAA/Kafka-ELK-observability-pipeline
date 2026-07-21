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

## 2026-07-20 — README added, repo cleanup

**Phase**: Between Phase 5 and Phase 6 — documentation/polish work

**Done**:
- Wrote a full `README.md` for the repo root (previously missing) —
  problem statement, text-based architecture diagram, tech stack, a
  "why these choices" section covering the real design tradeoffs made
  (idempotent consumers over exactly-once, payload-as-JSON-string in Avro,
  field-level hashing for change detection, Kafka/ES kept outside the K8s
  cluster), a section on the real Kafka advertised-listener bug hit and
  fixed during Phase 5, setup instructions, and a phase-status table.
- Removed all em dashes from the README per user preference — replaced
  with commas, colons, or parentheses depending on context.
- Pushed via **GitHub Desktop** from the local Windows/WSL copy, not the
  EC2 terminal — first time pushing from local instead of EC2 for this
  project.

**Broken / blocked**:
- None. Worth noting: since this push came from local rather than EC2,
  local may now be one commit ahead of EC2's repo. Next EC2 session should
  run `git pull` (now that the GitHub remote exists, this is simpler than
  the earlier rsync-based sync method used before GitHub was set up).

**Next**:
- On next EC2 session: `git pull` to sync the README commit down.
- Continue into Phase 6 (KEDA autoscaling) or Phase 7 (dashboards &
  alerting) — user's choice, not yet decided as of this entry.

**Decisions made this session**:
- Confirmed the golden rule going forward: all git add/commit/push
  operations should generally happen from EC2 to avoid history divergence,
  EXCEPT for quick doc-only changes like this README, which are low-risk
  to push from local via GitHub Desktop. Any such local push should be
  followed by a `git pull` on EC2 before the next round of EC2-side commits,
  to keep both in sync.

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

## 2026-07-20/21 (session 3) — Phase 6: KEDA autoscaling

**Phase**: ✅ Phase 6 — KEDA autoscaling, complete

**Done**:
- Installed KEDA 2.20.1 via Helm. Hit an immediate compatibility warning:
  KEDA 2.20 is tested on Kubernetes 1.33+, but the `kind` cluster was
  still on 1.30 (from Phase 0). Decided to upgrade rather than proceed
  with the gap — see decisions below.
- Discovered along the way that `k8s/overlays/prod` and `k8s/overlays/dev`
  are empty — despite the base/overlays folder layout suggesting Kustomize,
  there's no `kustomization.yaml` anywhere in the tree. Deployment has
  actually always been plain `kubectl apply -f` against `k8s/base/`
  directly. Overlays were scaffolded early with intent, never built out.
  Not fixing now — just documenting so it's not mistaken for a bug later.
- Upgraded `kind` from v0.23.0 to v0.29.0 and recreated the cluster on
  node image `kindest/node:v1.33.1`. Deliberately picked v0.29.0 over the
  latest available (v0.32.0, which defaults to Kubernetes 1.36) — v0.29.0
  lands exactly on the 1.33 floor KEDA needs without pulling in unrelated
  breaking changes (kubeadm v1beta4, Envoy replacing HAProxy for LB, etc).
- **Gotcha**: cluster recreation wipes kind's node-local Docker image
  cache. Both consumer Deployments and one CronJob came up in
  `ImagePullBackOff`/`ErrImagePull` immediately after. Images were still
  in the host's Docker cache though, so fixed with `kind load docker-image`
  for all four locally-built images (`camira-writer-consumer`,
  `es-writer-consumer`, `camira-producer`, `recalls-producer`), then
  `kubectl rollout restart` on the two Deployments. Worth remembering for
  any future cluster recreation — this isn't a one-time fluke.
- Tracked down the actual Kafka topic and consumer group names from the
  consumer source (not present in the `pipeline-config` ConfigMap, so
  pulled from `os.environ.get(..., default)` calls directly):
  - `camira-writer-consumer` → topic `camira-fabrics-raw`, group `es-writer-camira`
  - `es-writer-consumer` → topic `recalls-raw`, group `es-writer-recalls`
- Wrote and applied `ScaledObject` manifests for both consumers
  (`k8s/base/keda-scaledobjects/`): `minReplicaCount: 0`,
  `maxReplicaCount: 5`, `pollingInterval: 15`, `cooldownPeriod: 60`,
  `lagThreshold: "10"`, Kafka trigger pointed at the private-IP bootstrap
  address from Phase 5.
- Verified KEDA creates and drives an HPA per ScaledObject automatically
  (`keda-hpa-<name>`) — confirmed this is a real mechanism, not just
  config that looks right, by watching `kubectl get events` show
  `SuccessfulRescale ... external metric s0-kafka-recalls-raw ... above
  target` during the live test below.
- **Real end-to-end test**: manually triggered `recalls-producer`
  (20 records). KEDA detected the resulting lag and scaled
  `es-writer-consumer` from 0 → 2 replicas — the math checked out exactly
  (20 lag ÷ lagThreshold 10 = 2). Both consumers processed the batch,
  lag cleared, and after the 60s cooldown KEDA scaled back to 0.
- **Bug found and fixed**: on scale-down, both consumer pods went
  `Terminating` → `Error` instead of exiting cleanly. Root cause (confirmed
  via `kubectl get events` showing a clean Kubernetes-side
  `Killing`/`SuccessfulDelete` with no Kubernetes-level failure, plus a
  source grep): both consumers only caught `KeyboardInterrupt` (SIGINT),
  never `SIGTERM` — which is what Kubernetes actually sends on pod
  termination. With no handler registered, Python's default SIGTERM
  disposition killed the process before the existing
  `finally: consumer.close()` block could run, surfacing as a non-zero
  exit. Fixed in both `consumers/es_writer/consumer.py` and
  `consumers/camira_writer/consumer.py`: added a `signal.signal(SIGTERM,
  ...)` handler that raises a `GracefulShutdown` exception, caught
  alongside `KeyboardInterrupt`, so the existing cleanup path now runs on
  real pod termination too. Rebuilt both images, reloaded into kind,
  redeployed, and re-ran the exact same test — pods now end in
  `Completed` as expected.
- Committed and pushed from EC2 (commit `a349c3d`): both `ScaledObject`
  manifests plus the SIGTERM fix in both consumers, 4 files.

**Broken / blocked**:
- None outstanding. The SIGTERM bug was found and fixed within this
  session, verified with a second live test before committing.

**Next**:
- Update README's "why these choices" / bug-story section with the
  SIGTERM fix and the deliberate kind v0.29.0 version pick, alongside the
  existing Phase 5 advertised-listener story.
- Continue into Phase 7 (dashboards & alerting) or Phase 8 (CI/CD) —
  user's choice, not yet decided as of this entry.

**Decisions made this session**:
- Upgraded the kind cluster to Kubernetes 1.33 rather than proceeding
  with KEDA's unsupported-version warning on 1.30. Reasoning: the upgrade
  was still cheap at this point (few CronJobs/Deployments, no accumulated
  state), and that gap only grows more expensive to close as Phase 7/8
  add more surface area on top of the cluster.
- Picked `minReplicaCount: 0` (true scale-to-zero) over `1` for both
  ScaledObjects. This is the capability that actually distinguishes KEDA
  from a plain Kubernetes HPA (which can't scale below 1), and it fits
  the pipeline's real traffic shape — CronJob-driven batches, not a
  continuous stream needing an always-warm consumer. Cold-start latency
  on scale-up is a non-issue at this traffic volume.

## 2026-07-21 (session 4) — Phase 7: Dashboards & alerting

**Phase**: ✅ Phase 7 — Dashboards & alerting, complete

**Done**:
- Confirmed ELK stack version (Elasticsearch 8.14.3) and license tier
  (Basic) before planning anything, since license tier directly gates
  which Kibana alerting connectors are usable. On Basic, only `Index`
  and `Server Log` connector types work — Slack, email, webhook,
  PagerDuty all require Gold+. Decided upfront to build alerting
  around the `Index` connector as a deliberate, honest scope choice
  rather than something to apologize for — alerts get written to a
  dedicated `pipeline-alerts` index, which is itself queryable/
  visualizable, not just a workaround.
- Built 3 Kibana data views: `recalls-events`, `camira-fabric-events`,
  and `pipeline-logs-*` (wildcard, deliberately, since logs rotate
  into a new daily index — a non-wildcard pattern would've silently
  stopped matching new data after the first day).
- Built the `Observability Pipeline Overview` dashboard, 3 panels:
  pipeline log volume by level (over time), recalls discovered over
  time, and recalls by manufacturer country. The country panel
  replaced an initial attempt at "recalls by hazard type," which
  turned out to be free-text sentences rather than clean categories
  (61% fell into "Other," each visible slice was a unique sentence)
  — caught this by actually looking at the rendered chart rather than
  assuming the field would behave like a categorical one. Manufacturer
  country turned out to be a genuinely interesting real finding:
  80.95% of recalled products in the current dataset trace back to
  China.
- Hit a real blocker setting up Connectors/Rules: Kibana's Alerting
  framework requires `XPACK_ENCRYPTEDSAVEDOBJECTS_ENCRYPTIONKEY` to
  be configured, which the docker-compose Kibana service never had
  (it was only ever configured for ingestion, not alerting). Generated
  a key with `openssl rand -hex 32`. Initially added it directly to
  `docker-compose.yml` as a hardcoded value — caught this before
  pushing to GitHub via a `git diff` review, and fixed it properly:
  moved the real key into a gitignored `.env` file, changed
  `docker-compose.yml` to reference it as `${KIBANA_ENCRYPTION_KEY}`
  so the requirement is documented in version control without the
  actual secret ever being committed.
- Created the `pipeline-alerts-index` connector (Index type), verified
  it independently using Kibana's built-in connector test feature
  before wiring it into any rule — confirmed a real write reached
  Elasticsearch.
- Built 2 alert rules on `pipeline-logs-*`:
  - **ERROR log detection**: fires when `log_level: ERROR` count is
    above 0 in a 5-minute window.
  - **Pipeline silence detection**: fires when total document count is
    below 1 in a 30-minute window. This window was NOT picked
    arbitrarily — checked the actual CronJob schedules via `kubectl
    get cronjob` first (`recalls-producer` every 15min,
    `camira-producer` every 30min) and set the window comfortably
    above the tightest one (15min) to leave margin for scheduling
    jitter and Logstash ingestion lag, so the alert wouldn't falsely
    fire on normal gaps between scheduled runs.
  - Both rules write formatted alert documents to `pipeline-alerts`
    via the Index connector, using Kibana's built-in `context.*`
    template variables (`context.title`, `context.message`,
    `context.value`, `context.date`) rather than trying to reach into
    raw `context.hits` array indexing, which is less reliable across
    Kibana versions. `context.value` is deliberately stored as a
    quoted string, not a bare number, since Kibana's rule-action JSON
    editor validates the template as literal JSON before substitution
    happens and rejects an unquoted `{{ }}` token.
- **Verified both rules end-to-end, not just configured them**:
  manually indexed a fake `ERROR` log document via `curl`, forced the
  ERROR rule to run immediately ("Run rule"), and confirmed a
  correctly-formatted alert document landed in `pipeline-alerts`
  referencing the real match count. Bonus finding: the silence rule
  had already caught a genuine ~30-minute quiet gap in real
  `pipeline-logs-*` data earlier in the session — confirmed by
  comparing timestamps, this fired before the manual test even
  started, so it's proof of real detection, not just the synthetic
  test working.
- Exported all Kibana saved objects (dashboard, both rules, the
  connector, and the data views) as NDJSON via Stack Management →
  Saved Objects, transferred from local Windows Downloads to EC2 via
  `scp`, and committed to the repo under `kibana/saved-objects/` —
  matching how the rest of this project treats infrastructure as
  code, rather than leaving the Kibana config to only exist as
  in-place UI state with no version history.

**Broken / blocked**:
- None outstanding. The encryption-key secret near-miss was caught
  and corrected before anything was pushed.

**Next**:
- Phase 8 (CI/CD) is the last item remaining from the original phase
  list.

**Decisions made this session**:
- Built the dashboard and alert rules through the Kibana UI rather
  than hand-authoring Saved Objects API JSON, then exported the
  finished result to NDJSON for git tracking. Reasoning: Kibana's
  saved-object JSON is deeply nested internal serialized state that
  nobody hand-writes in real practice; building in the UI is both the
  standard workflow and better resume material ("I built this," not
  "I had it generated"), while the export step still gets the
  reproducibility benefit.
- Scoped alerting delivery around the Basic-license `Index` connector
  deliberately, rather than treating it as a limitation to work
  around — framed as a clean, honest, fully self-contained
  demonstration of the alerting mechanism.

## Phase 8: CI/CD

**Phase**: ✅ Phase 8 — CI/CD, complete

**Done**:
- Installed a GitHub Actions self-hosted runner directly on the EC2
  instance, registered as a systemd service so it persists across
  SSH disconnects and survives reboots without manual restart. Chose
  self-hosted over a GitHub-hosted runner deliberately: the kind
  cluster and its loaded Docker images only exist on this specific
  EC2 box, so a generic cloud runner would have no way to reach
  `kind load` or `kubectl` for this cluster without a much more
  complex bridge (SSH-based remote deploy, exposing kubectl over the
  network, etc).
- Wrote `.github/workflows/deploy.yml`: builds all four project
  images (both consumers, both producers), loads them into the kind
  cluster, reapplies the k8s manifests, and does an explicit rollout
  restart on the two long-running Deployments (CronJobs pick up a
  freshly-loaded image automatically on their next scheduled run
  since they're already `imagePullPolicy: IfNotPresent`, but
  Deployments keep running the old image in memory until explicitly
  restarted).
- Scoped the push trigger to `consumers/**`, `producers/**`, and
  `k8s/**` only, so doc-only commits (README, Memory.md) don't
  trigger a full rebuild — deliberate trade-off, weighed the small
  risk of forgetting to extend the path list if a new component
  folder is added later against the ongoing cost of unnecessary
  rebuilds running on the same box as the live pipeline.
- Also added `workflow_dispatch` alongside the push trigger, to allow
  manually running the workflow on demand — used this for the first
  real test rather than needing a throwaway code change just to
  trigger it.
- Hit a real GitHub restriction on first push: a Personal Access
  Token needs the `workflow` scope specifically to create or update
  files under `.github/workflows/`, separate from general repo write
  access. Generated a new token with both `repo` and `workflow`
  scopes to resolve it.
- **Verified end-to-end via a real manual run**, not just by writing
  the YAML and assuming it'd work: triggered "Run workflow" from
  GitHub's Actions tab, watched it execute live on the self-hosted
  runner, completed in 57s. All four images built, loaded into kind,
  manifests applied, both Deployments successfully rolled out.
  Confirmed afterward that the cluster settled back into a healthy
  state (CronJob pods completed cleanly, consumer Deployments scaled
  back to zero via KEDA once their post-restart batch was processed).

**Broken / blocked**:
- None outstanding.

**Next**:
- All planned phases (0 through 8) are now complete. Remaining work
  is polish: keep the README's "why these choices" section updated
  with anything from this phase worth highlighting (self-hosted
  runner reasoning, the workflow-scope token gotcha), and general
  repo cleanup.

**Decisions made this session**:
- Self-hosted runner over GitHub-hosted, specifically because of the
  kind cluster's locality — this is the standard real-world pattern
  for deploying to infrastructure that isn't reachable from the
  public internet, not a workaround.
- Rebuild all four images on every trigger rather than detecting
  which specific service changed and only rebuilding that one.
  Simpler, and not worth the added complexity yet given how fast
  these builds are — worth revisiting only if build times grow
  significantly later.
