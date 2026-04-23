---
name: ai-visibility-setup
description: End-to-end Peec AI project setup — competitor discovery from real AI chats, customer-journey prompt design across Awareness → Consideration → Decision → Retention, topic/tag taxonomy, GSC-based keyword mapping, forum pain-point mining (Reddit, Gutefrage, t3n, OMR), and a categorized executable backlog. Use when the user wants to set up, restructure, or audit a Peec AI project for their own brand or a client. 9 phases, full funnel coverage, real buyer language.
user-invocable: true
---

# AI Visibility Setup

## Role
Take a Peec AI project from empty (or broken) to operator-ready: correct competitors, full-funnel prompts, coherent taxonomy, GSC keyword mapping, forum-mined buyer language, and a categorized executable backlog the client can run for the next 2 weeks.

## Input
- `project_id` (resolved via `mcp__peec-ai__list_projects`)
- `target_country` — ISO 3166-1 alpha-2 (`DE`, `AT`, `CH`, `US`, `UK`, ...). Default `DE`. Drives SERP/GSC filters and forum source selection.
- `prompt_language` — ISO 639-1 (`de`, `en`, `fr`, ...). Default = lowercase of `target_country` (`DE` → `de`). Drives the language Peec prompts are authored in.
- Optional: `secondary_languages` — list, default `[]`. Used for multi-market projects (e.g. DE primary + EN secondary).
- Optional: `offer_keywords` (retainer, monthly, etc.), `own_domain`
- Optional: `scope` — `full` | `audit` | `partial:<phase>` | `competitors_only` | `prompts_only` | `taxonomy_only` (default: auto-detected from setup state, see Phase 0)

**Resolving language/country at start:**
1. If state file exists with these fields → use them, skip the question.
2. Else if user passed them as arguments → use those.
3. Else infer from `own_domain` TLD (`.de` → DE/de, `.at` → AT/de, `.ch` → CH/de + ask de/fr, `.com` → ASK).
4. Else ASK the user **once** before Phase 1: "Target country (ISO, e.g. DE)? Prompt language (ISO, e.g. de)?". Persist the answer in state.

Never silently default to `EN`/`en` when the project has no signal — this corrupts every downstream skill.

## Output
A setup report with: before/after counts, funnel distribution (e.g. 5/5/5/5), the single **hero prompt** to win first, the refresh timeline (24h for fresh data), a categorized P0/P1/P2 backlog, and any user-preference memories saved. No dashboards.

## When to use
- "Set up Peec for <client>"
- "My Peec competitors are wrong / not real competitors"
- "Design prompts for my customer journey"
- "Map GSC keywords to my Peec prompts"
- "Restructure Peec topics / tags"
- Audit of an existing AI-visibility tracking setup

## Prerequisites
- Peec AI MCP connected (`mcp__peec-ai__*`)
- Visibly AI MCP connected (`mcp__visiblyai__*`) — optional, only for GSC
- GSC + GA4 connected inside Visibly AI (check via `get_google_connections`)

## State

This skill **owns** the setup state file. See [`_shared/SETUP_STATE.md`](../_shared/SETUP_STATE.md) for the full schema and protocol.
- **Reads** `<project>/growth_loop/setup_state.json` at Phase 0 to decide the run mode (`full | audit | partial | skip`).
- **Writes** the same file at the end of Phase 9 with merged `phases_completed` and a fresh `snapshot`.

All other skills in this repo refuse to run without this file — never bootstrap a setup from inside another skill.

---

## Phase 0 — State check & mode selection

Always runs first. Cheap (single file read + at most one parallel Peec read in brownfield case). Determines whether the rest of the run is needed at all.

