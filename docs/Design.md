# Design.md — Visual & Presentation Conventions

This project has no traditional app UI — the "visual surface" is Kibana dashboards,
the README, and the architecture diagram. Treat these with the same care as a UI,
since they're what a reviewer actually sees.

## 1. Kibana Dashboards

**Layout convention** (top to bottom, left to right):
1. Top row — system-wide status: a single at-a-glance panel per source (green/amber/
   red) showing "last successful update" — this should be the first thing anyone sees
2. Second row — consumer lag over time (line chart, one series per topic)
3. Third row — pipeline latency (scrape → Kafka → ES elapsed time), as a histogram or
   percentile chart (p50/p95/p99, not just average — averages hide problems)
4. Bottom row — error/log volume by source, over time

**Color convention**:
- Green: healthy / within SLA
- Amber: degraded (e.g. stale by 1-2x the expected interval)
- Red: failed / stale beyond threshold
- Keep this consistent across every panel — a source should never be "green" on one
  panel and "red" on another for the same time window

**Naming convention**:
- Dashboard titles: `[Pipeline] <Purpose>` e.g. `[Ingestion] Source Health Overview`
- Index patterns: `<source>-events-*` and `<source>-logs-*` (day-based, e.g.
  `environdec-events-2026.07.19`)

## 2. Architecture Diagram (for README)
- Use a simple left-to-right or top-to-bottom flow diagram (excalidraw, draw.io, or
  Mermaid rendered to an image) — not a photo of a whiteboard
- Color-code by layer: sources (grey), Kafka/messaging (orange, matching Kafka's own
  brand color for instant recognizability), Kubernetes (blue), ELK (yellow/green,
  matching Elastic's brand), storage (neutral)
- Label every arrow with what's flowing (not just "data") — e.g. "Avro event" not
  just an unlabeled line
- Keep it to one diagram that shows the whole system, plus optional zoomed-in
  diagrams per phase if needed (e.g. a separate KEDA scaling diagram)

## 3. README Structure & Tone
- Lead with the problem statement in plain language (see PRD §1) — not "this repo
  contains a Kafka pipeline," but "public data sources break silently; this system
  catches it in minutes."
- Architecture diagram near the top, not buried
- A "Why these choices" section — this is what separates a portfolio project from a
  tutorial clone; be specific (see Architecture.md §6)
- Setup instructions that actually work if followed literally (test them yourself
  after writing)
- A results/demo section: screenshots of the dashboard, and ideally a short GIF/video
  of the KEDA scaling event
- Keep tone factual and specific — avoid resume-speak ("leveraged cutting-edge
  technologies to architect a robust solution"); say what it does and why

## 4. Code Style (applies across all languages/configs in repo)
- Python: `black` formatting, type hints on function signatures, docstrings on
  non-trivial functions
- YAML (K8s manifests): 2-space indent, consistent key ordering (apiVersion, kind,
  metadata, spec)
- Consistent naming: `snake_case` for Python, `kebab-case` for K8s resource names and
  Kafka topics (e.g. `epd-raw`, not `epd_raw` or `EpdRaw`)

## 5. Non-Goals
- No custom frontend/web UI is planned for this project — Kibana is the interface.
  If a future iteration adds a custom UI, this section should be updated first.
