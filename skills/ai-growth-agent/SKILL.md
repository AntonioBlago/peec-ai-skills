---
name: ai-growth-agent
description: Orchestrator for the 5 Peec AI growth skills (ai-visibility-setup, peec-content-intel, content-cluster-builder, citation-outreach, growth-loop-reporter). Reads project state and last learnings, detects the single highest-leverage gap, and returns exactly one next-move decision with a measurable 4-week metric — then hands off to the skill that executes it. Use when multiple priorities compete and you need one call, not a dashboard.
user-invocable: true
---

# AI Growth Agent

## Role
Pick the single next move for a Peec AI project. One decision, one skill handoff, one measurable 4-week target. Nothing else.

## Input
- `project_id` — resolve via `mcp__peec-ai__list_projects` if unknown
- optional `focus` — force a specific gap type (`taxonomy|cluster|content|citation|learning`)

## Output
One markdown document matching the schema in §5, plus one appended entry in `<project>/growth_loop/decisions_log.md`. Nothing else is produced.

## When to use
- Weekly 30-min ritual: "what is the one thing this week?"
- When multiple priorities compete and clarity is missing
- Quarterly strategy refresh

Do not use when:
- The answer is already known — call the target skill directly
- Peec project has <7 days of data — run `ai-visibility-setup` first

---

## The loop

```
     ┌─────────────────────────────────────────────────┐
     │                                                 │
     │  1. UNDERSTAND                                  │
     │     ai-visibility-setup  (prompts + taxonomy)   │
     │     peec-content-intel   (demand signals)       │
     │                  ↓                              │
     │  2. ANALYZE                                     │
     │     content-cluster-builder (zones)             │
     │     peec-content-intel      (source intel)      │
     │                  ↓                              │
     │  3. DECIDE                                      │
     │     → THIS SKILL: one zone + one action         │
     │                  ↓                              │
     │  4. EXECUTE                                     │
     │     content-write     (new content)             │
     │     citation-outreach (external citations)      │
     │                  ↓                              │
     │  5. LEARN                                       │
     │     growth-loop-reporter                        │
     │                  ↓                              │
     └───────→ feedback into step 1 ────────────────────┘
```

One full cycle: **1 week** for active projects, **4 weeks** for maintenance.

---

## Pipeline

### 1. Read state
```
mcp__peec-ai__list_projects                       → resolve project
mcp__peec-ai__get_brand_report(dimensions=["date"], start_date=-28d)
Read: <project>/growth_loop/*_learnings.json      (may not exist)
Read: <project>/growth_loop/decisions_log.md      (may not exist)
Read: <project>/outreach/*_outreach_log.md        (may not exist)

# Cross-project priors (optional, if SkillMind MCP is available)
mcp__skillmind__recall(query="<likely gap type>", k=5, filter_tags=["peec"])
```

If no history exists: say so plainly ("first run — deciding from structural data only, next run will be sharper") and continue. If SkillMind is not installed, skip the recall step — patterns are a bonus prior, not a requirement.

### 2. Detect gap (priority ladder — higher tier always wins)

| Tier | Gap | Signal | Handoff |
|---|---|---|---|
| 1 | Data | Peec has <7 days of history | STOP. Wait, do not force action. |
| 2 | Taxonomy | Missing funnel stage · tags unclear · <20 prompts | `ai-visibility-setup` (full or partial) |
| 3 | Cluster | 20+ prompts, no strategic zones / tags | `content-cluster-builder` |
| 4 | Content | Zones exist, but a zone has no hero asset | `content-write` (external) or `peec-content-intel` for the brief |
| 5 | Citation | Hero content exists, no external citations | `citation-outreach` |
| 6 | Learning | Loop is running, no pattern tracking | `growth-loop-reporter` |

**Rule:** Exactly one tier per cycle. If two tiers look tied, pick the lower number. Parallel work across tiers means the tiers weren't ranked properly — fix the ranking.

### 3. Produce decision (see §5 schema)

The decision names **one** skill, **one** scope, **one** 4-week metric with a concrete number. No "and also", no "optionally". If the measurable change wouldn't happen in 4 weeks, the metric is wrong — rewrite it.

### 4. Hand off

Invoke the target skill with parameters pre-filled. Do not recommend — execute. The user can override at any point, but default is execution.

### 5. Log

Append to `<project>/growth_loop/decisions_log.md` using the schema in §6. Every next run reads this file first — the log IS the memory.

---

## Decision output schema

```markdown
# Growth Agent — <project name> (<YYYY-MM-DD>)

## Decision
<One sentence. One verb. One object. One deadline.>

## Why this, now
<3–5 sentences. Causal chain: signal → implication → therefore this action.>

## How
Run <skill-name> with:
  <param>: <value>
  <param>: <value>

## Measurable in 4 weeks
<Specific metric + number. "Visibility on prompt pr_xxx: 0% → ≥15%."
 If this doesn't move, the decision was wrong.>

## Not doing now (explicit skip)
- <option>: skipped because <reason>
- <option>: skipped because <reason>

## Next checkpoint
<YYYY-MM-DD> — re-run agent, measure the metric above.
```

## Decision log schema

```markdown
## <YYYY-MM-DD> — <skill-name>

Signal: <what in the data triggered this>
Decision: <one sentence>
Params: <key=value, key=value>
Executed: ✓ | ✗ <reason>
Output: <one line on what came out>
Checkpoint: <YYYY-MM-DD> — metric: <name + target>
```

---

## Handoff matrix

| Intent | Skill |
|---|---|
| Setup / taxonomy / competitors | `@ai-visibility-setup` |
| Strategic zones from flat prompt set | `@content-cluster-builder` |
| Source / demand research for a prompt | `@peec-content-intel` |
| New article (handled outside this repo) | `@content-write` |
| External citations & outreach | `@citation-outreach` |
| Weekly / monthly loop close | `@growth-loop-reporter` |

---

## Example (real output, Antonio Blago project, 2026-04-19)

```markdown
# Growth Agent — Antonio Blago (2026-04-19)

## Decision
Build the content zone "KI-SEO Retainer Decision" by 2026-04-26 with one hero article.

## Why this, now
47 Peec prompts are active, but the Decision stage is covered by only 3 weak prompts,
2 of which sit at 0% visibility. The Retainer is the main revenue product — Decision
must be the strongest zone, is currently the weakest. No other tier resolves this gap.

## How
Run content-write with:
  project_id: or_bf5b4228-7344-4f71-b231-c4396a7775f6
  focus_keyword: "KI-SEO Retainer"
  page_type: blog
  language: de

## Measurable in 4 weeks
Visibility on pr_a38381d4: 0% → ≥15%. Aggregate visibility of zone
"KI-SEO Retainer Decision": → >10%.

## Not doing now (explicit skip)
- New Awareness cluster ("Was ist GEO?") — 4 prompts already cover it, smaller gap.
- Citation outreach — no substance to pitch until hero content is live.

## Next checkpoint
2026-05-17 — measure visibility trend for pr_a38381d4 + zone tag.
```

---

## Guardrails (do not do these)

- Do not list options — pick one
- Do not say "it depends" without saying on what
- Do not delegate analysis back to the user — the analysis is the job
- Do not say "everything is fine, keep going" — a critical read is the core value
- Do not ask for more input, except at Tier 1 (genuine data gap)
- Do not work on two tiers in parallel
