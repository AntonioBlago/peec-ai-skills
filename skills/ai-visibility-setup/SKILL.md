---
name: ai-visibility-setup
description: End-to-end Peec AI project setup — competitor discovery, customer-journey prompt design, topic/tag taxonomy, GSC-based keyword mapping, forum pain-point mining (Reddit, Gutefrage, t3n, OMR), reporting. Use when the user wants to set up, restructure, or audit a Peec AI project for their own brand or a client. Covers the full funnel (Awareness → Consideration → Decision → Retention) and ensures competitors, prompts, and tags reflect the actual offer and real buyer language.
user-invocable: true
---

# AI Visibility Setup — Peec AI Workflow

Complete workflow for setting up or restructuring a Peec AI project so that brand visibility, competitor comparisons, and prompt coverage actually match the client's offer. Combines Peec MCP, Visibly AI (GSC/GA4), and web research.

**When to trigger:**
- "Set up Peec for [client]"
- "My Peec competitors are wrong / not real competitors"
- "Design prompts for my customer journey"
- "Map GSC keywords to my Peec prompts"
- "Restructure Peec topics/tags"
- Any audit of existing AI visibility tracking.

**Prerequisites:**
- Peec AI MCP connected (`mcp__peec-ai__*` tools)
- Visibly AI MCP connected (`mcp__visiblyai__*`) — only for GSC data, optional
- GSC + GA4 connected inside Visibly AI (check with `get_google_connections`)

---

## Phase 1 — Initial Audit (state of play)

Run these in parallel:

```
mcp__peec-ai__list_projects                          → pick project_id
mcp__peec-ai__list_brands(project_id)                → current competitors
mcp__peec-ai__list_prompts(project_id, limit=200)    → current prompts + tag_ids + topic_id
mcp__peec-ai__list_topics(project_id)                → current topic taxonomy
mcp__peec-ai__list_tags(project_id)                  → current tag taxonomy
```

**Red flags to call out:**
- Competitors list contains **SaaS tool brands** (SEMrush, Ahrefs, Sistrix, Moz, Ryte, Yoast, Screaming Frog, SurferSEO, Frase). If the client is a freelancer/consultant, these distort SoV and visibility — they aren't business competitors.
- Prompts clustered only in one funnel stage (e.g. all MOFU "empfiehl" — no Awareness/Decision/Retention coverage).
- Topics = theme only (e.g. "AI" / "SEO") → can't track funnel performance.
- Tags = only Peec's default 4 (branded/non-branded/informational/transactional) → no offer-specific slicing possible.

---

## Phase 2 — Competitor Discovery (ground truth)

### 2a. Extract from AI chats (authoritative)

For each **losing prompt** (where the own brand has 0% visibility but competitors are present), pull actual chats:

```
mcp__peec-ai__list_chats(project_id, start_date, end_date, prompt_id=<losing_prompt>)
  → pick 1 chat per engine (chatgpt-scraper, perplexity-scraper, google-ai-overview-scraper)
mcp__peec-ai__get_chat(project_id, chat_id)
  → inspect messages[] for freelancer/consultant names; inspect sources[] for their domains
```

Extract: human names, domain names, and the sources the AI pulled. These are the **real** competitors LLMs recommend against you.

### 2b. Supplement with web research

```
WebSearch: "SEO Freelancer Deutschland [niche] 2026"
WebSearch: "[niche] Freelancer Experte KI ChatGPT empfehlen"
```

Cross-check with the domain report — any domain already retrieving (`get_domain_report`) but not tracked as a brand is an **invisible competitor**:

```
mcp__peec-ai__get_domain_report(project_id, start_date, end_date, limit=25)
  → find domains with retrieved_percentage > 5% not yet in list_brands output
```

---

## Phase 3 — Competitor Curation (mutation)

### 3a. Add real competitors

For each discovered freelancer/agency/brand, batch-call in parallel:

```
mcp__peec-ai__create_brand(
  project_id,
  name: "Human Name or Brand",
  domains: ["their-domain.de"],
  aliases: ["Alternate Spelling"]  // Umlaut ↔ ASCII variants, alias abbreviations
)
```

Categories to include:
- **Direct positioning overlap** (e.g. KI-SEO, GEO, Neuro-SEO freelancers)
- **Niche-specific freelancers** (e.g. E-Commerce/Shopify SEO)
- **Local competitors** (same city/region)
- **Micro-agencies** (5-20 person KI/GEO specialists)
- **Invisible competitors** already appearing in the domain report

### 3b. Remove irrelevant competitors

If the project is for a **solo freelancer** or **service business**, remove SaaS tool brands — they aren't buyers' alternatives:

```
mcp__peec-ai__delete_brand(project_id, brand_id)
```

Tool brands to remove for a freelancer project: SEMrush, Ahrefs, Sistrix, Moz, Ryte, Yoast, Screaming Frog, SurferSEO, Frase, SE Ranking.

**Note:** Deletion is soft. Also save a feedback memory noting the user's preference to track humans only (so future sessions don't re-suggest these).

---

## Phase 4 — Keyword & Intent Analysis (Visibly AI + GSC)

### 4a. Verify GSC connection

```
mcp__visiblyai__get_google_connections()
  → confirm the domain has a gsc_property and (ideally) a GA4 pairing
```

### 4b. Pull GSC keywords

```
mcp__visiblyai__get_keywords(domain="example.com", limit=200, location="Germany")
  → returns real click data, CTR, impressions, avg. position
```

Alternative: `mcp__visiblyai__query_search_console(dimension="query", days=28, country="deu", limit=500)` for finer control.

### 4c. Classify intent gap

Cluster keywords into:
- **Informational (TOFU)** — "was ist", "wie funktioniert", "claude ohne anmeldung", ratgeber queries
- **Brand** — client brand name + variations
- **Commercial (MOFU)** — "beste", "vergleich", "Agentur vs Freelancer"
- **Transactional (BOFU)** — "Kosten", "Preis", "buchen", "kontaktieren", "[service] + [location]"

**Frequent pattern:** the domain ranks well for **TOFU informational** queries (blog-driven traffic) but invisible for **commercial/transactional** queries — those are exactly the queries Peec prompts should test.

### 4d. Map GSC keywords → Peec prompts

For each top GSC keyword:
- Does a Peec prompt exist that tests AI visibility for the same intent?
- If not → flag as "prompt gap".

---

## Phase 5 — Pain Point Research (Reddit, Gutefrage, Foren)

Mine **verbatim buyer pain points** from public forums to turn them into Peec prompts that match real customer language (not sanitized marketing phrasing). These prompts also reveal what LLMs are pulling from forum UGC — and whether the client's brand surfaces in answers.

### 5a. Source forums

**German-language (priority for DACH clients):**
- **Reddit DE** — `r/de`, `r/Finanzen`, `r/kmu`, `r/selbststaendig`, `r/Unternehmer`, plus niche: `r/shopify`, `r/ecommerce`, `r/SEO`
- **Gutefrage.net** — broadest consumer-intent DE Q&A; strong for commercial/transactional pain
- **t3n forum** (`t3n.de/forum`) — DACH digital/business pros
- **OMR forum** (`omr.com/de/forum`) — marketing/SEO operator pains
- **gründerszene** comments / **deutsche-startups** — startup-side B2B pain

**Global / EN fallback:**
- Reddit: `r/SEO`, `r/localseo`, `r/ecommerce`, `r/shopify`, `r/smallbusiness`, `r/entrepreneur`, niche subs per industry
- Quora (`quora.com`)
- Stack Exchange (Webmasters, Freelancing) for technical pains

