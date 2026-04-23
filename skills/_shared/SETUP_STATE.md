# Setup State — shared convention

Single source of truth for how Peec AI Skills remember **whether the project setup has been completed** and avoid re-running discovery from scratch on every invocation.

All skills in this repo MUST follow this convention. Do not invent alternatives.

---

## File location

```
<project>/growth_loop/setup_state.json
```

`<project>` is the local working directory the user is operating in (the same root where `decisions_log.md`, `*_learnings.json`, and `patterns.md` live — see `ai-growth-agent/SKILL.md` §Output and `growth-loop-reporter/SKILL.md` §Output).

If `<project>/growth_loop/` does not exist yet, the writer creates it.

---

## Schema

```json
{
  "peec_project_id": "string",
  "domain": "string",
  "target_country": "DE",
  "prompt_language": "de",
  "secondary_languages": [],
  "setup_version": "1.1",
  "completed_at": "2026-04-23T14:30:00Z",
  "phases_completed": [
    "competitors",
    "prompts",
    "topics",
    "tags",
    "gsc_mapping",
    "forum_mining",
    "backlog"
  ],
  "snapshot": {
    "brands": 8,
    "prompts": 24,
    "topics": 6,
    "tags": 18
  },
  "hero_prompt_id": "string|null",
  "last_audit_at": null,
  "notes": "optional free text — what was unusual about this setup"
}
```

**Field rules:**
- `target_country` — ISO 3166-1 alpha-2 (`DE`, `AT`, `CH`, `US`, `UK`, ...). The market the brand is selling into. Used by all skills for SERP / GSC filters and forum-source choice (Reddit vs Gutefrage vs OMR vs Quora).
- `prompt_language` — ISO 639-1 (`de`, `en`, `fr`, ...). The language Peec prompts are authored in. Drives content-brief language, outreach-pitch language, and which forums to mine. **Decoupled from `target_country`** because CH/de, CH/fr, BE/nl, US/es etc. are real cases.
- `secondary_languages` — optional list for multi-market projects (e.g. `["en"]` when DE is primary but EN content is also produced). Empty array is the default.
- `completed_at` — ISO 8601 UTC. Set on first successful end-to-end run.
- `phases_completed` — append-only. Partial re-runs add missing phases; never reset.
- `snapshot` — counts at the moment of `completed_at`. Used to detect drift via cheap live check.
- `last_audit_at` — set when a re-run is performed in `audit` mode.
- `setup_version` — bump when this schema changes; writers must migrate older versions. Current: `1.1`.

**Migration from v1.0 → v1.1:** if reading a state file with `setup_version == "1.0"` (no `target_country` / `prompt_language`):
- promote old `market` field (if present) into `target_country`; otherwise default to `DE`
- default `prompt_language` to lowercase of `target_country` (`DE` → `de`)
- write back with `setup_version = "1.1"` after the next successful run

---

## Read protocol — every skill except `ai-visibility-setup`

Before any other work, run this check:

```
1. Try to read <project>/growth_loop/setup_state.json
2. If file missing OR completed_at missing OR phases_completed lacks one of
   {competitors, prompts, topics, tags}:
     STOP. Output exactly:
       "No Peec setup state found at <project>/growth_loop/setup_state.json.
        Run /ai-visibility-setup first."
     Do not attempt to bootstrap setup yourself.
3. If completed_at is older than 90 days:
     WARN once in your output:
       "Setup is N days old — consider /ai-visibility-setup audit before acting on the result."
     Continue anyway.
4. Use peec_project_id from state as the canonical project ID for this run.
   Do not call list_projects again unless explicitly overridden by the user.
5. Read prompt_language and target_country from state. These drive:
     - the language of any content brief, outreach pitch, or forum query you produce
     - SERP / GSC market filters (e.g. visiblyai__query_search_console country=DE)
     - which forums to mine (DE → reddit.com/r/de + gutefrage.net + t3n;
       AT → derstandard.at forums + reddit;
       US → reddit.com + quora;
       CH → reddit.com/r/de + reddit.com/r/fr + 20min.ch comments)
   Never default to English silently — if these fields are missing, treat the state as v1.0 and apply migration defaults from §Field rules.
```

**Why a hard stop instead of falling through to setup:** each skill has a focused role. Discovery + competitor pruning + funnel design is the job of `ai-visibility-setup` alone — duplicating it inside every skill creates drift.

---

## Write protocol — `ai-visibility-setup` only

