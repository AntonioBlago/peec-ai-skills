---
name: content-cluster-builder
description: Turns a Peec AI prompt set into strategic content zones — not keyword groups. Groups prompts by buyer intent + funnel stage + visibility gap + shared demand signals, producing 4–8 "content zones" with the competitive weakness to attack, supporting evidence (forum quotes, SERP patterns), and a rank-ordered next-move per zone. Use when a Peec project has 20+ prompts and needs a topic architecture — not a flat content calendar. Output is a strategic map, not a list.
user-invocable: true
---

# Content Cluster Builder

## Role
Reduce a flat Peec prompt set to 4–8 **strategic zones** — each with a structural weakness in the competition, one measurable metric, and one "do exactly this now" action. Not keyword clusters. Not a content calendar.

A zone is coherent only when three axes line up:

```
      Intent
       ↑
Visibility gap
       ↑
Demand signal
```

If a candidate zone fails any axis, it gets merged or dropped.

## Input
- `project_id` — Peec project
- optional `date_range` — default last 30 days
- optional `target_zones` — default 4–8 (skill picks the resolution)
- optional `focus_funnel_stage` — restrict to one stage

## Output
One markdown zone map (schema in §Output schema), plus one Peec tag per zone (`zone:<slug>`) with all prompts retagged, so `growth-loop-reporter` can measure zone lift later.

## When to use
- ≥20 Peec prompts and the team has lost the overview
- After `@ai-visibility-setup`, before `@content-write` per article
- Quarterly strategy refresh
- Before an investment conversation ("what is our AI content strategy?")

Do not use when:
- <10 prompts (not enough mass for real zones)
- Prompts aren't split into Awareness / Consideration / Decision / Retention yet (run `@ai-visibility-setup` first)

---

## Pipeline

### 1. Pull prompt inventory + visibility state

```
mcp__peec-ai__list_prompts(project_id)
mcp__peec-ai__get_brand_report(
  project_id, start_date, end_date,
  dimensions=["prompt_id"],
  filters=[{field: "brand_id", operator: "in", values: [own_brand_id]}]
)
mcp__peec-ai__get_url_report(
  project_id, start_date, end_date,
  dimensions=["prompt_id"],
  filters=[{field: "gap", operator: "gt", value: 0}]
)
```

Merge into one table:
`prompt_id | text | funnel_stage | topic | tags | own_visibility | gap_size | top_competitor_url | top_competitor_class`

### 2. Score each prompt on three axes

- **Intent density** (0–1): semantic overlap with other prompts in the same funnel stage. Compute via embedding cosine (e.g. `text-embedding-3-small`) or `mcp__visiblyai__classify_keywords` as a regex-based fallback.
- **Visibility gap** (0–1): `1 − own_visibility`, weighted by `gap_size / max_gap_size_in_project`.
- **Demand density** (0–1): count of `classification=DISCUSSION` source URLs for this prompt in `get_url_report`. High = real buyers are asking.

**Combined score** = `intent_density × visibility_gap × demand_density` (multiplicative — all three must be non-zero).

### 3. Cluster (embedding-based, not regex)

**Primary — `mcp__visiblyai__query_fanout` as semantic bridge** (≥v0.6.0):

```
for each prompt with score > median:
  mcp__visiblyai__query_fanout(url=own_domain, keyword=prompt_keyword, language=lang)
  → fanout_queries[] becomes the semantic fingerprint
```

Two prompts go in the same zone when their fan-out queries overlap ≥40%.

**Fallback — direct LLM instruction:**

```
Given these <N> prompts with metadata (funnel stage, tags, visibility gap,
demand signal), group them into 4–8 strategic content zones by:

1. Same buying decision question (not merely similar keywords)
2. Same funnel stage (or adjacent)
3. Shared demand signal (same pain points from forum data)
4. Shared structural leverage (same competitor type we can beat)

For each zone: name, 2-sentence thesis, prompt_ids, shared competitor weakness,
one concrete "do exactly this now" action.
```

### 4. Validate each candidate zone

Four checks, all must pass:

1. **Coherence** — ≥3 prompts with ≥0.4 embedding similarity to zone centroid
2. **Funnel** — max 1 funnel stage of spread (Awareness + Consideration ok; Awareness + Decision not)
3. **Gap** — average `visibility_gap` of zone > 0.3
4. **Uniqueness** — each zone has a competitor type not won by another zone

Zones that fail get merged to nearest neighbor or dropped.

### 5. Extract 6 components per valid zone

| Component | Source |
|---|---|
| **Name** (≤40 chars) | synthesize from prompts |
| **Thesis** (2 sentences) | why this zone exists + why you win here |
| **Funnel span** | TOFU / MOFU / BOFU / Retention |
| **Top 5 prompts** | sorted by combined score |
| **Competitor structural weakness** | from `peec-content-intel`: what's missing across all competitors in this zone |
| **One-move action** | concrete verb, concrete artifact, concrete channel — no "analyze X", instead "write article Y with structure Z and pitch at Z1, Z2" |

### 6. Rank zones by potential impact

```
potential_impact = sum(prompts.visibility_gap × prompts.demand_density × funnel_weight)

funnel_weight = {Awareness: 0.6, Consideration: 1.0, Decision: 1.5, Retention: 1.2}
```

### 7. Persist zones as Peec tags

For each validated zone:

```
mcp__peec-ai__create_tag(project_id, name="zone:<slug>", color="<color>")
for each prompt in zone:
  mcp__peec-ai__update_prompt(project_id, prompt_id, tag_ids=[..., zone_tag_id])
```

This is the hook `growth-loop-reporter` uses to track zone performance over time.

---

## Output schema

```markdown
# Content zones for <project> (<YYYY-MM-DD>)

## Zone 1 (score 0.85): <Name>

**Thesis:** <2 sentences>
**Funnel:** Consideration → Decision
**Prompts:** 7 (see appendix A)

**Competitor weakness:**
- None of the top-5 competitor URLs address <topic X>
- 4 of 5 say nothing about <pricing / retainer / methodology>

**ONE MOVE NOW:**
> Write a HOW-TO-GUIDE, title "<concrete>", H2 outline <concrete>,
> publish at `/blog/<slug>`, then within 7 days pitch at
> <domain 1 from get_actions>, <domain 2>, and answer <reddit URL>.

**Success metric (measure after 6 weeks):**
Peec visibility across the 7 prompts: avg X% → Y%.

---

## Zone 2 (score 0.78): ...
```

---

## Quick reference

| Step | Tool |
|---|---|
| Load prompts / topics / tags | `mcp__peec-ai__list_prompts` / `list_topics` / `list_tags` |
| Visibility per prompt | `mcp__peec-ai__get_brand_report(dimensions=["prompt_id"])` |
| Gap per prompt | `mcp__peec-ai__get_url_report(filters: gap>0)` |
| Semantic cluster signal | `mcp__visiblyai__query_fanout` or `classify_keywords` |
| Pain density | `mcp__peec-ai__get_url_content` on reddit threads |
| Persist zone | `mcp__peec-ai__create_tag` + `update_prompt` |

---

## Done criteria (self-check before returning)

A zone map is only complete when:

1. Every zone has a one-move action with a concrete verb
2. Every zone has a structural competitor weakness (not "weak content" — "competitor X lacks pricing, competitor Y lacks FAQ block")
3. Every zone is measurable (Peec tag exists, prompt_ids listed)
4. ≤8 zones total — if the algorithm returns 12, merge or drop the weakest 4

---

## Guardrails (do not do these)

- Do not cluster by keyword — "Neuro-SEO Blog" + "Neuro-SEO Shop" address different funnels and different buyers
- Do not ship a zone map where all zones are Awareness — Decision coverage is often more valuable than five Awareness clusters
- Do not create a zone without a named competitor weakness — if you can't name what they do wrong, the zone isn't real
- Do not return more than 8 zones — 12 zones means 12 half-finished topics; 5 zones means 5 topics you win
- Do not skip the tag persistence step — without tags, `growth-loop-reporter` has nothing to attribute against
