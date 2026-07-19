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
