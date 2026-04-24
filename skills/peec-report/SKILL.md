---
name: peec-report
description: Weekly / monthly closed-loop reporter for Peec AI visibility growth. Measures what moved (visibility per prompt, cluster, zone) against what was invested (content published, pitches sent, forum answers), detects winning patterns, and outputs a ranked next-actions list — not a dashboard. Closes the feedback loop for the growth agent. Use weekly for active projects or monthly for maintenance-mode.
user-invocable: true
---

# Growth Loop Reporter

## Role
Close the loop. Three questions per cycle, answered in ≤400 words:

1. **What moved?** — visibility trend per prompt, cluster, zone
2. **Why?** — which specific investment caused which lift
3. **What next?** — 3 prioritized actions, at least 1 stop-doing

Output is a short narrative + actions, not a dashboard. Fifteen charts don't get read. 400 words do.

## Input
- `project_id` — Peec project
- `reporting_window` — `weekly` | `monthly` | `quarterly`
- optional `baseline_date` — default 28 / 90 / 180 days back
- optional `include_clusters` — auto-detected via `zone:*` tags if `peec-cluster` has run

## Output
- One narrative at `<project>/growth_loop/YYYY-MM-DD_report.md` (schema below)
- One `learnings.json` with winners / losers / surprises / next_actions / stop_doing — consumed by the next `peec-cluster` and `peec-outreach` runs as priors

## When to use
- Weekly for active projects with running content + outreach
- Monthly for retainer projects in maintenance
- Quarterly as strategy review — feeds the next `peec-cluster` run
- After a launch, publication, or new zone going live

Do not use when:
- Project has <4 weeks of history (too little signal)
- No content or outreach actions in the window (nothing to learn)

---

## Pipeline

### 0. Pre-flight — setup state required

Per [`_shared/SETUP_STATE.md`](../_shared/SETUP_STATE.md), this skill refuses to run without a completed setup:

```
Read <project>/growth_loop/setup_state.json
If missing OR completed_at missing OR phases_completed lacks
   {competitors, prompts, topics, tags}:
     STOP. Output:
       "No Peec setup state found at <project>/growth_loop/setup_state.json.
        Run /peec-setup first."
If completed_at older than 90 days: WARN once, continue.
Use peec_project_id from state — don't re-resolve via list_projects.
```

### 1. Pull time-series of core metrics

```
# Overall brand visibility trend
mcp__peec-ai__get_brand_report(
  project_id, start_date=baseline, end_date=now,
  dimensions=["date"],
  filters=[{field: "brand_id", operator: "in", values: [own_brand_id]}]
)

# Per prompt (top-N by weight)
mcp__peec-ai__get_brand_report(
  project_id, start_date=baseline, end_date=now,
  dimensions=["prompt_id", "date"],
  filters=[{field: "brand_id", operator: "in", values: [own_brand_id]}]
)

# Per zone (if zone:* tags exist)
for each zone_tag:
  mcp__peec-ai__get_brand_report(
    project_id, start_date=baseline, end_date=now,
    dimensions=["tag_id", "date"],
    filters=[{field: "tag_id", values: [zone_tag_id]}]
  )
```

Per bucket (prompt or zone) compute:
- `visibility_t0` (start of window)
- `visibility_t1` (end of window)
- `delta` = t1 − t0
- `trend` = linear-regression slope across the window

### 2. Assemble investment log

```
# New content
git log --since=<baseline> --author=<user> -- "Content Automation/blog/"
# or: filesystem scan for blog/YYYY-MM-DD_*/

# Outreach
Read: <project>/outreach/*_outreach_log.md
# all pitches with status != 'queued' in the window

# Taxonomy changes in Peec
mcp__peec-ai__list_prompts + list_brands + list_tags
# diff against a snapshot from the start of the window (if one exists)
```

Produce: one list of investments with `date | type (content|outreach|taxonomy) | target (prompt_id or url) | description`.

### 3. Match investment → lift

- **Content investment** → prompts whose focus_keyword is referenced in the HTML body
  - Extract focus keyword from `publish_<slug>.py` (`RANK_MATH_FOCUS`)
  - Match against `list_prompts` via embedding or string-contains
- **Outreach investment (citation live)** → prompts where `target_url` appears in `get_url_report`
  - `mcp__peec-ai__get_url_report(filters=[{url in [target_url]}])`
