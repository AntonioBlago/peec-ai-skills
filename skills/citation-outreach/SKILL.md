---
name: citation-outreach
description: Turns Peec AI's get_actions recommendations + forum/UGC discovery into a prioritized outreach pipeline with pitch templates, contact extraction, status tracking, and success measurement. Goes beyond "here is a list of domains" — produces ready-to-send pitches, covers Reddit / Gutefrage / editorial / owned quadrants, and tracks citation gains week over week. Use when a Peec project has active competitor gaps and needs systematic off-site work, not just content production.
user-invocable: true
---

# Citation Outreach

## Role
Writing new content isn't enough — most AI-visibility lift comes from citations on domains LLMs already crawl. This skill turns `get_actions` plus forum discovery into a **prioritized outreach pipeline** with concrete, target-specific pitches, a tracker, and a citation-gain measurement after 4 weeks.

## Input
- `project_id` — Peec project
- optional `scope` — `editorial` | `ugc` | `reference` | `owned` | `all` (default `all`)
- optional `weekly_cap` — max pitches per week (default 5)
- optional `own_asset_url` — an own URL to actively pitch (case study, pillar, tool)

## Output
- One outreach tracker at `<project>/outreach/YYYY-Wkk_outreach_log.md` (schema below)
- One ready-to-send pitch per queued target, filled with concrete quote + concrete offer
- After 4 weeks: one attribution summary feeding into `growth-loop-reporter`

## When to use
- After `@ai-visibility-setup` Phase 8 or `@peec-content-intel` Phase 6 — when the opportunity list is in
- Weekly ritual: 3–5 quality pitches to stay independent of Google
- Whenever Peec `get_actions` surfaces high-opportunity `editorial` / `ugc` / `reference` rows

Do not use when:
- No opportunity list from Peec (run `get_actions` first)
- Brand has no reference page / case study to pitch yet (run `content-write` first)

---

## Pipeline

### 1. Aggregate opportunity sources

```
mcp__peec-ai__get_actions(project_id, scope="overview",  start_date, end_date)
mcp__peec-ai__get_actions(project_id, scope="editorial", start_date, end_date)
mcp__peec-ai__get_actions(project_id, scope="ugc", domain="reddit.com",  start_date, end_date)
mcp__peec-ai__get_actions(project_id, scope="ugc", domain="youtube.com", start_date, end_date)

mcp__peec-ai__get_domain_report(
  project_id, start_date, end_date,
  filters=[{field: "gap", operator: "gt", value: 0}],
  limit=40
)
```

Merge into one candidate table:
`target_url | domain | type | opportunity_score | retrieval_% | citation_rate | mentioned_brand_ids`

### 2. Sort into 4 quadrants

```
         │  High impact     │  Low impact
─────────┼──────────────────┼──────────────────
Easy ask │  QUICK WINS      │  SNACKABLE
         │  (pitch now)     │  (when time allows)
─────────┼──────────────────┼──────────────────
Hard ask │  STRATEGIC       │  DROP
         │  (build relation)│
```

- **Impact** = `opportunity_score × retrieval_%`
- **Difficulty**:
  - `easy`   = reddit thread (just post), Gutefrage, OMR forum
  - `medium` = editorial blog (email), LinkedIn author
  - `hard`   = major publication, closed community

### 3. Extract contact per target

| Target type | Contact source |
|---|---|
| Editorial blog | `WebFetch(url)` → author box / LinkedIn / contact page |
| Reddit thread | OP username visible in `mcp__peec-ai__get_url_content` output |
| YouTube | channel URL from `channel_title` → `/about` page |
| Gutefrage | no direct contact (post the answer directly) |
| LinkedIn Pulse | author profile in URL path |

Produce: `target_url | target_type | contact_method | contact_handle | language | topic_focus`

### 4. Pick pitch template

**Write in the target's language.** The templates below are structural — fill them in the language of the target URL.

#### Editorial inclusion pitch