```
1. Read <project>/growth_loop/setup_state.json

2. If state file MISSING:
   2a. Live-detect Peec content (parallel reads):
         list_brands(project)
         list_prompts(project, limit=5)
         list_topics(project)
         list_tags(project)
   2b. If Peec is empty (≤2 brands AND ≤4 prompts AND ≤0 topics):
         → mode = full     (greenfield — proceed to Phase 1)
   2c. If Peec is populated (≥3 brands OR ≥5 prompts OR ≥1 topic):
         → mode = import   (brownfield — see "Import mode" below)

3. If state file PRESENT, branch on `completed_at`:
     < 30 days ago       → mode = skip      (show summary, ASK user before continuing)
     30–90 days ago      → mode = audit     (live-diff snapshot, only redo drifted phases)
     > 90 days ago       → mode = full      (warn: stale)

4. If user passed an explicit `scope`, that wins over auto-detection.

5. Print one line:
     "Setup state: <found|missing|imported> · age: N days · mode: <full|import|audit|partial|skip>"
```

### `import` mode (brownfield) — runs entirely inside Phase 0

Per [`_shared/SETUP_STATE.md` §`import` mode](../_shared/SETUP_STATE.md), this mode reconstructs `setup_state.json` from live Peec data without re-doing discovery.

```
1. Show user one line:
     "Detected existing Peec setup: <N> brands, <M> prompts, <T> topics, <G> tags."
2. ASK three things at once (single user turn):
     - "Import this as the setup state, or run full setup from scratch? [import/full]"
     - "Target country (ISO, e.g. DE)?"
     - "Prompt language (ISO, e.g. de)?"
3. If user picks `import`:
     a. Infer completed_at (NEVER default to now silently):
          read created_at from list_brands + list_prompts;
          completed_at = min(created_at across first 5 brands AND first 5 prompts)
          If unavailable → list_chats(limit=1, sort=asc).timestamp
          If still unavailable → ASK user one bucket question
            ("when did you set this up? [today/past month/past quarter/past year/older]")
            and map to a date.
     b. Build state object:
          phases_completed = inferred from non-empty buckets (brands≥3 → +competitors; etc.)
          snapshot         = the counts just read
          completed_at     = inferred per (a) above
          imported_at      = now (UTC)
          last_audit_at    = now
          hero_prompt_id   = null
          target_country, prompt_language = from user answers in step 2
          notes            = "imported from existing Peec project on <imported_at>;
                              original setup inferred at <completed_at>"
          setup_version    = "1.1"
     c. **Persist immediately** — atomic write to <project>/growth_loop/setup_state.json
        (write to .tmp, then rename). Do not wait for any other phase.
     d. Print:
          "State imported: <project>/growth_loop/setup_state.json (phases: X/7).
           Inferred setup date: <YYYY-MM-DD> (~N days ago).
           Run /ai-growth-agent to pick the next move, or /ai-visibility-setup
           partial:gsc_mapping to fill in skipped phases."
     e. Exit Phase 0. Do NOT proceed to Phase 1 — import mode finishes here.
        The user can now invoke any consumer skill; they will all read the freshly
        written state. If they want missing phases (e.g. forum_mining never happened),
        they explicitly call partial:<phase>.
4. If user picks `full`:
     CONFIRM ONCE MORE: "Full setup will create new prompts/topics/tags alongside
     the existing ones. Proceed? [yes/no]"
     On yes → mode = full, proceed to Phase 1.
     On no  → exit cleanly.
```

**`skip` mode behaviour:** show the existing snapshot (counts, phases, hero_prompt_id) and ask "Re-run anyway? [audit / partial:<phase> / full / no]". Do not auto-run.

**`audit` mode behaviour:** call `list_brands / list_prompts / list_topics / list_tags` and compare counts to `snapshot`. For each phase where drift > 20% (or a P0 red flag from Phase 1 reappears), re-run only that phase. Append `last_audit_at` on write.

**`partial:<phase>` mode:** jump straight to the named phase, skip everything else.

If `mode == skip` and user declines re-run, exit cleanly with a 3-line summary — no further phases.

---

## Phase 1 — Initial audit

Run in parallel:

```
mcp__peec-ai__list_projects
mcp__peec-ai__list_brands(project_id)         # current competitors
mcp__peec-ai__list_prompts(project_id, limit=200)
mcp__peec-ai__list_topics(project_id)
mcp__peec-ai__list_tags(project_id)
```