```
At the end of Phase 9 (or whichever phase concludes the run):
  1. Read existing setup_state.json if present.
  2. Merge:
       - phases_completed = union(old, new)
       - snapshot = fresh counts from live Peec calls just made
       - completed_at = keep old value if present, else set to now
       - last_audit_at = now (only if scope=audit and old completed_at exists)
  3. Write atomically (write to .tmp, rename) to avoid half-written files
     if the user interrupts.
  4. Print one line in the run summary:
       "State written: <project>/growth_loop/setup_state.json (phases: X/7)"
```

`ai-visibility-setup` also reads the file at Phase 0 to decide between `full | audit | partial | skip` (see that skill's Phase 0 section).

---

## Re-run modes (determined by Phase 0 of `ai-visibility-setup`)

| State file | Live Peec content | Default mode | Behaviour |
|---|---|---|---|
| Missing | Empty (≤2 brands AND ≤4 prompts AND ≤0 topics) | `full` | Greenfield. Run all 9 phases. Write fresh state. |
| Missing | **Populated** (≥3 brands OR ≥5 prompts OR ≥1 topic) | `import` | Brownfield. Reconstruct state from live Peec, ASK user to confirm + provide language/country, then write state. **Do not redo discovery.** |
| Present, < 30 days | — | `skip` | Show summary, ASK user before re-running. Do not auto-redo. |
| Present, 30–90 days | — | `audit` | Live-diff snapshot vs Peec, report drift, only re-run phases where drift > 20%. |
| Present, > 90 days | — | `full` (warn) | Recommend full re-run; data is stale. |

The user can always force a mode with `scope=full` etc.

### `import` mode (brownfield) — minimum work to bootstrap state

When the state file is missing **but** Peec already has content:

```
1. Run cheap parallel reads:
     list_brands, list_prompts(limit=200), list_topics, list_tags
2. Show user a one-line summary:
     "Detected existing Peec setup: <N> brands, <M> prompts, <T> topics, <G> tags."
3. ASK three things at once:
     - "Import this as the setup state, or run full setup from scratch? [import/full]"
     - "Target country (ISO, e.g. DE)?"
     - "Prompt language (ISO, e.g. de)?"
4. If user picks `import`:
     phases_completed = inferred from non-empty buckets
       (brands ≥ 3 → +"competitors"; prompts ≥ 5 → +"prompts";
        topics ≥ 1 → +"topics"; tags ≥ 5 → +"tags")
     snapshot         = the counts just read
     completed_at     = INFERRED from Peec — see "Inferring setup date" below.
                        Never silently default to now() — that would mask a stale setup
                        and prevent the audit-mode trigger.
     imported_at      = now (UTC) — separate field, records when this state file was created
     last_audit_at    = now
     hero_prompt_id   = null (the user can re-run a partial Phase 9 to set it)
     notes            = "imported from existing Peec project on <imported_at>;
                         original setup inferred at <completed_at>"
     setup_version    = "1.1"
   Write atomically. Print:
     "State imported: <project>/growth_loop/setup_state.json (phases: X/7).
      Inferred setup date: <YYYY-MM-DD> (~N days ago).
      Run /ai-growth-agent to pick the next move, or /ai-visibility-setup partial:gsc_mapping
      to fill in skipped phases."

   **Inferring setup date:**
   - Read `created_at` from `list_brands` and `list_prompts` results (Peec exposes both).
   - `completed_at = min(created_at across the first 5 brands AND first 5 prompts)`
     — i.e. when the bulk of structural setup happened. Single later additions don't reset it.
   - If `created_at` is unavailable on the Peec response (older API), fall back to
     `list_chats(limit=1, sort=asc)` to get the earliest chat timestamp; use that as a
     proxy for "project has been live since".
   - If both are unavailable: ASK the user "Roughly when did you set this Peec project up?
     [today / past month / past quarter / past year / older]" and bucket to a date.
     Never invent a date silently.
5. If user picks `full`: proceed with full Phase 1 onwards, overwriting Peec content.
   (Confirm once more — full mode will create new prompts/topics/tags.)
```

This means a long-running Peec project can adopt these skills **without** a destructive 9-phase re-run.

---

## What this is NOT

- Not a replacement for SkillMind cross-project memory. SkillMind stores transferable **patterns**; setup_state stores the **project's own** completion record.
- Not a Peec data cache. Always pull live data for analysis; the snapshot is only a freshness indicator.
- Not synced to Peec. The state lives locally with the user's project workspace.
