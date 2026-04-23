---
name: peec-content-intel
description: Content-intelligence workflow that turns a Peec AI visibility gap into a publish-ready content brief. Combines Peec (prompt visibility, source URLs, scraped chat responses), Visibly AI (backlinks, onpage, keywords, GSC), and Reddit / forum mining. Uses Query Fan-Out to expand one prompt into 5–8 sub-queries and scores competitor URLs for attackability. Use when the user wants to find content opportunities, evaluate competitor content, build a content brief from Peec data, or discover what content wins specific AI prompts.
user-invocable: true
---

# Peec Content Intel

## Role
For one Peec prompt that the brand is losing, produce one publish-ready content brief: sub-queries, verbatim buyer pains, competitor breakdown, outline, focus keywords, and outreach targets.

## Input
- `project_id` — Peec project (read from `setup_state.json` per pre-flight; do not re-resolve)
- `prompt_id` — the target prompt (must have ≥24h of data)
- optional `date_range` — default last 28 days
- `language` — read from `setup_state.json` (`prompt_language`); user can override per-run, but never default to `en` silently
- `target_country` — read from `setup_state.json`; drives forum source picks (DE→reddit/r/de+gutefrage+t3n, AT→reddit+derstandard, US→reddit+quora, CH→reddit/r/de+r/fr) and SERP/GSC market filters

## Output
One markdown brief per prompt, saved at `briefs/<YYYY-MM-DD>_<prompt-slug>/brief.md`, plus the raw data next to it (`competitor-urls.json`, `forum-pains.json`, `scoring.json`). No dashboards.

## When to use
- "Which content wins Peec prompt X?"
- "Analyze the sources competitors get cited for on prompt X"
- "What's the content gap between me and competitor.de?"
- Runs **after** `ai-visibility-setup` — the project must exist with structured prompts.

Do not use when:
- Prompt has <24h of Peec data (no chats / sources yet)
- No own-brand absence on the prompt (nothing to close)

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
        Run /ai-visibility-setup first."
If completed_at older than 90 days: WARN once, continue.
Use peec_project_id from state — don't re-resolve via list_projects.
```

### 1. Find the gap URLs

```
mcp__peec-ai__get_brand_report(
  project_id, start_date, end_date,
  dimensions=["prompt_id"],
  filters=[{field: "prompt_id", operator: "in", values: [prompt_id]}]
)
mcp__peec-ai__get_url_report(
  project_id, start_date, end_date,
  dimensions=["prompt_id"],
  filters=[
    {field: "prompt_id", operator: "in", values: [prompt_id]},
    {field: "gap", operator: "gt", value: 0}
  ],
  limit=25
)
```

Output: up to 25 URLs, sorted by retrieval frequency, each with a `classification` (LISTICLE / ARTICLE / COMPARISON / HOW_TO_GUIDE / PROFILE / DISCUSSION).

Interpretation:
- **LISTICLE / COMPARISON** → outreach targets (get included)
- **HOW_TO_GUIDE / ARTICLE** → own-content targets (write and publish)
- **PROFILE / DISCUSSION (reddit, youtube)** → community targets (participate)

### 2. Query Fan-Out

**Primary path — `mcp__visiblyai__query_fanout`** (Visibly MCP ≥ v0.6.0, ~3–5 credits):

```
mcp__visiblyai__query_fanout(
  url="https://<own-or-competitor-domain>/<page>",
  keyword="<focus_keyword>",
  data_source="dataforseo",   # or "gsc" / "both"
  gsc_property=null,          # required if data_source includes gsc
  language="de"               # or "en"
)
```

Returns: `fanout_queries[]`, `coverage_score` (0–1), `covered_count` / `total_count`, `gaps[]` (sub-queries not addressed on the URL — this is the content backlog), `coverage_details[]`.

Fire once per top gap URL from Phase 1. Replaces sub-query generation + crawling + semantic match in one call.

**Fallback — inline heuristic** (if Visibly MCP unavailable or credits tight):

Generate 6 sub-queries along fixed intent axes:
1. Synonym (same intent, different wording)
2. Decision ("what does it cost", "when to switch")
3. Comparison ("X vs Y")
4. Problem ("why doesn't X work")
5. Long-tail (narrow niche)
6. Forum / community (informal phrasing)

Coverage matching is then skipped — flag that explicitly in the brief.

### 3. Mine forum pain per sub-query

**Reddit** (tested 2026-04-19): `WebFetch` against `reddit.com` is blocked. The workaround that works: Peec has already scraped Reddit threads, so use

```
mcp__peec-ai__get_url_content(project_id, url="https://reddit.com/r/<sub>/comments/<id>/...")
```

Procedure:
1. From Phase 1, list all `classification=DISCUSSION` + `domain=reddit.com` URLs
2. For the top 3 by retrieval, call `get_url_content`
3. Extract: verbatim pain quotes, tool mentions, competitor mentions, sentiment

**Gutefrage / t3n / OMR**:
```
WebSearch("site:gutefrage.net <query>")
WebSearch("site:t3n.de/forum <query>")
WebSearch("site:omr.com <query>")
WebFetch(url, "Extract the original question verbatim, plus top 3 answers. Note frustrations, decision triggers, competitor/brand mentions.")
```

Gutefrage blocks WebFetch with 403. Fallback: Google search snippets + archive.org.

Per sub-query, aggregate: 3–5 verbatim pain quotes, competitor mentions with sentiment, top 2–3 thread URLs for later engagement.

### 4. Score competitor URLs (Visibly deep-dive)

Per top gap URL from Phase 1:

```
mcp__visiblyai__get_backlinks(domain="<competitor-domain>", limit=10, location="Germany")
mcp__visiblyai__onpage_analysis(url="<competitor-url>", keyword="<focus-keyword>")   # 15 credits, top 3 only
mcp__peec-ai__get_url_content(project_id, url="<competitor-url>")                    # for outline mining
mcp__visiblyai__get_keywords(domain="<competitor-domain>", limit=200, location="Germany")
```

**Backlinks caution**: `get_backlinks` can return 260 KB+ (2,836 backlinks for noahlutz.de). Always pass `limit: 10-20` or delegate to a subagent. For headline metrics (`total_count`, `rank`, `domain_from_rank`), `limit=1` is enough.

DR interpretation:
- **DR <20** → organic authority, realistic to overtake
- **DR 20–50** → established, 6–12 months of content + targeted links
- **DR >50** → hard to beat head-on; flank with long-tail instead

### 5. Opportunity scoring

```
score = (retrieval_freq × gap_size × forum_pain_density)
        / (domain_DR × (1 + content_quality_diff))
