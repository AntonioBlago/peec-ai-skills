---
name: peec-checkup
description: Read-only health check for an existing Peec AI project. In one pass produces (1) a setup-quality audit (red flags from the structural setup — wrong competitors, funnel gaps, taxonomy issues), (2) a brand-performance snapshot (visibility per stage / engine, hero prompts winning vs losing, source diversity, competitor delta), and (3) a priority-ranked list of 5–8 concrete improvements drawn from Peec's get_actions + URL gap data. Works from day 1 of Peec data — no 4-week history needed. Never writes to Peec or to setup_state.json. Use when the user asks "Wo stehe ich?", "Wie ist mein Status?", "Was sind die Verbesserungspotenziale?", "Mein Setup checken", or runs /peec-checkup.
user-invocable: true
---

# Peec Checkup

## Role
Single read-only pass over a Peec project that answers three questions:

1. **Setup quality** — is the project configured correctly, or are there structural problems holding back every measurement?
2. **Brand performance now** — where does the brand actually stand, snapshot today?
3. **Top improvements** — which 5–8 concrete moves would move the needle most, ranked?

No writes. No content production. No outreach. Pure diagnosis + recommendations.

## Input
- `project_id` — Peec project (read from `setup_state.json` per pre-flight; fallback to `mcp__peec-ai__list_projects` if state missing)
- optional `date_range` — default last 28 days (falls back to whatever data exists if project is younger)
- optional `top_n` — number of improvements to surface, default 5, max 8

## Output
One markdown report saved to `<project>/checkups/YYYY-MM-DD_checkup.md` (schema in §6). Mirrored to stdout for the user. Never modifies setup_state.json or any Peec data.

## When to use
- "Wo stehe ich bei Peec?" / "Wie ist mein Status?"
- "Mein Setup checken" / "Was läuft falsch bei meinem Peec-Projekt?"
- "Welche Verbesserungspotenziale gibt es?"
- Onboarding a project from another consultant — first pass to see what was set up
- Periodic ritual: monthly without 4 weeks of action history (use `growth-loop-reporter` instead when history exists)
- After someone else changed the Peec project and you want to see what shifted

Do not use when:
- The user wants ONE next action — that is `/ai-growth-agent`
- The user wants attribution of past actions — that is `/growth-loop-reporter`
- The project is empty — that is `/ai-visibility-setup` (full mode)
- The user wants to mutate Peec — every other skill, not this one

---

## Pipeline

### 0. Pre-flight — setup state required (lenient)

Per [`_shared/SETUP_STATE.md`](../_shared/SETUP_STATE.md), this skill prefers a state file but **does not hard-stop** without one — checkup is itself the audit you'd run when state is missing. Logic:

```
Read <project>/growth_loop/setup_state.json
If present:
  Use peec_project_id, target_country, prompt_language from state.
  Note the setup age in the report.
If missing:
  Resolve project via mcp__peec-ai__list_projects.
  Note in the report: "no setup_state.json — run /ai-visibility-setup
  (mode: import) after this checkup to persist findings."
  Default target_country=DE, prompt_language=de UNLESS the user said otherwise.
```

This is the only consumer skill allowed to run without a state file — because its whole job is to tell you whether you should run `ai-visibility-setup` next.

### 1. Setup-quality audit (read-only mirror of ai-visibility-setup Phase 1 + 2)

Parallel reads:
```
mcp__peec-ai__list_brands(project_id)
mcp__peec-ai__list_prompts(project_id, limit=200)
mcp__peec-ai__list_topics(project_id)
mcp__peec-ai__list_tags(project_id)
```

Score against this checklist (each item = +/− points; record per-finding evidence):

| Check | Red flag |
|---|---|
| Competitors are real buyer alternatives | SaaS tool brands present (SEMrush, Ahrefs, Sistrix, Moz, Ryte, Yoast, Frase, Surfer, ScreamingFrog) — distort SoV |
| Competitors include AI-recommended ones | Compare list to brands appearing in `list_chats` sources but not tracked → "invisible competitors" |
| Funnel coverage balanced | Counts per stage (Awareness/Consideration/Decision/Retention) — flag any stage <20% or >50% of total |
| Prompts use buyer language | Quick scan: ≥3 prompts contain platform-vendor phrases ("empfiehl", "vergleich", "alternativ") |
| Prompts under 200 chars | Peec hard limit — list any over |
| Topics enable funnel slicing | Topics named after funnel stages OR by clear analytical axis (offer, audience). Flag topics that are pure themes ("AI", "SEO") with no slicing value |
| Tags are richer than the default 4 | If only `branded`/`non-branded`/`informational`/`transactional` exist → no offer/persona slicing possible |
| Brand aliases handle Umlauts | Any brand with Umlauts in name but no ASCII alias (`"Stürkat"` without `"Stuerkat"` alias) → matching fails on chats |
| Hero prompt identified | `setup_state.hero_prompt_id` set OR clearly inferrable from get_brand_report; flag if not |