**Red flags to call out:**
- Competitors list contains **SaaS tool brands** (SEMrush, Ahrefs, Sistrix, Moz, Ryte, Yoast, Screaming Frog, SurferSEO, Frase). For a freelancer / consultant project these distort SoV — they are not buyers' alternatives.
- Prompts clustered in one funnel stage only (e.g. all MOFU "empfiehl" — no Awareness / Decision / Retention coverage).
- Topics represent **themes only** (e.g. "AI" / "SEO") — can't track funnel performance.
- Tags are only Peec's default 4 (branded / non-branded / informational / transactional) — no offer-specific slicing possible.

---

## Phase 2 — Competitor discovery (ground truth)

### 2a. Extract from AI chats (authoritative)

For each **losing prompt** (own brand 0% visibility, competitors present):

```
mcp__peec-ai__list_chats(project_id, start_date, end_date, prompt_id=<losing_prompt>)
  → pick 1 chat per engine (chatgpt-scraper, perplexity-scraper, google-ai-overview-scraper)
mcp__peec-ai__get_chat(project_id, chat_id)
  → inspect messages[] for freelancer / consultant names
  → inspect sources[]  for their domains
```

Extract: human names, domain names, sources the AI pulled. These are the **real** competitors LLMs recommend against you.

### 2b. Supplement with web research

```
WebSearch("SEO Freelancer Deutschland <niche> 2026")
WebSearch("<niche> Freelancer Experte KI ChatGPT empfehlen")
```

Cross-check against the domain report — any domain retrieving (`get_domain_report`) but not tracked as a brand is an **invisible competitor**:

```
mcp__peec-ai__get_domain_report(project_id, start_date, end_date, limit=25)
  → find domains with retrieved_percentage > 5% not yet in list_brands
```

---

## Phase 3 — Competitor curation (mutation)

### 3a. Add real competitors

Batch-call in parallel:

```
mcp__peec-ai__create_brand(
  project_id,
  name="<Human name or brand>",
  domains=["their-domain.de"],
  aliases=["Alternate Spelling"]   # Umlaut ↔ ASCII variants, abbreviations
)
```

Categories to include:
- **Direct positioning overlap** (e.g. KI-SEO, GEO, Neuro-SEO freelancers)
- **Niche-specific freelancers** (E-commerce / Shopify SEO)
- **Local competitors** (same city / region)
- **Micro-agencies** (5–20 person KI / GEO specialists)
- **Invisible competitors** already appearing in the domain report

### 3b. Remove irrelevant competitors

For solo freelancer / service-business projects, remove SaaS tool brands:

```
mcp__peec-ai__delete_brand(project_id, brand_id)
```

Tool brands to remove: SEMrush, Ahrefs, Sistrix, Moz, Ryte, Yoast, Screaming Frog, SurferSEO, Frase, SE Ranking.

Deletion is soft. Also save a feedback memory noting "track humans only" so future sessions don't re-suggest these.

---

## Phase 4 — Keyword & intent analysis (Visibly AI + GSC)

### 4a. Verify GSC connection
```
mcp__visiblyai__get_google_connections()
  → confirm domain has a gsc_property and (ideally) a GA4 pairing
```

### 4b. Pull GSC keywords
```
mcp__visiblyai__get_keywords(domain="example.com", limit=200, location="Germany")
# or for finer control:
mcp__visiblyai__query_search_console(dimension="query", days=28, country="deu", limit=500)
```

### 4c. Classify intent

Cluster keywords into:
- **Informational (TOFU)** — "was ist", "wie funktioniert", "<tool> ohne anmeldung", ratgeber queries
- **Brand** — client brand name + variations
- **Commercial (MOFU)** — "beste", "vergleich", "Agentur vs Freelancer"
- **Transactional (BOFU)** — "Kosten", "Preis", "buchen", "kontaktieren", "<service> + <location>"

**Frequent pattern:** domain ranks well for TOFU informational (blog traffic) but is invisible for commercial / transactional — those are exactly the queries Peec prompts should test.

### 4d. Map GSC keywords → Peec prompts

For each top GSC keyword: does a Peec prompt exist that tests AI visibility for the same intent? If not, flag as "prompt gap".

---

## Phase 5 — Forum pain-point mining