- **Zone intervention** → all prompts with the zone tag

### 4. Compute attribution per investment

```
attribution_score =
    sum(affected_prompts[p].delta for p in matched_prompts)
  - baseline_drift
```

**baseline_drift** = median delta of non-affected prompts in the same window. This isolates the intervention effect from general drift.

### 5. Detect patterns (three buckets)

**Winners** (high attribution):
- Which content type (HOW_TO / COMPARISON / PILLAR) moved the most
- Which outreach target class (EDITORIAL / UGC / REFERENCE) produced most citations
- Which zone grew fastest

**Losers** (negative or zero attribution despite investment):
- Content published but not indexed / cited
- Pitches with no response after 14 days
- Zones stagnant despite new content (→ content misses the intent layer)

**Surprises** (positive delta without a direct investment):
- Prompts that gained without direct action (organic spillover from another page?)
- Sudden drops (competitor action? algorithm shift?)

### 6. Generate the narrative

Claude synthesizes a narrative **≤400 words** using the schema below.

### 7. Persist learnings

Save to `<project>/growth_loop/YYYY-MM-DD_learnings.json` — used by the next runs of `peec-cluster` and `peec-outreach` as priors.

---

## Narrative schema

```markdown
# Growth loop — <project> (<window>)

## Headline
<One sentence: what's the most important insight of this period?>

## What moved
- Overall visibility: X% → Y% (<N pp>)
- Strongest zone: <name> (+Z%)
- Weakest zone: <name> (flat or −)
- Top-3 single-prompt lifts: <list>

## What actually worked
<2–3 sentences. Not "the content plan" — but: "Article X became a citation in 11 of 15
target prompts; the retainer pitch at evergreen.media produced Y citations within 10
days; the Shopify zone grew organically without new content there — likely spillover
from zone Z.">

## What did not work
<1–2 sentences: which investment had zero effect, and the most plausible reason.>

## DO NOW (prioritized, max 3)
1. <concrete action with deadline>
2. <concrete action>
3. <concrete action>

## STOP DOING
- <pattern that was identified as time-waste>
```

## Learnings JSON schema

```json
{
  "period": {"start": "...", "end": "...", "window": "weekly"},
  "overall_visibility_delta": 0.04,
  "winners": {
    "content_types": [{"type": "HOW_TO_GUIDE", "avg_lift": 0.08, "n": 2}],
    "outreach_domains": [{"domain": "evergreen.media", "citations_gained": 5}],
    "zones": [{"zone_tag": "retainer-decision", "lift": 0.12}]
  },
  "losers": {
    "content_types": [],
    "outreach_domains": [{"domain": "<...>", "response_rate": 0.0}]
  },
  "surprises": [],
  "next_actions": ["..."],
  "stop_doing": ["..."]
}
```

---

## Quick reference

| Step | Tool |
|---|---|
| Overall visibility trend | `mcp__peec-ai__get_brand_report(dimensions=["date"])` |
| Per prompt | `mcp__peec-ai__get_brand_report(dimensions=["prompt_id", "date"])` |
| Per zone (if tagged) | `mcp__peec-ai__get_brand_report(dimensions=["tag_id", "date"])` |
| Citation source check | `mcp__peec-ai__get_url_report(filters: url in [...])` |
| Content log | git log on content-automation path |
| Outreach log | local `<project>/outreach/*.md` |

---

## Done criteria (self-check before returning)

A growth report is only complete when:

1. Narrative is ≤400 words — longer reports aren't read and usually hedge
2. Attribution is reasoned, not guessed — every winner / loser needs a causal mechanism, not just correlation
3. Exactly 3 next-actions — not 7, not 1. Three is the weekly capacity ceiling
4. At least 1 STOP DOING — the courage to discard is worth more than new ideas
5. `learnings.json` persisted — without it, no loop

---

## Guardrails (do not do these)

- Do not ship a dashboard — a dashboard is not a report
- Do not sell correlation as causation — visibility went up; competitor also had an SSL outage
- Do not ignore baseline drift — without a comparison group, every lift is suspect
- Do not skip the STOP DOING line — addition without subtraction fragments energy
- Do not ship a report without persisting learnings — the next cycle can't learn
- Do not run this before 4 weeks of history — too little signal, pattern detection degenerates to noise
