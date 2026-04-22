---
name: skillmind-learner
description: Cross-project pattern layer for the Peec AI growth loop. After any Peec skill completes (or after growth-loop-reporter closes a cycle), extract 1–3 concrete patterns from the output and persist them to SkillMind via mcp__skillmind__add_pattern / remember. On the next orchestrator run, recall matching patterns and pass them in as priors — so lessons learned on project A inform decisions on project B. Use when a Peec skill has produced an artifact (brief, zone map, outreach log, decision, learnings.json) worth remembering.
user-invocable: true
---

# SkillMind Learner

## Role
Turn project-local Peec outputs into cross-project patterns. Each run does two things:

1. **Write** — extract 1–3 patterns from a just-produced artifact (decision, brief, zone map, outreach log, learnings.json) and store them in SkillMind with tags so they can be retrieved later.
2. **Read** — on request, recall patterns matching a project / skill / gap type and hand them back as priors for the next orchestrator cycle.

This is the memory layer beneath `growth-loop-reporter`: that skill persists learnings *for the project*, this skill promotes them *across projects*.

## Input

For **write** mode:
- `project_id` — Peec project the artifact came from
- `source_skill` — which skill produced the artifact (`ai-growth-agent`, `content-cluster-builder`, `citation-outreach`, `peec-content-intel`, `growth-loop-reporter`)
- `artifact_path` or `artifact_content` — the file or inline content to extract from
- optional `max_patterns` — default 3

For **read** mode:
- `query` — what the caller wants to recall (e.g. `"editorial outreach DACH high citation rate"`)
- optional `project_id` — narrow to patterns originally written for this project
- optional `source_skill` — narrow to patterns originally written by this skill
- optional `k` — default 5

## Output

Write mode: JSON list of `{pattern_id, title, tags, summary}` for each persisted pattern, plus a one-line confirmation (`"added 3 patterns · skipped 1 dupe"`).

Read mode: ranked list of `{pattern_id, title, summary, provenance: {project_id, source_skill, date}, score}`. Empty list is a valid result — say so plainly.

Neither mode produces dashboards.

## When to use

**Write:**
- Right after `growth-loop-reporter` emits `learnings.json`
- After a `citation-outreach` batch closes (week-end ritual)
- After `content-cluster-builder` ships a zone map (zones become reusable taxonomy patterns)
- After `ai-growth-agent` logs a decision whose 4-week metric came in (attribution is known)
- After `peec-content-intel` ships a brief that later won its prompt (write the *retrospective* pattern, not the brief itself)

**Read:**
- At the top of `ai-growth-agent` Phase 1 (state read) — recall patterns tagged with the current gap type
- At the start of `citation-outreach` — recall domain-class patterns with high historical citation gain
- At the start of `content-cluster-builder` — recall zone-shape patterns that worked in adjacent projects