Mine **verbatim buyer pain** from public forums → convert into Peec prompts that match real customer language (not sanitized marketing phrasing). These prompts also reveal what LLMs pull from UGC, and whether the brand surfaces in those answers.

### 5a. Sources

**German (priority for DACH):**
- Reddit DE — `r/de`, `r/Finanzen`, `r/kmu`, `r/selbststaendig`, `r/Unternehmer`; niche: `r/shopify`, `r/ecommerce`, `r/SEO`
- Gutefrage.net — broadest DE consumer Q&A; strong for commercial / transactional pain
- t3n forum (`t3n.de/forum`) — DACH digital / business pros
- OMR forum (`omr.com/de/forum`) — marketing / SEO operator pain
- gründerszene comments / deutsche-startups — B2B startup pain

**Global / EN fallback:**
- Reddit: `r/SEO`, `r/localseo`, `r/ecommerce`, `r/shopify`, `r/smallbusiness`, `r/entrepreneur`
- Quora
- Stack Exchange (Webmasters, Freelancing) for technical pain

**Video / social UGC (via WebFetch):**
- YouTube comment sections under competitor videos surfaced in the domain report
- LinkedIn post comments on competitor pulse articles (from `get_actions`)

### 5b. Query patterns

Run in parallel — different pain angles:

```
WebSearch("site:reddit.com <offer-keyword> <problem-word>")
# problem-words: "funktioniert nicht", "erfahrungen", "lohnt sich", "hilfe", "enttäuscht"
WebSearch("site:gutefrage.net <offer-keyword>")
WebSearch("site:t3n.de/forum <niche-keyword>")
WebSearch("site:omr.com <niche-keyword> frage")
WebSearch("<offer-keyword> erfahrungen forum")
WebSearch("<competitor-name> review reddit")
```

Example for a DACH SEO-retainer project:
- `site:reddit.com SEO Freelancer erfahrungen`
- `site:gutefrage.net SEO Berater lohnt sich`
- `"Shopify SEO" "funktioniert nicht" forum`
- `"KI SEO" reddit erfahrung`

### 5c. Extract threads

```
WebFetch(url, "Extract the original question verbatim, plus the 3 most upvoted answers.
              Note frustrations, decision triggers, and brand / competitor mentions.")
```

Signals to capture:
- **Verbatim question wording** — the buyer's natural language
- **Frustration markers** — "habe schon X ausprobiert", "keine Ergebnisse", "zu teuer", "bin überfordert"
- **Decision triggers** — "was kostet X?", "wie lange dauert Y?", "reicht selbst machen?", "brauche ich Z?"
- **Competitor mentions** — names, domains, verdicts
- **Thread recency** — prioritize last 12 months; older threads ≠ current AI training signal

### 5d. Convert pain → Peec prompts

Rules:
1. **Keep the buyer's language.** "Lohnt sich ein SEO-Berater überhaupt?" stays — do not polish to "Welcher Nutzen bietet SEO-Beratung?"
2. **Map to funnel stage** by intent:
   - "Was ist / wie funktioniert / bin ich zu spät" → Awareness
   - "Freelancer vs Agentur / beste Option / welcher lohnt sich" → Consideration
   - "Was kostet / kann ich buchen / wen kontaktieren" → Decision
   - "Erfahrungen mit X / Fallstudien / funktioniert das wirklich" → Retention
3. **Reject pure curiosity.** "Was ist KI?" without buying path is out.
4. **Business-model fit.** Ask: would a buyer asking this become a retainer / one-shot / product buyer? If no, reject.
5. **≤200 chars** (Peec limit) — tighten without losing the pain.

### 5e. Tag for traceability

When creating the prompt in Phase 7, also tag with **`from-forum`** (create once: `create_tag(name="from-forum", color="slate")`). Later you can filter reports to `tag_id=from-forum` and measure whether pain-point prompts outperform generic ones.

### 5f. Example transformations