```
Subject: Expert quote for your article on <topic> — <1-line angle>

Hi <author>,

I came across your article "<title>" while researching <concrete tie-in>.
One section could use an added angle from my practice: <concrete section>.

I've worked <N> years as <role> with <specialization>. In a recent
<project context>, I observed <concrete number / finding>.

Would a 2–3 sentence expert quote or a short sidebar with my take work?
I can deliver copy + name + headshot within 48 hours.

<signature with own domain + 1 reference URL>
```

**Rule:** quote the concrete section, offer a concrete addition. No generic "happy to collaborate".

#### Reddit thread answer

Not a pitch — a direct, substantive answer to the OP (150–300 words). Rules:

1. First 2 sentences answer the question directly — no preamble
2. Middle: one concrete method / number / example from own practice
3. Optionally end with one own source — only if it completes the answer, never as CTA
4. Match the OP's language exactly
5. Use a personal account, never a brand account (reddit policy)

#### Gutefrage / forum answer

Same shape as Reddit, 100–200 words. Forum users prefer compact answers.

#### YouTube comment + follow-up

1. Substantive comment under the video (300–500 chars, question + addition)
2. After 48h without response: email to the channel owner referencing 3 of your own videos / posts that match the channel theme

### 5. Fill templates with project context

```
mcp__peec-ai__get_project(project_id)
# or: mcp__visiblyai__get_project(project_id)
#   → brand_name, USPs, custom_content_prompt, crawl_summary
```

Per candidate, replace every angle bracket with **specific** detail:
- `<concrete section>` → real quote from target URL
- `<concrete number>` → real number from own project (retainer case, traffic lift, measurable result)
- `<project context>` → concrete industry of the target author

### 6. Append to tracker

File: `<project>/outreach/YYYY-Wkk_outreach_log.md`

```markdown
# Outreach log — week <ISO-week>

| # | Target | Type | Status | Sent | Replied | Citation | Notes |
|---|--------|------|--------|------|---------|----------|-------|
| 1 | evergreen.media/ratgeber/ki-seo | editorial | sent   | 2026-04-22 | pending | — | expert quote on retainer pricing |
| 2 | r/selbststaendig/comments/xyz   | reddit    | posted | 2026-04-22 | —       | answer_score=12 | — |
```

Status values: `queued` → `sent` | `posted` → `replied` → `citation_live` | `declined` | `ignored`

### 7. Measure after 4 weeks

For each target with `status=citation_live`:

```
mcp__peec-ai__get_url_report(filters=[{field: "url", values: [target_url]}])
# retrievals before vs. after
mcp__peec-ai__get_brand_report(...)
# own-brand visibility for prompts that had this URL as source
```

Winners (citation gain > baseline) feed into `growth-loop-reporter` as a "working leverage pattern" — next cycle prioritizes similar targets.

---

## Quick reference

| Step | Tool |
|---|---|
| Opportunity sources | `mcp__peec-ai__get_actions(scope=overview/editorial/ugc)` |
| Gap URLs | `mcp__peec-ai__get_domain_report(filters: gap>0)` |
| Thread content + OP | `mcp__peec-ai__get_url_content` |
| Contact extraction | `WebFetch` on target URL |
| Project frame for pitch | `mcp__peec-ai__list_projects` + `get_project` |
| Citation measurement | `mcp__peec-ai__get_url_report(dimensions=["date"])` |

---

## Done criteria (self-check before returning)

An outreach batch is only complete when:

1. ≤ `weekly_cap` pitches — 5 quality pitches beat 20 generic ones
2. Every pitch has a concrete quote from the target URL
3. Every pitch offers something specific — a concrete asset, by a concrete date
4. Tracker is live — every pitch logged with `status=sent | posted`
5. Each pitch has an explicit success criterion: "expecting a mention in section X, measurable via `get_url_report` within 6 weeks"

---

## Guardrails (do not do these)

- Do not send generic "happy to contribute" pitches — quote something specific or don't send
- Do not use a brand account on Reddit / Gutefrage — it gets you banned; only personal accounts
- Do not skip follow-ups — 30–50% of editorial citations come from a follow-up 7–10 days later
- Do not exceed the weekly cap — 3 considered pitches beat 15 mass pitches
- Do not pitch before there's an asset to back it — no case study or reference page = no substance
- Do not measure before 4 weeks — LLM indexing of new citations takes time