Do not use when:
- The artifact is <24h old and no outcome is measured yet (you'd persist speculation, not a pattern)
- The artifact is a raw data dump (`list_chats` output) — needs to be interpreted first
- SkillMind MCP is unavailable — fall back to appending a line to `<project>/growth_loop/patterns.md` and flag the skip in the output

---

## Pipeline — write mode

### 1. Read artifact

```
Read(artifact_path)
# or accept inline artifact_content
```

Supported artifact shapes:
- `decisions_log.md` entry (single decision block)
- `learnings.json` (winners / losers / surprises)
- `brief.md` with a *later-known* outcome (prompt visibility moved from X → Y)
- `outreach_log.md` row with `status=citation_live` and a measured lift
- `zones.md` with ≥4 weeks of tag-level visibility data

### 2. Extract candidate patterns

Ask: what would transfer to another project? Good patterns are:
- **Causal** — "<input pattern> → <measurable outcome>", not "<thing happened>"
- **Transferable** — not tied to a single brand / client
- **Falsifiable** — someone else applying this could confirm or refute it

Anti-patterns (reject):
- Project-specific trivia ("antonioblago.de's homepage")
- Restatements of Peec docs ("get_actions has a scope parameter")
- Generic SEO wisdom ("write good content")

Target: 1–3 patterns per artifact. If you can only find 1, persist 1. Zero is a valid result.

### 3. Check for duplicates

```
mcp__skillmind__recall(query=<pattern_title>, k=5)
```

If any hit has ≥0.85 semantic similarity to the new candidate:
- Same claim + stronger evidence → `mcp__skillmind__update_memory` (don't re-add)
- Same claim + weaker evidence → skip
- Contradicting claim → persist anyway, tag `contradicts:<existing_pattern_id>`

### 4. Persist

```
mcp__skillmind__add_pattern(
  title="<≤80 chars, causal phrasing>",
  body="<structured pattern, schema below>",
  tags=["peec", "<source_skill>", "<gap_type>", "<funnel_stage>", "<market>"]
)
```

Required tags every pattern carries:
- `peec` (project family)
- `source:<skill-name>` (which skill observed it)
- `project:<slug>` (anonymized if needed)
- `date:<YYYY-MM-DD>` (observation date)
- ≥1 semantic tag (`gap:taxonomy` / `funnel:decision` / `channel:reddit` / `lever:editorial` / ...)

### 5. Confirm

Return the list of persisted patterns. If a pattern was skipped as a duplicate, say which existing pattern it merged into.

---

## Pipeline — read mode

### 1. Query

```
mcp__skillmind__recall(
  query=<query>,
  k=<k, default 5>,
  filter_tags=[<optional narrowing tags>]
)
```

### 2. Filter by provenance (optional)

Drop hits whose `project:` tag matches `project_id` *if* the caller wants cross-project priors only (supplied via a `exclude_own=true` flag). Default: include own project's patterns.

### 3. Rank

Score = `semantic_similarity × recency_decay × evidence_weight`

- `recency_decay` = `0.5 ^ (months_since / 6)` — a 6-month-old pattern is worth half
- `evidence_weight` = `1.0` for single-project patterns, `1.5` for patterns with ≥2 projects of evidence (consolidated)

### 4. Return

Return top-k as structured list. The caller (usually `ai-growth-agent`) uses them as priors in its Decision Framework.

---

## Pattern schema

```markdown
## <causal title — ≤80 chars>

**Claim:** <one sentence, causal, falsifiable>

**Evidence:**
- <project, date>: <observation with a number>
- <project, date>: <observation with a number>
- ...

**Transfer conditions:**
- Works when: <market / funnel stage / offer type>
- Does NOT transfer when: <named conditions>

**Counter-evidence (if any):**
- <project, date>: <what contradicted it>

**Related patterns:** <pattern_id>, <pattern_id>
```

## Example pattern (concrete)

```markdown
## Editorial citations on DACH micro-publications gain 3× faster than Reddit

**Claim:** For DACH service-business projects, editorial-pitch-wins at t3n / OMR /
fachportal-niveau produce citation lift inside 10–14 days; reddit-thread-answers
typically need 3–6 weeks to surface in LLM training signal — if they surface at all.

**Evidence:**
- project:antonioblago, 2026-04: 2 editorial wins → 5 citations in 10d, 1 subreddit
  answer → 0 citations in 30d
- project:paroc, 2026-03: 1 t3n contribution → 4 citations in 8d

**Transfer conditions:**
- Works when: DACH market, B2B service offer, target domain DR 40–60
- Does NOT transfer when: consumer B2C (reddit is faster there)

**Counter-evidence:** none yet.

**Related patterns:** `pat_b12a` (reddit threads need authoritative first-5-sentences)
```

Tags: `peec`, `source:citation-outreach`, `project:antonioblago`, `project:paroc`,
`date:2026-04-22`, `gap:citation`, `channel:editorial`, `market:dach`, `funnel:decision`.

---

## Quick reference

| Step | Tool |
|---|---|
| Persist a pattern | `mcp__skillmind__add_pattern` |
| Update an existing pattern | `mcp__skillmind__update_memory` |
| Recall patterns by query | `mcp__skillmind__recall` |
| List all peec-tagged patterns | `mcp__skillmind__list_patterns` (filter `tag=peec`) |
| Merge near-duplicates | `mcp__skillmind__consolidate` |
| Export to obsidian for backup | `mcp__skillmind__export_obsidian` |

---

## Handoff points (where other skills call this one)

- `ai-growth-agent` Phase 1 → **read mode** with `query=<current gap type>` to load priors before deciding
- `growth-loop-reporter` Phase 7 → **write mode** for each entry in `learnings.json.winners[]` and `.losers[]` with `source_skill="growth-loop-reporter"`
- `citation-outreach` Phase 7 (post 4-week measurement) → **write mode** for each `status=citation_live` + measured lift row
- `content-cluster-builder` Phase 7 (after zone tags exist 4+ weeks) → **write mode** for zones whose `tag:zone:*` visibility moved >10pp

---

## Done criteria (self-check before returning)

Write mode is complete when:

1. 0–3 patterns persisted (zero is valid — don't force-fill)
2. Every persisted pattern has all required tags (peec, source, project, date, ≥1 semantic)
3. Duplicates are either skipped or consolidated, never silently doubled
4. Evidence references a measured number — no pattern is persisted on vibes

Read mode is complete when:

1. Top-k returned with scores (semantic × recency × evidence)
2. Empty result is announced plainly ("no matching patterns") — do not fabricate
3. Each result carries provenance (project + source_skill + date)

---

## Guardrails (do not do these)

- Do not persist patterns from artifacts without a measured outcome — a brief that hasn't won its prompt yet is speculation, not a pattern
- Do not persist generic SEO advice — only claims grounded in a specific Peec-measured observation
- Do not persist more than 3 patterns per artifact — if a run produces 10 "learnings," most are noise
- Do not silently merge contradicting patterns — contradictions are information; tag them and keep both
- Do not recall without provenance — every returned pattern must say which project + skill + date it came from, or the caller can't judge transfer fit
- Do not run in write mode on <24h-old artifacts — measurement window hasn't closed
- Do not run if SkillMind MCP is unavailable — fall back to appending to `<project>/growth_loop/patterns.md` and flag the skip; never fabricate persistence