| Raw forum query (verbatim) | Peec prompt | Funnel | Tags |
|---|---|---|---|
| "Lohnt sich ein SEO-Freelancer für kleine Shopify-Shops überhaupt?" (Gutefrage) | Lohnt sich ein SEO-Freelancer für kleine Shopify-Shops überhaupt? | Consideration | shopify, e-commerce, from-forum |
| "Habe schon 3 Agenturen durch, keine Ergebnisse – was jetzt?" (r/selbststaendig) | Was tun, wenn drei SEO-Agenturen keine Ergebnisse geliefert haben? | Decision | retainer, coach, from-forum |
| "Wie viel SEO kann man selbst machen, bevor man jemanden holt?" (gutefrage) | Wie viel SEO können KMU-Betreiber selbst machen, bevor ein Berater sinnvoll ist? | Awareness | coach, from-forum |
| "SEO für Shopify mit ChatGPT – reicht das?" (r/shopify) | Reicht SEO für Shopify mit ChatGPT ohne zusätzlichen Berater aus? | Awareness | shopify, ai-seo, from-forum |
| "Bin ich 2026 noch nicht zu spät für SEO?" (r/de) | Ist es 2026 noch sinnvoll, mit SEO zu starten? | Awareness | from-forum |

### 5g. Secondary use

Extracted pain points are also **content topics** — feed them to the client for blog posts / LinkedIn pulses / YouTube scripts. Answering the pain in owned content is the fastest way to **win** the corresponding Peec prompt in 6–12 weeks.

---

## Phase 6 — Customer-journey prompt design

4 funnel stages:

| Stage | Intent | Typical shape | Example |
|---|---|---|---|
| **Awareness** | educate on category | "Was ist X?", "Wie funktioniert Y?", "Warum wird Z wichtiger?" | Was ist Neuro-SEO? |
| **Consideration** | compare options | "Beste X", "Vergleiche Y", "X oder Y – was lohnt sich?" | Beste SEO-Freelancer E-Commerce |
| **Decision** | ready to book | "Wer ist <brand>?", "Was kostet X?", "<service> gesucht" | Was kostet eine monatliche SEO-Retainer-Beratung? |
| **Retention** | trust / proof | "Fallstudien", "Erfahrungen mit <brand>", "Wer veröffentlicht X?" | Erfahrungen mit <brand> Neuro-SEO System |

**Target 5 prompts per stage = 20 total.** Below this, per-stage SoV tracking is too noisy.

### Prompt quality criteria

A retainer-worthy prompt:
- Asks for **exactly what the client sells** (offer keywords: "Retainer", "monatlich", "System", "laufend")
- Is **MOFU → BOFU intent** for Decision prompts (no vague "what is")
- Has **competitor weakness built in** (tool brands can't answer consultative queries; agencies lose on "persönlich" / "coach"; generalists lose on the client's unique category)
- German for DE market; language-match for other regions
- ≤200 chars

### Pick the hero prompt

Identify ONE prompt that:
1. Matches the offer verbatim
2. Is BOFU intent
3. Has competitor weakness (tool brands, agencies, or generalists fail it)
4. Uses the client's differentiator keywords

This is the hero prompt — track weekly.

---

## Phase 7 — Prompt creation

Batch in parallel:

```
mcp__peec-ai__create_prompt(
  project_id,
  text="...",
  country_code="DE",
  topic_id=<funnel-stage-topic-id>
)
```

Created prompts have `topic_id` but no tags — tagging happens in Phase 8.

**Credit caution:** Each prompt burns daily run credits on Peec TRIAL. For >20, create in waves and review coverage after 48h.

---

## Phase 8 — Taxonomy setup (topics + tags)

### 8a. Topics = funnel stages

Create 4 topics:

```
mcp__peec-ai__create_topic(project_id, name="Awareness",     country_code="DE")
mcp__peec-ai__create_topic(project_id, name="Consideration", country_code="DE")
mcp__peec-ai__create_topic(project_id, name="Decision",      country_code="DE")
mcp__peec-ai__create_topic(project_id, name="Retention",     country_code="DE")
```

If the project had theme-based topics (AI, SEO): **rebuild** — move each prompt to its funnel topic via `update_prompt`, then `delete_topic` the obsolete ones.

### 8b. Tags = intent + theme

Keep Peec's **standard intent tags**: branded, non-branded, informational, transactional.