Output: a **Setup Health Score** = % of checks passing, plus the bulleted findings (severity P0/P1/P2).

### 2. Brand-performance snapshot (read-only mirror of Phase 9)

```
own_brand_id = first brand whose domain matches setup_state.domain
              (or whose name == own_domain root); if ambiguous, ASK once

# Per-stage visibility
mcp__peec-ai__get_brand_report(
  project_id, start_date, end_date,
  dimensions=["topic_id"],
  filters=[{field: "brand_id", operator: "in", values: [own_brand_id]}]
)

# Per-engine visibility
mcp__peec-ai__get_brand_report(
  project_id, start_date, end_date,
  dimensions=["model_id"],
  filters=[{field: "brand_id", operator: "in", values: [own_brand_id]}]
)

# Per-prompt — find winners + losers
mcp__peec-ai__get_brand_report(
  project_id, start_date, end_date,
  dimensions=["prompt_id"],
  filters=[{field: "brand_id", operator: "in", values: [own_brand_id]}]
)

# Source diversity (how many distinct sources is the brand cited from)
mcp__peec-ai__get_url_report(
  project_id, start_date, end_date,
  dimensions=["url"],
  filters=[{field: "brand_id", operator: "in", values: [own_brand_id]}],
  limit=50
)

# Competitor delta — strongest opposition per topic
mcp__peec-ai__get_brand_report(
  project_id, start_date, end_date,
  dimensions=["topic_id", "brand_id"]
)
```

Compute:
- **Visibility now** — overall % + per stage + per engine
- **Hero prompts winning** — prompts where own_brand visibility > 50% (top 5)
- **Hero prompts losing** — prompts where own_brand visibility = 0 AND a competitor visibility > 30% (top 5)
- **Funnel weakness** — the stage with the lowest visibility (and which competitor dominates it)
- **Engine weakness** — the engine where the brand is invisible (chatgpt vs perplexity vs google-ai-overview)
- **Source diversity** — count of distinct domains the brand is cited from; <5 = weak; >15 = healthy

If the project has < 7 days of data: explicitly say so and skip the per-prompt sections — only report counts. Do not invent insights from one day of data.

### 3. Improvement candidates (raw inputs)

```
mcp__peec-ai__get_actions(project_id, scope="overview",  start_date, end_date, limit=10)
mcp__peec-ai__get_actions(project_id, scope="editorial", start_date, end_date, limit=10)
mcp__peec-ai__get_actions(project_id, scope="ugc",       start_date, end_date, limit=10)
mcp__peec-ai__get_actions(project_id, scope="owned",     start_date, end_date, limit=10)

# Where competitors get cited but I don't
mcp__peec-ai__get_url_report(
  project_id, start_date, end_date,
  filters=[{field: "gap", operator: "gt", value: 0}],
  limit=25
)
```

This produces a raw candidate pool of ~50 items. Do not return all of them.

### 4. Prioritise — score and rank

For each candidate, compute a **leverage score**:

```
leverage = impact × actionability × strategic_fit
```

| Dimension | Scoring rule |
|---|---|
| **impact** (0–3) | Peec opportunity_score band (0=low, 1=mid, 2=high, 3=top quartile) |
| **actionability** (0–3) | 3 = direct edit (own URL, own prompt fix); 2 = one outreach pitch; 1 = content brief required; 0 = needs new SEO project (>4 weeks) |
| **strategic_fit** (0–3) | 3 = fixes funnel weakness from §2 OR aligns to user's prior `setup_state.notes` / SkillMind priors; 1 = generic |

Multiplicative — anything with a 0 in any dimension is dropped (those are noise).

Take top `top_n` (default 5). For each, output:
- One-sentence action
- Which signal in §1 / §2 caused it (causal trace, not just "Peec said so")
- Suggested handoff skill (`/peec-content-intel`, `/citation-outreach`, `/ai-visibility-setup partial:<phase>`)
- Estimated effort (S/M/L)
- Estimated 4-week metric impact (visibility delta on which prompt or zone)

Always include at least one **structural improvement** (from §1) if the Setup Health Score is < 80%. Don't drown setup issues under content opportunities — broken setup invalidates everything else.

### 5. Synthesize report

