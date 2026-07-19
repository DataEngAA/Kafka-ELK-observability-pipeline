# Rules.md — Boundaries for AI-Assisted Development

These rules apply to any AI tool (Claude, Cursor, Copilot, etc.) working on this repo.
Read this before writing or modifying code.

## 1. General Principles
- Prefer boring, well-documented libraries over clever ones. This project is for
  learning and demonstrating understanding — not for showing off unfamiliar tricks.
- Every non-obvious design choice must get a one-line comment or a note in
  `Architecture.md` explaining *why*, not just *what*.
- Do not silently swallow errors. Every `except`/`catch` must either re-raise, log
  with context, or route the failure to a dead-letter/retry path.
- No hardcoded credentials, endpoints, or magic constants — use env vars / ConfigMaps
  / Secrets, with sane local-dev defaults in `.env.example`.

## 2. Libraries — Preferred
- Kafka client: `confluent-kafka-python` (not `kafka-python`, which is less actively
  maintained)
- Avro: `fastavro` for serialization performance
- Schema registry client: Karapace's REST-compatible client or `confluent-kafka`'s
  built-in SchemaRegistryClient
- HTTP: `httpx` (async-capable) over raw `requests` for producers hitting APIs
- Scraping: Playwright only if a source requires JS rendering; otherwise `requests` +
  `BeautifulSoup4` (matches existing scraper conventions)
- K8s manifests: Helm charts preferred over raw YAML once the manifest count exceeds
  ~10 files
- Testing: `pytest`

## 3. Libraries — Avoid
- Avoid ORMs for this project — Elasticsearch and Kafka don't need one, and adding one
  adds unnecessary abstraction
- Avoid framework-heavy web servers (Flask/FastAPI) unless a component genuinely needs
  to expose an HTTP endpoint (e.g. a webhook receiver for alerts) — don't wrap simple
  scripts in a web framework "just in case"
- Avoid `latest` tags in any Dockerfile or Helm chart — pin versions

## 4. Kafka-Specific Rules
- Never use a single shared topic for multiple unrelated sources
- Every producer message must be Avro-serialized and validated against the schema
  registry before publish — no raw JSON on the wire
- Consumers must commit offsets only after a successful, idempotent write — never
  commit-then-process
- Any schema change must be additive/backward-compatible unless explicitly building
  the "schema drift" demo scenario, which must be documented as intentional

## 5. Kubernetes-Specific Rules
- Every Deployment/CronJob must set resource `requests` and `limits` — no unbounded
  pods
- No `latest` image tags in manifests
- Secrets go through Kubernetes Secrets (or an external secrets manager) — never
  committed to the repo, even in "example" form with real-looking values
- KEDA ScaledObjects must scale on a Kafka lag metric — do not fall back to CPU-based
  scaling and call it done

## 6. Error Handling
- Producer failures (source unreachable, parse failure): log with source + timestamp,
  do not crash the CronJob loop for other sources
- Consumer failures: failed messages go to a dead-letter topic, not dropped silently
- Any stage that calls an external API (geocoding, source APIs) must implement retry
  with exponential backoff, capped at a small max (e.g. 3-5 attempts)

## 7. What the AI Should NOT Do
- Do not invent fake data sources or fake metrics to make dashboards look populated —
  use real (if small-scale) data, or clearly-labeled synthetic load-test data
- Do not skip the schema registry "to save time" — this is a core learning objective
  of the project, not optional polish
- Do not bypass Logstash and write straight from consumer to Elasticsearch — that
  defeats the purpose of including Logstash at all
- Do not mark a phase (see Phases.md) complete without the corresponding success
  criteria being demonstrably true (a working demo/test, not just code existing)
- Do not silently change the scope defined in PRD.md — if scope needs to change, say
  so explicitly and update PRD.md

## 8. Commit Hygiene
- Small, incremental commits with descriptive messages — no single "initial commit"
  dumping the whole repo
- Each phase (Phases.md) should map to a identifiable range of commits, ideally a
  feature branch merged via PR (even solo, this shows real workflow discipline)