```

Tiers:
- **Tier 1 (score >50)** — attack now: write + outreach
- **Tier 2 (20–50)** — 3–6 month horizon
- **Tier 3 (<20)** — park or flank with long-tail

### 6. Render brief

Save to `briefs/<YYYY-MM-DD>_<prompt-slug>/brief.md`. Schema below.

---

## Brief schema

```markdown
## Content Brief: <prompt text>

### Goal
Win Peec prompt: "<prompt_text>"
Funnel stage: Awareness | Consideration | Decision | Retention
Current own visibility: X%  →  Target: Y% in 90 days

### Buyer language (forum pain, verbatim)
- "<verbatim quote>"  (source: r/selbststaendig, 2026-03)
- "<verbatim quote>"  (source: Gutefrage)
- "<decision trigger>"

### Sub-queries (Query Fan-Out)
1. <sub-query>
2. <sub-query>
...

### Competitor landscape
| URL | Class | Retrieval | DR | Opp score | Note |
|---|---|---|---|---|---|
| evergreen.media/ki-seo | ARTICLE | 22% | 47 | 35 | high DR, pitch as contributor |
| noahlutz.de/ki-seo | LISTICLE | 9% | 22 | 68 | direct attack, similar DR |

### Recommended format
<LISTICLE | COMPARISON | HOW-TO | DEFINITION> — based on dominant URL class

### Title (draft, ≤60 chars)
<title>

### Meta description (≤155 chars)
<description using buyer language>

### Outline (H2 / H3)
1. <opening pain>
2. <definition / framework>
3. <decision matrix or checklist>
4. <practice examples>
5. <pitfalls>
6. <CTA>

### Focus + secondary keywords
- Focus: <keyword>  (volume, intent)
- Secondary: <kw2>, <kw3>, <kw4>   (from keyword gap)

### Backlink strategy
- <domain 1>: editorial pitch (template)
- <subreddit>: join thread (URL)
- <editorial>: contribute to existing article

### KPI
- Prompt visibility after 90 days: Y%
- GSC position for focus keyword: top 10
- ≥3 backlinks from DR >30
```

---

## Quick reference

| Step | Tool |
|---|---|
| Gap URLs | `mcp__peec-ai__get_url_report(filters: gap>0)` |
| AI response + sources | `mcp__peec-ai__list_chats` → `get_chat` |
| Scraped competitor content | `mcp__peec-ai__get_url_content` |
| Query Fan-Out + coverage | `mcp__visiblyai__query_fanout` (≥v0.6.0) |
| Backlink profile | `mcp__visiblyai__get_backlinks` |
| 24-point onpage audit | `mcp__visiblyai__onpage_analysis` (15 cr) |
| Competitor keywords | `mcp__visiblyai__get_keywords` |
| Intent classification | `mcp__visiblyai__classify_keywords` |
| Full-site crawl | `mcp__visiblyai__crawl_website` (15–60 cr) |

## Credit budget (Visibly)

Per prompt analysis: ~45–75 credits.
- 1× `get_backlinks` per top-3 competitor domain (cheap, often ~0)
- 3× `onpage_analysis` → 45
- 1× `get_keywords` per top-2 competitor (cheap)

Batch of 10 prompts: ~500–750 credits.

---

## Guardrails (do not do these)

- Do not analyze prompts with <24h of Peec history — phase 1 returns empty
- Do not `WebFetch` Gutefrage (403) — use WebSearch snippets instead
- Do not run `onpage_analysis` on more than the top-3 URLs — credit drain
- Do not mix funnel stages in the fan-out — a MOFU parent must not pull in TOFU sub-queries, or the brief dilutes
- Do not judge a competitor by DR alone — weak content at high DR is still attackable; read the actual content via `get_url_content`
- Do not run this skill before `ai-visibility-setup` — depends on structured prompts/topics/tags