**Video/social UGC (use WebFetch):**
- YouTube comment sections on **competitor** videos (already surfaced in Peec's domain report as high-retrieval — e.g. Farbentour Online Marketing GmbH)
- LinkedIn post comments on competitor articles (e.g. the pulse article Peec's `get_actions` recommends)

### 5b. Query patterns

Run these in parallel — each returns different pain angles:

```
WebSearch("site:reddit.com [offer-keyword] [problem-word]")
  // problem-words: "funktioniert nicht", "erfahrungen", "lohnt sich", "hilfe", "enttäuscht"
WebSearch("site:gutefrage.net [offer-keyword]")
WebSearch("site:t3n.de/forum [niche-keyword]")
WebSearch("site:omr.com [niche-keyword] frage")
WebSearch("[offer-keyword] erfahrungen forum")
WebSearch("[competitor-name] review reddit")
```

For a DACH SEO-retainer project, example queries:
- `site:reddit.com SEO Freelancer erfahrungen`
- `site:gutefrage.net SEO Berater lohnt sich`
- `"Shopify SEO" "funktioniert nicht" forum`
- `"KI SEO" reddit erfahrung`

### 5c. Extract & inspect threads

For each promising hit:

```
WebFetch(url, "Extract the original question verbatim, plus the 3 most upvoted answers. Note frustrations, decision triggers, and brand/competitor mentions.")
```

Pay attention to:
- **Verbatim question wording** — buyer's natural language
- **Frustration markers** — "habe schon X ausprobiert", "keine Ergebnisse", "zu teuer", "bin überfordert"
- **Decision triggers** — "was kostet X?", "wie lange dauert Y?", "reicht selbst machen?", "brauche ich Z?"
- **Competitor mentions** — names, domains, verdicts (positive/negative)
- **Thread recency** — prioritize threads from the last 12 months; older threads ≠ current AI training signal

### 5d. Convert pain points → Peec prompts

Rules:
1. **Keep the buyer's language** — do NOT rewrite to marketing-speak. "Lohnt sich ein SEO-Berater überhaupt?" stays; don't polish to "Welcher Nutzen bietet SEO-Beratung?"
2. **Map to funnel stage** by intent:
   - "Was ist / wie funktioniert / bin ich zu spät" → Awareness
   - "Freelancer vs Agentur / beste Option / welcher lohnt sich" → Consideration
   - "Was kostet / kann ich buchen / wen kontaktieren" → Decision
   - "Erfahrungen mit X / Fallstudien / funktioniert das wirklich" → Retention
3. **Reject pure curiosity** — "Was ist KI?" without buying path. Only keep queries that plausibly lead to your offer.
4. **Filter by business-model fit** — ask "would a buyer asking this become a retainer client / a one-shot client / product buyer?" If none → reject.
5. **Max 200 chars** — tighten without losing the pain.

### 5e. Tag for traceability

When creating the prompt in Phase 7, also tag with a **`from-forum`** tag (create once: `create_tag(name="from-forum", color="slate")`). This lets you later filter reports to `tag_id=from-forum` and measure whether pain-point prompts outperform generic ones.

### 5f. Example transformations

| Raw forum query (verbatim) | Peec prompt | Funnel | Tags |
|---|---|---|---|
| "Lohnt sich ein SEO-Freelancer für kleine Shopify-Shops überhaupt?" (Gutefrage) | Lohnt sich ein SEO-Freelancer für kleine Shopify-Shops überhaupt? | Consideration | shopify, e-commerce, from-forum |
| "Habe schon 3 Agenturen durch, keine Ergebnisse – was jetzt?" (r/selbststaendig) | Was tun, wenn drei SEO-Agenturen keine Ergebnisse geliefert haben? | Decision | retainer, coach, from-forum |
| "Wie viel SEO kann man selbst machen, bevor man jemanden holt?" (gutefrage) | Wie viel SEO können KMU-Betreiber selbst machen, bevor ein Berater sinnvoll ist? | Awareness | coach, from-forum |
| "SEO für Shopify mit ChatGPT – reicht das?" (r/shopify) | Reicht SEO für Shopify mit ChatGPT ohne zusätzlichen Berater aus? | Awareness | shopify, ai-seo, from-forum |
| "Bin ich 2026 noch nicht zu spät für SEO?" (r/de) | Ist es 2026 noch sinnvoll, mit SEO zu starten? | Awareness | from-forum |

### 5g. Secondary use: content briefing

The extracted pain points are also **content topics** — feed them to the client for blog posts / LinkedIn pulses / YouTube scripts. Answering the pain point in owned content is the fastest way to **win** the corresponding Peec prompt in 6-12 weeks.

---

## Phase 6 — Customer Journey Prompt Design

Organize prompts across **4 funnel stages**:

| Stage | Intent | Typical prompt shape | Example |
|---|---|---|---|
| 🟢 **Awareness** | Educate on category | "Was ist X?", "Wie funktioniert Y?", "Warum wird Z wichtiger?" | Was ist Neuro-SEO? |
| 🟡 **Consideration** | Compare options | "Beste X", "Vergleiche Y", "X oder Y – was lohnt sich?" | Beste SEO-Freelancer E-Commerce |
| 🔴 **Decision** | Ready to book | "Wer ist [Brand]?", "Was kostet X?", "[Service] gesucht" | Was kostet eine monatliche SEO-Retainer-Beratung? |
| 🟣 **Retention** | Trust / proof | "Fallstudien", "Erfahrungen mit [Brand]", "Wer veröffentlicht X?" | Erfahrungen mit [Brand] Neuro-SEO System |

**Targeting 5 prompts per stage = 20 total** is the proven minimum for meaningful SoV tracking per stage.

### Prompt quality criteria

A retainer-worthy prompt:
- Asks for **exactly what the client sells** (incorporate offer keywords: "Retainer", "monatlich", "System", "laufend")
- Is **MOFU→BOFU intent** for decision prompts (not vague "what is")
- Has **competitor weakness built in** (e.g. tool brands can't answer consultative queries; agencies lose on "persönlich"/"coach"; most competitors lose on the client's unique category)
- German-language for DE market; language-match for other regions
- < 200 chars (Peec limit)

### ⭐ Pick the single most important prompt

For any project, identify ONE prompt that:
1. Matches the offer verbatim
2. Is BOFU-intent (buyer is near purchase)
3. Has competitor weakness (tool brands, agencies, or generalists fail it)
4. Uses the client's differentiator keywords

This is the **hero prompt** to win first — track it weekly.

---

## Phase 7 — Prompt Creation

Batch-create via parallel calls:

```
mcp__peec-ai__create_prompt(
  project_id,
  text: "...",
  country_code: "DE",
  topic_id: <funnel-stage-topic-id>
)
```

After creation, prompts have `topic_id` but no tags — tagging happens in Phase 7.

**Credit caution:** Each prompt consumes daily run credits on Peec's TRIAL plan. For large sets (>20), consider creating in waves and reviewing coverage after 48h.

---

## Phase 8 — Taxonomy Setup (topics + tags)

### 7a. Topics = Funnel Stages

Create 4 topics:

```
mcp__peec-ai__create_topic(project_id, name="Awareness", country_code="DE")
mcp__peec-ai__create_topic(project_id, name="Consideration", country_code="DE")
mcp__peec-ai__create_topic(project_id, name="Decision", country_code="DE")
mcp__peec-ai__create_topic(project_id, name="Retention", country_code="DE")
```

If the project already had theme-based topics (AI, SEO) — **rebuild**: move each prompt to its funnel topic via `update_prompt`, then `delete_topic` on the obsolete ones.

### 7b. Tags — intent + theme

Keep Peec's **standard 4 intent tags**: branded, non-branded, informational, transactional.

Add **theme tags** reflecting the offer:

```
mcp__peec-ai__create_tag(project_id, name="retainer", color="orange")
mcp__peec-ai__create_tag(project_id, name="e-commerce", color="purple")
mcp__peec-ai__create_tag(project_id, name="shopify", color="green")
mcp__peec-ai__create_tag(project_id, name="ai-seo", color="cyan")
mcp__peec-ai__create_tag(project_id, name="neuro-seo", color="fuchsia")   // or client's proprietary term
mcp__peec-ai__create_tag(project_id, name="coach", color="teal")
mcp__peec-ai__create_tag(project_id, name="local", color="yellow")
mcp__peec-ai__create_tag(project_id, name="brand-<name>", color="rose")
mcp__peec-ai__create_tag(project_id, name="from-forum", color="slate")       // Phase 5 pain-point traceability
```

### 7c. Assign every prompt

For each prompt:

```
mcp__peec-ai__update_prompt(
  project_id,
  prompt_id,
  topic_id: <funnel stage>,
  tag_ids: [
    <intent>,              // transactional OR informational
    <branding>,            // branded OR non-branded
    <theme1>, <theme2>...  // retainer, e-commerce, etc.
  ]
)
```

Rule of thumb:
- Awareness → informational + non-branded
- Consideration → transactional + non-branded (except explicit brand-Y comparisons)
- Decision → transactional + (branded if mentioning client brand, else non-branded)
- Retention → informational/transactional + branded for "Erfahrungen mit [Brand]"

### 7d. Clean up

Delete obsolete topics after all prompts have been moved:

```
mcp__peec-ai__delete_topic(project_id, old_topic_id)
```

---

## Phase 9 — Reporting & Actions

Wait ~24h after setup, then pull:

### Funnel visibility

```
mcp__peec-ai__get_brand_report(
  project_id,
  start_date, end_date,
  dimensions: ["topic_id"],
  filters: [{ field: "brand_id", operator: "in", values: [own_brand_id] }]
)
```

Expose which funnel stage is weakest (usually Awareness if the category is client-invented, or Decision if brand discovery is poor).

### Hero prompt tracking

```
mcp__peec-ai__get_brand_report(
  project_id, start_date, end_date,
  filters: [{ field: "prompt_id", operator: "in", values: [<hero_prompt_id>] }],
  dimensions: ["model_id"]
)
```

Track the single ⭐ prompt's visibility per engine — this is the KPI to move.

### Theme SoV

```
mcp__peec-ai__get_brand_report(
  project_id, start_date, end_date,
  filters: [{ field: "tag_id", operator: "in", values: [<retainer_tag_id>] }],
  dimensions: ["brand_id"]
)
```

### Opportunity actions

```
mcp__peec-ai__get_actions(project_id, scope="overview", start_date, end_date)
  → pick top 3 opportunity rows
mcp__peec-ai__get_actions(project_id, scope="editorial", url_classification="ARTICLE", ...)
mcp__peec-ai__get_actions(project_id, scope="ugc", domain="youtube.com", ...)
  // also try reddit.com, linkedin.com
```

Deliver concrete outreach list + content-format guidance from actions' `text` column.

---

## Deliverable Structure

At the end of a full setup, present:

1. **Before/After table** — brand count, prompt count, topics, tags (then vs now)
2. **Funnel prompt distribution** — 5/5/5/5 (or the actual numbers)
3. **Hero prompt callout** — which single prompt to win first, and why
4. **Refresh timeline** — "Rerun brand/domain reports in 48h"
5. **ToDo / Improvement Backlog** — categorized task list (see next section)
6. **Memory hygiene** — save any user preferences uncovered (e.g. "never track tool brands as competitors") to feedback memory

---

## ToDo / Improvement Backlog — Categorized Template

Every setup should end with a concrete, categorized task list the client/user can execute. Structure output as seven categories. Each task = one line, prefixed with priority (P0 / P1 / P2) and estimated effort (S / M / L).

### 1. Content — Own Domain (pillar + offer pages)
- **P0** — Create / optimize a **transactional hero page** for the offer (e.g. "[Offer] Retainer") with pricing bands, FAQ schema, CTAs
- **P0** — Build a **category pillar page** for the client's unique term (e.g. "Was ist Neuro-SEO?") — targets Awareness prompts
- **P1** — Case-study page per niche (Shopify / B2B / Local) — targets Retention prompts
- **P1** — Comparison page ("Freelancer vs Agentur für [niche]") — targets Consideration
- **P2** — Glossary / FAQ hub covering pain points mined in Phase 5

### 2. Editorial Outreach (third-party authority)
- **P0** — Pitch inclusion into high-opportunity editorial articles surfaced by `get_actions` (scope=editorial). Example: evergreen.media, OMR, t3n, fachportal of the niche
- **P1** — Publish 1 guest article per quarter on competitor-cited domains
- **P2** — Get quoted in roundup / listicle articles ("Top N [role] in Deutschland")

### 3. UGC / Community Presence
- **P0** — Establish presence in **Reddit** subs identified in Phase 5 (r/selbststaendig, r/SEO, r/ecommerce, niche-specific) — answer 1 thread/week with non-spammy, branded answers
- **P0** — Answer top-pain questions on **Gutefrage** referencing own expertise
- **P1** — Publish 1 LinkedIn **pulse article** per month in the format Peec's `get_actions` recommends
- **P1** — Produce YouTube content matching the format of the competitor channel already being cited
- **P2** — OMR forum / t3n forum — 1 high-signal reply per month

### 4. Technical SEO / Schema
- **P1** — Add **Person + Organization + Service** Schema.org to homepage and offer pages
- **P1** — Add **FAQPage** schema to pillar pages (using mined forum pain points as the Q&A items)
- **P2** — Add **Review/Rating** schema if the client has testimonials
- **P2** — Breadcrumbs + internal linking aligned to pillar architecture

### 5. Peec AI Operations (maintenance)
- **P0** — **Weekly review** of the hero prompt's visibility curve (per engine)
- **P1** — Monthly check: surface new competitors appearing in `get_chat` responses; add via `create_brand`
- **P1** — Quarterly: expand prompt count from 20 → 50 (add mined forum pain points as they emerge)
- **P2** — Set up `/schedule` trigger to auto-run brand + domain reports weekly

### 6. Data Ops / Analytics
- **P1** — Connect Visibly AI to the domain's GSC + GA4 (if not already — check with `get_google_connections`)
- **P1** — Monthly check: are commercial-intent GSC queries rising (CTR & impressions for offer keywords)?
- **P2** — Cross-reference: does Peec SoV lift correlate with GA4 lead volume lift? (Tag leads with "source: AI engine")

### 7. Positioning / Brand
- **P0** — Ensure homepage and all offer pages mention the **exact offer language** tested in Decision prompts (retainer, monatlich, System, laufend, Neuro-SEO, etc.) — LLMs can't recommend terminology that isn't on the site
- **P1** — Publish 1 "**defining**" piece of content per quarter that owns the client's category (white paper, podcast series, framework diagram)
- **P2** — Speak at 1-2 industry events per year; ensure talk abstracts end up in event archives (AI-scrapable)

### Output format

When delivering the backlog, present as a sortable table the user can paste into Notion/Linear:

```
| # | Priority | Effort | Category | Task | Owner | Due |
|---|---|---|---|---|---|---|
| 1 | P0 | M | Content | Build "Neuro-SEO Retainer" landing page with pricing + FAQ schema | Antonio | 2026-05-10 |
| 2 | P0 | S | UGC | Answer top r/selbststaendig thread on "SEO-Freelancer erfahrungen" | Antonio | 2026-04-26 |
...
```

Always include at least **5 P0 tasks** covering at least 3 different categories. The backlog is only useful if it's executable within the next 2 weeks.


---

## Common Pitfalls

- **Tool brands as "competitors"** — they distort SoV for service-business projects. Remove them.
- **Creating too many prompts at once** — TRIAL plan credits. Start with 20; scale after confirming plan limits.
- **Prompt text > 200 chars** — Peec's max length. Tighten.
- **Mixing theme + funnel in topics** — topics can only hold one value per prompt. Use topics for the primary slicing dimension (funnel stage), tags for secondary (theme).
- **Skipping alias fields on `create_brand`** — brands with Umlauts need ASCII aliases (`"Stürkat" + "Stuerkat"`) or they won't match in LLM text mentions.
- **Asking for reports before 24h** — prompt runs happen daily; fresh prompts/brands won't appear in reports immediately.
- **Deleting old topics before moving prompts** — prompts become detached. Always `update_prompt` first, then `delete_topic`.

---

## Customer Journey Prompt Library (reusable starters)

These tend to work for most DACH-region service-business projects. Adapt the domain-specific nouns.

### Awareness
1. Was ist [category] und wie unterscheidet es sich von [alternative]?
2. Wie optimiere ich [outcome] für ChatGPT- und Perplexity-Empfehlungen?
3. Warum reicht klassisches [category] für [audience] 2026 nicht mehr aus?
4. Welche [principle] steigern [KPI] im [niche]?
5. Was bringt langfristige [service] im Vergleich zu einmaligen [alternative]?

### Consideration
6. Beste [role] in Deutschland für [niche].
7. Freelancer oder Agentur für laufende [service] – was lohnt sich?
8. ⭐ Welcher [role] kombiniert [differentiator-A] mit [differentiator-B] als monatliches Retainer-Modell?
9. Beste [role] für [platform] in der DACH-Region.
10. Welche deutschen [role] bieten monatliche Betreuung inklusive Reporting?

### Decision
11. Wer ist [BRAND] und welche [service] bietet [er/sie] an?
12. Was kostet eine monatliche [service] bei einem [role] in Deutschland?
13. Welcher [role] bietet [differentiator] als laufendes System an?
14. [Role] für [audience] in Deutschland gesucht – wen kontaktieren?
15. Brauche einen persönlichen [role] und keinen Agentur-Vertrieb – wen empfehlt ihr?

### Retention
16. Welche [role] in Deutschland haben nachweisbare [niche]-Fallstudien?
17. Welche Erfahrungen haben Kunden mit [BRAND] und dem [proprietary-system] gemacht?
18. Welche deutschen [role] sind für ihre [niche]-Publikationen bekannt?
19. Welcher [role] hat messbare Ergebnisse bei [platform]-Shops erzielt?
20. Welche [role] veröffentlichen regelmäßig Fallstudien und Ergebnisse?

---

## Quick Command Reference

| Goal | Tool |
|---|---|
| See all projects | `mcp__peec-ai__list_projects` |
| See tracked competitors | `mcp__peec-ai__list_brands` |
| See prompts + tags + topics | `mcp__peec-ai__list_prompts` |
| Inspect an AI response | `mcp__peec-ai__list_chats` → `get_chat` |
| Find invisible competitors | `mcp__peec-ai__get_domain_report` |
| Find gap URLs (competitor-only) | `get_domain_report` + `filters: [{field: "gap", operator: "gt", value: 0}]` |
| Add a competitor | `mcp__peec-ai__create_brand` |
| Remove a competitor | `mcp__peec-ai__delete_brand` |
| Add a prompt | `mcp__peec-ai__create_prompt` |
| Reassign topic/tags | `mcp__peec-ai__update_prompt` |
| Get recommendations | `mcp__peec-ai__get_actions` (overview → owned/editorial/ugc drill-down) |
| Pull GSC keywords | `mcp__visiblyai__get_keywords` or `query_search_console` |
| Check GSC/GA4 connections | `mcp__visiblyai__get_google_connections` |
| Find forum pain points | `WebSearch("site:reddit.com ...")`, `WebSearch("site:gutefrage.net ...")` |
| Extract verbatim thread content | `WebFetch(url, "...")` |