Add theme tags reflecting the offer:

```
mcp__peec-ai__create_tag(project_id, name="retainer",    color="orange")
mcp__peec-ai__create_tag(project_id, name="e-commerce",  color="purple")
mcp__peec-ai__create_tag(project_id, name="shopify",     color="green")
mcp__peec-ai__create_tag(project_id, name="ai-seo",      color="cyan")
mcp__peec-ai__create_tag(project_id, name="neuro-seo",   color="fuchsia")  # client's proprietary term
mcp__peec-ai__create_tag(project_id, name="coach",       color="teal")
mcp__peec-ai__create_tag(project_id, name="local",       color="yellow")
mcp__peec-ai__create_tag(project_id, name="brand-<name>",color="rose")
mcp__peec-ai__create_tag(project_id, name="from-forum",  color="slate")    # Phase 5 traceability
```

### 8c. Assign every prompt

```
mcp__peec-ai__update_prompt(
  project_id, prompt_id,
  topic_id=<funnel stage>,
  tag_ids=[
    <intent>,         # transactional OR informational
    <branding>,       # branded OR non-branded
    <theme1>, <theme2>, ...
  ]
)
```

Default mapping:
- Awareness → informational + non-branded
- Consideration → transactional + non-branded (unless explicit brand-Y comparison)
- Decision → transactional + (branded if client brand named, else non-branded)
- Retention → informational / transactional + branded for "Erfahrungen mit <brand>"

### 8d. Clean up

After every prompt has been moved:
```
mcp__peec-ai__delete_topic(project_id, old_topic_id)
```

---

## Phase 9 — Reporting & actions

Wait ~24h after setup. Then:

### Funnel visibility
```
mcp__peec-ai__get_brand_report(
  project_id, start_date, end_date,
  dimensions=["topic_id"],
  filters=[{field: "brand_id", operator: "in", values: [own_brand_id]}]
)
```

Usually exposes the weakest funnel stage — often Awareness if the category is client-invented, or Decision if brand discovery is poor.

### Hero prompt tracking
```
mcp__peec-ai__get_brand_report(
  project_id, start_date, end_date,
  filters=[{field: "prompt_id", operator: "in", values: [<hero_prompt_id>]}],
  dimensions=["model_id"]
)
```

### Theme SoV
```
mcp__peec-ai__get_brand_report(
  project_id, start_date, end_date,
  filters=[{field: "tag_id", operator: "in", values: [<retainer_tag_id>]}],
  dimensions=["brand_id"]
)
```

### Opportunity actions
```
mcp__peec-ai__get_actions(project_id, scope="overview",  start_date, end_date)   # top 3 rows
mcp__peec-ai__get_actions(project_id, scope="editorial", url_classification="ARTICLE", ...)
mcp__peec-ai__get_actions(project_id, scope="ugc", domain="youtube.com", ...)
# also try reddit.com, linkedin.com
```

Deliver as concrete outreach list + content-format guidance from the actions' `text` column.

### Persist setup state (mandatory final step)

Before the deliverable summary, write the state file per [`_shared/SETUP_STATE.md`](../_shared/SETUP_STATE.md):

```
1. Read <project>/growth_loop/setup_state.json (if present).
2. Merge:
     phases_completed    = union(old, phases actually run this session)
     snapshot            = fresh counts from list_brands/list_prompts/list_topics/list_tags
                           called moments ago in this phase
     completed_at        = keep old if present, else now (UTC ISO8601)
     last_audit_at       = now ONLY if this run was mode=audit
     hero_prompt_id      = the one selected in Phase 9
     peec_project_id, domain = from session context
     target_country      = from input (resolved per "Resolving language/country" rules)
     prompt_language     = from input
     secondary_languages = from input (default [])
     setup_version       = "1.1"
3. Write atomically: write to setup_state.json.tmp, then rename.
4. Print exactly one line in the run summary:
     "State written: <project>/growth_loop/setup_state.json (phases: X/7)"
```

If `<project>/growth_loop/` does not exist, create it (this is the same directory the orchestrator and reporter use).

---

## Deliverable structure

At the end of a full setup, present:

1. **Before / after table** — brand count, prompt count, topics, tags (then vs now)
2. **Funnel distribution** — e.g. 5/5/5/5
3. **Hero prompt callout** — which single prompt to win first, and why
4. **Refresh timeline** — "rerun brand / domain reports in 48h"
5. **Categorized backlog** (below)
6. **Memory hygiene** — save preferences uncovered (e.g. "never track tool brands") to feedback memory

---

## Executable backlog template

Every setup ends with a **categorized task list** the client / user can run in the next 2 weeks. 7 categories. Each task = one line, prefixed with priority (P0 / P1 / P2) and effort (S / M / L).

### 1. Content — owned domain
- **P0** — transactional hero page for the offer ("<offer> Retainer") with pricing bands, FAQ schema, CTAs
- **P0** — category pillar page for the client's unique term ("Was ist Neuro-SEO?") → targets Awareness
- **P1** — case-study page per niche (Shopify / B2B / Local) → targets Retention
- **P1** — comparison page ("Freelancer vs Agentur für <niche>") → targets Consideration
- **P2** — glossary / FAQ hub covering pain points from Phase 5

### 2. Editorial outreach
- **P0** — pitch inclusion in high-opportunity editorial articles surfaced by `get_actions` (scope=editorial): evergreen.media, OMR, t3n, niche fachportal
- **P1** — 1 guest article per quarter on competitor-cited domains
- **P2** — get quoted in roundup / listicle ("Top N <role> in Deutschland")

### 3. UGC / community
- **P0** — presence in Reddit subs from Phase 5 (r/selbststaendig, r/SEO, r/ecommerce, niche-specific) — 1 thread / week with non-spammy branded answers
- **P0** — answer top-pain questions on Gutefrage
- **P1** — 1 LinkedIn Pulse / month in the format `get_actions` recommends
- **P1** — YouTube content matching the format of the already-cited competitor channel
- **P2** — OMR / t3n forum — 1 high-signal reply / month

### 4. Technical SEO / schema
- **P1** — Person + Organization + Service Schema.org on homepage + offer pages
- **P1** — FAQPage schema on pillar pages (use mined forum pain as Q&A items)
- **P2** — Review / Rating schema if testimonials exist
- **P2** — breadcrumbs + internal linking aligned to pillar architecture

### 5. Peec AI operations (maintenance)
- **P0** — weekly review of the hero prompt's visibility curve per engine
- **P1** — monthly: new competitors from `get_chat` → `create_brand`
- **P1** — quarterly: grow from 20 → 50 prompts (add new mined pain points)
- **P2** — `/schedule` trigger for weekly auto-run of brand + domain reports

### 6. Data ops / analytics
- **P1** — connect Visibly AI to the domain's GSC + GA4 if not already (`get_google_connections`)
- **P1** — monthly: are commercial-intent GSC queries rising (CTR + impressions for offer keywords)?
- **P2** — cross-reference: does Peec SoV lift correlate with GA4 lead volume lift? Tag leads with "source: AI engine"

### 7. Positioning / brand
- **P0** — ensure homepage + offer pages contain the **exact offer language** tested in Decision prompts (retainer, monatlich, System, laufend, Neuro-SEO). LLMs can't recommend terminology that isn't on the site.
- **P1** — 1 "defining" piece of content per quarter owning the client's category (white paper, podcast series, framework diagram)
- **P2** — 1–2 industry events per year; ensure talk abstracts land in event archives (AI-scrapable)

### Output format

Present as a sortable table, paste-ready for Notion / Linear:

```
| # | Priority | Effort | Category | Task | Owner | Due |
|---|----------|--------|----------|------|-------|-----|
| 1 | P0 | M | Content | Build "Neuro-SEO Retainer" landing page with pricing + FAQ schema | Antonio | 2026-05-10 |
| 2 | P0 | S | UGC     | Answer top r/selbststaendig thread on "SEO-Freelancer erfahrungen" | Antonio | 2026-04-26 |
...
```

Always ≥5 P0 tasks across ≥3 categories. The backlog is only useful if it's executable within 2 weeks.

---

## Customer journey prompt library (reusable starters)

