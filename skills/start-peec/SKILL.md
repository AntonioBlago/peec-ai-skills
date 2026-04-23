---
name: start-peec
description: Single-entry slash command for the Peec AI growth loop. Detects whether the current working directory has a setup_state.json, what state it's in (missing / fresh / stale / very stale / brownfield-importable), and hands off to the right skill — /ai-visibility-setup (full or import or audit) or /ai-growth-agent. Use when the user says "/start-peec", "what should I do for Peec", "is my setup done", or any opening question about a Peec AI project where the next move is unclear.
user-invocable: true
---

# Start Peec

## Role
The single entry point for any Peec AI growth-loop session. Reads state, decides which skill is responsible for the next move, hands off. No content production, no analysis — pure dispatch.

## Input
None. The skill resolves everything from `<cwd>/growth_loop/setup_state.json` and (if missing) live Peec calls.

## Output
A 4–8 line decision block, then exactly one skill invocation as the next step. Nothing more.

## When to use
- Opening a Peec growth session and unsure where to start
- Periodic ritual ("what's the move this week?")
- After onboarding a new project that already has data in Peec
- When a hook injects `=== PEEC PROJECT DETECTED ===` context

Do not use when:
- The user already named a specific skill (`/ai-growth-agent`, `/peec-content-intel`, etc.) — call that directly
- The user is mid-execution of another skill — don't interrupt

---

## Pipeline

### 1. Read local state

```
Read <project>/growth_loop/setup_state.json
```

`<project>` = `$CLAUDE_PROJECT_DIR` env var if set, else cwd. Walk up at most 2 parents looking for `growth_loop/setup_state.json` (mirrors `hooks/peec-detect.py` behavior).

### 2. Branch — no state file

If file missing, run a single parallel Peec read:
```
mcp__peec-ai__list_projects
mcp__peec-ai__list_brands(project_id)         # only after project resolved
mcp__peec-ai__list_prompts(project_id, limit=5)
mcp__peec-ai__list_topics(project_id)
```

Then:

| Live Peec content | Decision |
|---|---|
| Empty (≤2 brands AND ≤4 prompts AND ≤0 topics) | Hand off to `/ai-visibility-setup` (mode = full, greenfield) |
| Populated (≥3 brands OR ≥5 prompts OR ≥1 topic) | Hand off to `/ai-visibility-setup` (mode = import, brownfield — see [`_shared/SETUP_STATE.md`](../_shared/SETUP_STATE.md) §`import` mode) |
| Peec MCP unreachable / no projects | STOP. Output: "No Peec MCP connection. Add it via `claude mcp add peec-ai --transport streamable-http https://api.peec.ai/mcp` then retry." |

### 3. Branch — state file present

Compute `age_days = now - completed_at`.

**User-intent split:** if the user opened with an *observational* phrase ("wo stehe ich?", "wie ist mein status?", "checkup", "was ist der stand?", "show me the picture") → route to `/peec-checkup` regardless of age. The agent path is for *deciding the next move*; checkup is for *seeing the picture*. They are complementary.

Otherwise (action-oriented intent — "was als nächstes?", "what's next", default `/start-peec` with no qualifier):

| Age | Decision |
|---|---|
| < 7 days, no actions logged | Hand off to `/peec-checkup` — too little data for `/ai-growth-agent` decisions, but checkup still surfaces setup health + early signals. |
| 7–30 days | Hand off to `/ai-growth-agent` (which itself orchestrates `/peec-checkup` first) |
| 30–90 days | Hand off to `/ai-growth-agent`; mention "consider /ai-visibility-setup audit if cluster recommendations look thin" |
| > 90 days | Hand off to `/ai-visibility-setup` (mode = audit). Do not skip straight to growth-agent on stale taxonomy. |

If `phases_completed` is missing one of `{competitors, prompts, topics, tags}`, override the above and hand off to `/ai-visibility-setup partial:<missing-phase>` first.

### 4. Output schema

```markdown
# Start Peec — <YYYY-MM-DD>

State:        <found|missing|brownfield>
Project:      <domain> (peec_project_id=<id>)
Locale:       country=<XX> · language=<xx>
Setup age:    <N days> (<fresh|stale|very stale|n/a>)
Phases:       <list> · missing: <list>

Decision: <one sentence with the chosen skill + scope>

Why: <one sentence — which signal in the state caused this branch>

Next: <invoking the chosen skill now>
```

Then immediately invoke that skill. Do not wait for confirmation unless the chosen branch is destructive (`/ai-visibility-setup` in `full` mode on a populated Peec project — that always confirms once).

---

## Why this skill exists

Three frictions kept biting:
1. New users open a Peec project, don't know which of 7 skills to call first.
2. The hook (`hooks/peec-detect.py`) needs a manual counterpart for users who turned hooks off.
3. The orchestrator (`/ai-growth-agent`) refuses to run without a setup state — so first-timers hit a dead end.

`start-peec` fixes all three by being the single safe entry point that always picks a defensible next step.

## Relationship to other skills

```
/start-peec
   │
   ├── no state, Peec empty       → /ai-visibility-setup (full)
   ├── no state, Peec populated   → /ai-visibility-setup (import)
   ├── state present, < 90 days   → /ai-growth-agent
   ├── state present, > 90 days   → /ai-visibility-setup (audit)
   └── state has missing phases   → /ai-visibility-setup (partial:<phase>)
```

Never produces deliverables itself. Never bypasses the [`_shared/SETUP_STATE.md`](../_shared/SETUP_STATE.md) protocol — uses the same age thresholds and the same import-mode trigger as Phase 0 of `ai-visibility-setup`, so the dispatcher and the orchestrator agree on what "fresh" means.

## Guardrails

- Never call `mcp__peec-ai__create_*` or `mcp__peec-ai__delete_*`. Dispatch only.
- Never write `setup_state.json`. Only `/ai-visibility-setup` writes it.
- Never silently default `target_country` / `prompt_language`. If state is missing both AND user hasn't said, ASK once before handoff.
- Never invoke more than one downstream skill per `/start-peec` run.