Save to `<project>/checkups/YYYY-MM-DD_checkup.md` (create dir if missing) and stream to user. See §6 schema.

End with one decisive sentence: **"Empfohlene nächste Aktion: <skill>"** — the single most leveraged item from §4.

---

## 6. Output schema

```markdown
# Peec Checkup — <domain> · <YYYY-MM-DD>

## TL;DR
- Visibility now: **<X%>** (was <prev>% N days ago — only if prior checkup exists)
- Setup health: **<Y%>** (<P0 count> P0 issues, <P1 count> P1)
- Strongest funnel: <stage> (<X%>) · Weakest: <stage> (<Y%>)
- Top competitor on weak stage: <brand>
- Recommended next action: <one skill + scope>

## 0. Inventory (counts as of <date>)

| Bucket | Count | Notes |
|---|---|---|
| Brands tracked | <N> | own=1 · competitors=<N-1> · invisible candidates=<N> |
| Prompts total | <M> | active=<M_active> · paused=<M_paused> |
| · Awareness | <a> | <a/M %> |
| · Consideration | <b> | <b/M %> |
| · Decision | <c> | <c/M %> |
| · Retention | <d> | <d/M %> |
| · Unclassified | <e> | flag if >0 — funnel-stage missing |
| Topics | <T> | named: <list first 5> |
| Tags | <G> | non-default: <list non-default tags> |
| Chats analysed in window | <C> | per engine: chatgpt=<x> · perplexity=<y> · gao=<z> |
| Window | <date_range> | days_with_data=<N> |

If `days_with_data < 7` → mark sections 2 + 3 with **"insufficient data"** badge and skip per-prompt detail.

## 1. Setup health (<Y%>)

### P0 — must fix (block valid measurement)
- <finding> — evidence: <data point>

### P1 — should fix (skews insights)
- <finding> — evidence: <data point>

### P2 — nice to have
- <finding>

## 2. Brand performance now (window: <date_range>)

### Visibility per funnel stage
| Stage | Visibility | Top competitor (delta) |
|---|---|---|
| Awareness | X% | comp.de (-Y%) |
| Consideration | … | … |
| Decision | … | … |
| Retention | … | … |

### Visibility per engine
| Engine | Visibility |
|---|---|
| chatgpt-scraper | X% |
| perplexity-scraper | … |
| google-ai-overview-scraper | … |

### Hero prompts — winning (top 5)
1. **<prompt text>** — Y% visibility, mostly via <engine> · sources: <count distinct>

### Hero prompts — losing (top 5)
1. **<prompt text>** — 0% visibility · top competitor: <brand> at <Z%> · cited URL type: <LISTICLE/ARTICLE/COMPARISON/HOW_TO_GUIDE/DISCUSSION>

### Source diversity
<N> distinct source URLs · top sources: <list 5> · health: <weak / OK / healthy>

## 3. Top <N> improvements (priority-ranked)

### #1 — <short action title>
- **Why now:** <causal trace from §1 or §2>
- **Handoff:** <skill + parameters>
- **Effort:** <S / M / L>
- **4-week metric:** <specific delta>

### #2 …

## Recommended next action
**<one skill invocation>** — because <one sentence>.

---
*Read-only checkup. No Peec data was modified. State file: <found at path | missing>.*
```

---

## Guardrails

- **Never call `mcp__peec-ai__create_*` or `delete_*` or `update_*`.** Pure read.
- **Never write `setup_state.json`.** Only `ai-visibility-setup` writes it. If state was missing, the report tells the user to run `/ai-visibility-setup partial:import` to persist findings.
- **Never invent insights from < 7 days of data.** Say "insufficient data" explicitly.
- **Never silently assume language/country.** If state has them, use them. If not, ask once before §3.
- **Never bury setup issues under content opportunities.** A Setup Health Score < 80% means the structural fix outranks any content recommendation in §4.
- **Never produce >8 improvements.** If 50 candidates score similarly, the scoring is wrong — re-tighten thresholds, don't widen output.

## Relationship to other skills

```
/peec-checkup
   │ (read-only diagnosis)
   ↓
   reports → user decides
   │
   ├── if structural P0 → /ai-visibility-setup (partial / audit)
   ├── if specific prompt to win → /peec-content-intel
   ├── if outreach gaps → /citation-outreach
   ├── if you want ONE decisive next move → /ai-growth-agent
   └── if you want time-series + attribution → /growth-loop-reporter (needs 4+ weeks)
```

`/start-peec` may route to `/peec-checkup` when the user's intent is observational ("how am I doing?") rather than action-driven ("what should I do?"). The two are complementary, not redundant: checkup is the lens, growth-agent is the trigger.