These templates work for most DACH service-business projects. The skeletons stay German because that IS the buyer language being tested — translating to English would break the semantic value. Adapt domain-specific nouns.

### Awareness
1. Was ist <category> und wie unterscheidet es sich von <alternative>?
2. Wie optimiere ich <outcome> für ChatGPT- und Perplexity-Empfehlungen?
3. Warum reicht klassisches <category> für <audience> 2026 nicht mehr aus?
4. Welche <principle> steigern <KPI> im <niche>?
5. Was bringt langfristige <service> im Vergleich zu einmaligen <alternative>?

### Consideration
6. Beste <role> in Deutschland für <niche>.
7. Freelancer oder Agentur für laufende <service> – was lohnt sich?
8. **[hero candidate]** Welcher <role> kombiniert <differentiator-A> mit <differentiator-B> als monatliches Retainer-Modell?
9. Beste <role> für <platform> in der DACH-Region.
10. Welche deutschen <role> bieten monatliche Betreuung inklusive Reporting?

### Decision
11. Wer ist <BRAND> und welche <service> bietet <er/sie> an?
12. Was kostet eine monatliche <service> bei einem <role> in Deutschland?
13. Welcher <role> bietet <differentiator> als laufendes System an?
14. <role> für <audience> in Deutschland gesucht – wen kontaktieren?
15. Brauche einen persönlichen <role> und keinen Agentur-Vertrieb – wen empfehlt ihr?

### Retention
16. Welche <role> in Deutschland haben nachweisbare <niche>-Fallstudien?
17. Welche Erfahrungen haben Kunden mit <BRAND> und dem <proprietary-system> gemacht?
18. Welche deutschen <role> sind für ihre <niche>-Publikationen bekannt?
19. Welcher <role> hat messbare Ergebnisse bei <platform>-Shops erzielt?
20. Welche <role> veröffentlichen regelmäßig Fallstudien und Ergebnisse?

---

## Quick reference

| Goal | Tool |
|---|---|
| All projects | `mcp__peec-ai__list_projects` |
| Current competitors | `mcp__peec-ai__list_brands` |
| Prompts + tags + topics | `mcp__peec-ai__list_prompts` |
| Inspect an AI response | `mcp__peec-ai__list_chats` → `get_chat` |
| Find invisible competitors | `mcp__peec-ai__get_domain_report` |
| Gap URLs (competitor-only) | `get_domain_report(filters: gap > 0)` |
| Add competitor | `mcp__peec-ai__create_brand` |
| Remove competitor | `mcp__peec-ai__delete_brand` |
| Add prompt | `mcp__peec-ai__create_prompt` |
| Reassign topic / tags | `mcp__peec-ai__update_prompt` |
| Recommendations | `mcp__peec-ai__get_actions` (overview → owned / editorial / ugc) |
| Pull GSC keywords | `mcp__visiblyai__get_keywords` or `query_search_console` |
| Check GSC / GA4 | `mcp__visiblyai__get_google_connections` |
| Forum pain | `WebSearch("site:reddit.com ...")`, `WebSearch("site:gutefrage.net ...")` |
| Extract thread | `WebFetch(url, "...")` |

---

## Guardrails (do not do these)

- Do not track SaaS tool brands as competitors for service-business projects — they aren't buyer alternatives and distort SoV
- Do not create more than 20 prompts at once on TRIAL — credit burn; scale in waves, review after 48h
- Do not exceed 200 chars per prompt — Peec's hard limit
- Do not mix theme + funnel in topics — topics hold one value; use topics for the primary slicing (funnel stage), tags for secondary (theme)
- Do not skip `aliases` on `create_brand` — names with Umlauts need ASCII aliases ("Stürkat" + "Stuerkat"), otherwise matching fails
- Do not request reports before 24h of history — prompt runs happen daily; fresh prompts / brands won't appear yet
- Do not delete old topics before moving prompts — prompts become detached; always `update_prompt` first, then `delete_topic`
- Do not translate mined buyer language to marketing-speak — "Lohnt sich das?" ≠ "Welcher Nutzen besteht?"; the whole skill depends on verbatim buyer phrasing
