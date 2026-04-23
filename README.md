# Peec AI Skills for Claude Code

Production-tested [Claude Code](https://claude.com/claude-code) skills for **Peec AI** — the brand-visibility tracking platform for LLM-powered search (ChatGPT, Perplexity, Google AI Overviews, Gemini).

These skills turn a freshly-invoked Peec AI project into an operator-ready setup with the right competitors, the right prompts, a proper customer-journey taxonomy, and an actionable content pipeline — using the Peec AI MCP server, Visibly AI (GSC/GA4), and web research.

---

## Quick install (60 seconds)

```bash
# 1. Clone + install all 9 skills into ~/.claude/skills/
git clone https://github.com/AntonioBlago/peec-ai-skills.git ~/peec-ai-skills
cd ~/peec-ai-skills
./claude-peec-ai.sh                 # use --copy on Windows without dev mode

# 2. Connect the Peec AI MCP (OAuth in browser on first tool call)
claude mcp add peec-ai --transport streamable-http https://api.peec.ai/mcp

# 3. Restart Claude Code, then in any directory:
#    /start-peec    →  detects state, dispatches the right skill
```

That's it. <code>/start-peec</code> reads <code>growth_loop/setup_state.json</code> if present, otherwise probes Peec live and either offers brownfield import or runs greenfield setup. Optional MCPs (Visibly AI, SkillMind) are documented under [Prerequisites](#prerequisites).

📑 **5-minute overview:** [`docs/presentation/peec-ai-skills-deck.pdf`](docs/presentation/peec-ai-skills-deck.pdf) — 20-slide pitch + tutorial.

---

## Skill system (8 skills + 1 orchestrator + 1 entry point)

Not a feature list — a **closed growth loop** with a cross-project memory layer underneath. Every skill has a specific job; the orchestrator (`ai-growth-agent`) decides which one runs next; `skillmind-learner` lifts lessons out of one project into priors for the next.

```
     ┌────────────────────────────────────────────────────────┐
     │                                                        │
     │   ENTER               start-peec  (manual entry)      │
     │                       hooks/peec-detect.py (auto)      │
     │                                    ↓                   │
     │   UNDERSTAND          ai-visibility-setup              │
     │   (prompts,           peec-content-intel (demand)      │
     │    demand,                         ↓                   │
     │    taxonomy)                                           │
     │                                                        │
     │   DIAGNOSE            peec-checkup                     │
     │   (read-only          (setup health + brand snapshot   │
     │    health pass)        + ranked improvements)          │
     │                                    ↓                   │
     │   ANALYZE             content-cluster-builder          │
     │   (strategic          peec-content-intel (sources)     │
     │    zones)                          ↓                   │
     │                                                        │
     │   DECIDE    ◄──────── ai-growth-agent (orchestrator)   │
     │   (one move)          calls /peec-checkup first        │
     │                                    ↓                   │
     │                                                        │
     │   EXECUTE             @content-write (Visibly skill)   │
     │   (build +            citation-outreach                │
     │    distribute)                     ↓                   │
     │                                                        │
     │   LEARN               growth-loop-reporter             │
     │   (attribution,                    ↓                   │
     │    next moves)                                         │
     │                                                        │
     └────────→ feeds back into UNDERSTAND ───────────────────┘
                             │
                             ▼
     ┌────────────────────────────────────────────────────────┐
     │  CROSS-PROJECT MEMORY     skillmind-learner            │
     │  (patterns, priors)       read: priors for next loop   │
     │                           write: patterns after lift   │
     └────────────────────────────────────────────────────────┘
```

| Skill | What it does | Credits | When to trigger |
|---|---|---|---|
| [`start-peec`](skills/start-peec/SKILL.md) **(entry point)** | Single-entry slash command. Detects `setup_state.json`, picks the correct downstream skill (setup / checkup / agent / audit) based on state age + user intent (observational vs action). Pure dispatch — never produces deliverables itself. | free | "Where do I start?", `/start-peec` |
| [`ai-visibility-setup`](skills/ai-visibility-setup/SKILL.md) | End-to-end Peec project configuration: competitor discovery from real AI chats, forum pain-mining (Reddit, Gutefrage, t3n, OMR), customer-journey prompt design across Awareness → Consideration → Decision → Retention, and structured topic/tag taxonomy. 9 phases + Phase 0 (full / import / audit / partial / skip). | free | "Set up Peec for [client]", "My Peec competitors are wrong", "Restructure Peec topics" |
| [`peec-checkup`](skills/peec-checkup/SKILL.md) | **Read-only health pass.** One report covering inventory (counts), setup-quality audit (red flags), brand-performance snapshot (visibility per stage / engine, hero prompts winning vs losing, source diversity), and 5–8 priority-ranked improvements. Never writes. Works from day 1 of data. | free | "Wo stehe ich?", "Mein Setup checken", "Verbesserungspotenziale?" |
| [`peec-content-intel`](skills/peec-content-intel/SKILL.md) | Content-intelligence workflow: Peec gap-URLs → Query Fan-Out (via `mcp__visiblyai__query_fanout` ≥ v0.6.0) → Reddit/forum pain mining (via Peec's scraped index, bypassing Reddit's WebFetch block) → Visibly backlinks + onpage → opportunity scoring → publish-ready content brief. 6 phases. | ~10–45 Visibly cr | "Which content wins Peec prompt X?", "Build a content brief from Peec data" |
| [`content-cluster-builder`](skills/content-cluster-builder/SKILL.md) | Turns a flat Peec prompt set into **strategic topic zones** — clustered by intent × funnel stage × visibility gap × demand signal. Produces 4-8 zones, each with a concrete "one move now" action and a measurable success metric. Persists zones as Peec tags for later attribution. | ~5–15 cr | "I have 20+ prompts, give me a content architecture, not a calendar" |
| [`citation-outreach`](skills/citation-outreach/SKILL.md) | Converts Peec's `get_actions` + forum/UGC discovery into a **prioritized outreach pipeline**: contact extraction, pitch templates per channel type (editorial / Reddit / Gutefrage / YouTube), tracker file, citation-gain measurement. 5 pitches/week cap by default. | free | "Content is shipped — now I need external citations" |
| [`growth-loop-reporter`](skills/growth-loop-reporter/SKILL.md) | Weekly/monthly **loop-closer**: measures visibility delta per prompt/zone, attributes it to specific content + outreach investments, detects winning patterns, outputs a ≤ 400-word narrative with 3 next-actions and at least 1 "stop doing". Persists learnings for the next cycle. | free | Weekly ritual or after any major action |
| [`skillmind-learner`](skills/skillmind-learner/SKILL.md) | **Cross-project memory layer.** After a Peec skill produces a measurable outcome, extracts 1–3 transferable patterns (causal, falsifiable, evidence-backed) and persists them to SkillMind. On the next orchestrator run, recalls matching patterns as priors — lessons from project A inform decisions on project B. | free | After `growth-loop-reporter` closes a cycle, or when a pitch / brief / zone lift is measured |
| [`ai-growth-agent`](skills/ai-growth-agent/SKILL.md) **(orchestrator)** | The decision-making layer. **Always invokes `/peec-checkup` first** to get inventory + setup health + brand performance, then picks **one** next move with a measurable 4-week metric. Hands off to the right skill with parameters pre-filled. Tells you "do exactly this now" instead of "here is a dashboard". | free | "What should I work on this week?" |

All skills are **user-invocable** — Claude Code triggers them automatically when the conversation matches, and users can invoke them explicitly with `/start-peec`, `/ai-visibility-setup`, `/peec-checkup`, `/peec-content-intel`, `/content-cluster-builder`, `/citation-outreach`, `/growth-loop-reporter`, `/skillmind-learner`, or `/ai-growth-agent`.

---

## Prerequisites

**Required:**
- [Claude Code](https://claude.com/claude-code) (CLI, VS Code extension, or JetBrains plugin)
- Peec AI MCP server connected (provides `mcp__peec-ai__*` tools — see below)

### Peec AI — hosted MCP (OAuth, zero install)

Peec AI ships a remote MCP server at `https://api.peec.ai/mcp` with OAuth — no API key file, just a browser redirect on first use.

```bash
claude mcp add peec-ai --transport streamable-http https://api.peec.ai/mcp
```

…or add it directly to your Claude Code `settings.json` / `~/.claude.json`:

```json
{
  "mcpServers": {
    "peec-ai": {
      "type": "http",
      "url": "https://api.peec.ai/mcp"
    }
  }
}
```

The first time any skill calls a `mcp__peec-ai__*` tool, Claude Code opens a browser to sign you in to Peec AI and authorize access. Tokens persist; subsequent runs are silent. Full docs: [docs.peec.ai/mcp/setup](https://docs.peec.ai/mcp/setup).

**Optional but strongly recommended:**

### Visibly AI — hosted MCP (zero install)

Visibly AI is a **remote MCP server** — no pip install required. Just add the connection to your Claude Code `settings.json`:

```json
{
  "mcpServers": {
    "visiblyai": {
      "type": "http",
      "url": "https://mcp.visibly-ai.com/mcp",
      "headers": {
        "Authorization": "Bearer lc_your_key"
      }
    }
  }
}
```

Get your API key under Account → API Keys. Without the `Authorization` header, only the 8 free tools are available. Full developer docs: [antonioblago.com/de/entwickler/mcp](https://www.antonioblago.com/de/entwickler/mcp).

Provides: GSC / GA4 read-through, backlinks, onpage analysis, `classify_keywords`, and — since v0.6.0 — the `query_fanout` coverage analyzer.

### SkillMind — local MCP (pip install)

SkillMind is a **local MCP server** that provides the cross-project memory layer used by `skillmind-learner`. Install:

```bash
pip install "skillmind[pinecone,mcp,youtube]"
# or for everything:
pip install "skillmind[all]"
```

Then add to Claude Code `settings.json`:

```json
{
  "mcpServers": {
    "skillmind": {
      "command": "python",
      "args": ["-m", "skillmind.mcp.server"],
      "env": {
        "PINECONE_API_KEY": "your-pinecone-key",
        "SKILLMIND_BACKEND": "pinecone",
        "ANTHROPIC_API_KEY": "your-anthropic-key"
      }
    }
  }
}
```

Credentials can also live in a `.env` file in your project root instead of the `env` block. Repo: [github.com/AntonioBlago/skillmind](https://github.com/AntonioBlago/skillmind).

### How skills remember setup (`setup_state.json`)

Setup is expensive — discovering competitors from real AI chats, designing 20 funnel-spread prompts, building taxonomy. You don't want it re-run from scratch every time the orchestrator asks "what next?". So the skills share **one** state file:

```
<project>/growth_loop/setup_state.json
```

- **`ai-visibility-setup`** owns it: reads at Phase 0 to decide `full | audit | partial | skip`, writes at Phase 9 with merged phases + a fresh count snapshot + the resolved `target_country` / `prompt_language`.
- **All other skills** (`ai-growth-agent`, `peec-content-intel`, `content-cluster-builder`, `citation-outreach`, `growth-loop-reporter`) refuse to run without it. If the file is missing, they output one line:
  > `No Peec setup state found at <project>/growth_loop/setup_state.json. Run /ai-visibility-setup first.`

This means: every consumer skill knows the project ID, the language to write briefs in, the country to filter SERPs by, and which forums to mine — without re-asking you and without silently defaulting to English. Setup older than 90 days triggers a warning; older than that without `audit` mode is a yellow flag in any output.

Schema and full read/write protocol: [`skills/_shared/SETUP_STATE.md`](skills/_shared/SETUP_STATE.md).

### Auto-detection: `/start-peec` + hooks

Two ways the right next move surfaces without you remembering which of 7 skills to call:

**1. `/start-peec` — slash command (manual entry point)**
Always-safe single command. Reads `setup_state.json`, optionally probes Peec live, then hands off:

```
/start-peec
   │
   ├── no state, Peec empty       → /ai-visibility-setup (full)
   ├── no state, Peec populated   → /ai-visibility-setup (import)
   ├── state present, < 90 days   → /ai-growth-agent
   ├── state present, > 90 days   → /ai-visibility-setup (audit)
   └── state has missing phases   → /ai-visibility-setup (partial:<phase>)
```

Use this when you forget the right starting skill or a hook isn't installed.

**2. Hooks — automatic context injection**
Two hooks in `~/.claude/settings.json` wrap [`hooks/peec-detect.py`](hooks/peec-detect.py). The script is silent unless it has something to say — it never pollutes non-Peec sessions.

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "python \"<repo>/hooks/peec-detect.py\"",
        "timeout": 10,
        "statusMessage": "Peec context check..."
      }]
    }],
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "python \"<repo>/hooks/peec-detect.py\" --session-start",
        "timeout": 10,
        "statusMessage": "Peec setup state..."
      }]
    }]
  }
}
```

| Trigger | Behavior |
|---|---|
| Session opens in a dir with `growth_loop/setup_state.json` (own dir or up to 2 parents) | Injects state summary + recommended skill into Claude's context |
| Session opens elsewhere | Silent |
| Prompt mentions a Peec keyword (`peec`, `sichtbarkeit`, `ai visibility`, `/start-peec`, …) | Injects setup hint or current state |
| Prompt is unrelated | Silent |

Output is a JSON envelope (`hookSpecificOutput.additionalContext`) per the Claude Code hook schema — Claude sees it as system context and decides whether to act.

If you change the hook config, run `/hooks` once or restart Claude Code so the settings watcher reloads.

### Tool matrix

| Phase | MCP tool | Provider | Credits | Used by |
|---|---|---|---|---|
| 1 · Gap URLs | `mcp__peec-ai__get_url_report` (filter `gap > 0`) | Peec | free | content-intel |
| 1 · Brands & prompts | `mcp__peec-ai__list_brands` / `list_prompts` / `list_topics` / `list_tags` | Peec | free | visibility-setup |
| 2 · Query Fan-Out + coverage | **`mcp__visiblyai__query_fanout`** | Visibly ≥ 0.6.0 | ~3-5 | content-intel (primary), visibility-setup (optional) |
| 3 · Chat mining (competitors + language) | `mcp__peec-ai__list_chats` → `get_chat` | Peec | free | visibility-setup |
| 3 · Reddit / forum content | `mcp__peec-ai__get_url_content` (Peec has already scraped Reddit) | Peec | free | both |
| 4 · GSC keywords | `mcp__visiblyai__get_keywords` / `query_search_console` | Visibly | 0 (via GSC) | visibility-setup |
| 4 · Backlinks & authority | `mcp__visiblyai__get_backlinks` | Visibly | variable | content-intel |
| 4 · 24-point OnPage audit | `mcp__visiblyai__onpage_analysis` | Visibly | 15 | content-intel |
| 4 · Keyword intent + funnel | `mcp__visiblyai__classify_keywords` | Visibly | 1 | both |
| 5 · Brand CRUD | `mcp__peec-ai__create_brand` / `delete_brand` | Peec | free | visibility-setup |
| 5 · Prompt CRUD | `mcp__peec-ai__create_prompt` / `update_prompt` / `delete_prompt` | Peec | free | visibility-setup |
| 6 · Topic/Tag CRUD | `mcp__peec-ai__create_topic` / `create_tag` / `delete_topic` | Peec | free | visibility-setup |
| 7 · Recommendations | `mcp__peec-ai__get_actions(scope=overview|owned|editorial|ugc)` | Peec | free | visibility-setup |

### Graceful degradation

The skills work even when pieces are missing:

- **Without Visibly AI**: the skills still do the Peec-side setup, competitor discovery from chats, Reddit / forum mining via Peec's scraped index, and taxonomy setup. They skip: GSC keyword mapping (Phase 4 of visibility-setup) and coverage analysis (Phase 2 of content-intel). The content brief is still generated, just without depth / coverage scores.
- **Without `query_fanout` (Visibly MCP < 0.6.0)**: the content-intel skill falls back to an inline 6-axis heuristic (synonym, decision, comparison, problem, long-tail, forum). Coverage matching is skipped.
- **Without `classify_keywords`**: funnel-stage detection drops to keyword pattern matching inside the SKILL.md logic.
- **Without SkillMind**: `skillmind-learner` falls back to appending patterns to `<project>/growth_loop/patterns.md` and flags the skip. The orchestrator skips the cross-project `recall` call in Phase 1 — patterns are a bonus prior, not a requirement.

---

## Install

The repo ships with `claude-peec-ai.sh` — a single script that installs all 7 skills into `~/.claude/skills/` (or a target you choose). Symlink by default; `git pull` in the repo then updates every installed skill in place.

```bash
git clone https://github.com/AntonioBlago/peec-ai-skills.git ~/peec-ai-skills
cd ~/peec-ai-skills
./claude-peec-ai.sh                           # symlink all 7 skills into ~/.claude/skills/
```

Flags:

```bash
./claude-peec-ai.sh --copy                    # copy instead of symlink (no git-pull updates)
./claude-peec-ai.sh --target ./.claude        # per-project install (project-local .claude/)
./claude-peec-ai.sh --force                   # overwrite existing skill dirs
./claude-peec-ai.sh --dry-run                 # preview, no filesystem changes
./claude-peec-ai.sh --uninstall               # remove the 7 skill entries
./claude-peec-ai.sh --only skillmind-learner,ai-growth-agent   # partial install
```

Symlink mode on Windows needs either Developer Mode or admin rights; the script falls back to copy automatically if the symlink call fails. On WSL / Git Bash it usually just works.

### Verify

Start a Claude Code session and type:

```
/ai-visibility-setup
```

If the skill registers, Claude Code picks it up and the workflow begins.

---

## Usage examples

### Set up Peec for a new client project

```
Set up Peec for example.com — SEO retainer offer, focused on DACH E-Commerce
```

Claude Code invokes `ai-visibility-setup` and walks through all 9 phases: initial audit, competitor discovery from chat history, forum pain-mining, customer-journey prompt design, taxonomy setup, reporting.

### Build a content brief from an underperforming prompt

```
Peec prompt pr_abc123 has 0% visibility — analyze what I need to rank
```

Claude Code invokes `peec-content-intel`: pulls gap-URLs, runs Query Fan-Out, extracts pain-point quotes from forum threads Peec already scraped, scores competitor URLs, outputs a publish-ready content brief.

---

## How the skills work under the hood

Claude Code skills are **markdown workflow definitions** with YAML frontmatter. The AI reads the SKILL.md content as a playbook and orchestrates the tool calls interactively — no additional Python or JavaScript runtime is required.

Both skills reference MCP tools that must exist in your Claude Code environment:

| Tool family | Provider | Example calls used by these skills |
|---|---|---|
| `mcp__peec-ai__*` | Peec AI MCP | `list_projects`, `get_url_report`, `get_chat`, `list_chats`, `get_url_content`, `create_brand`, `create_prompt`, `list_tags` |
| `mcp__visiblyai__*` | Visibly AI MCP (hosted, optional) | `get_google_connections`, `query_search_console`, `get_keywords`, `get_backlinks`, `onpage_analysis`, `classify_keywords`, `query_fanout` |
| `mcp__skillmind__*` | SkillMind MCP (local, optional) | `add_pattern`, `remember`, `recall`, `list_patterns`, `update_memory`, `consolidate`, `export_obsidian` |
| Built-in | Claude Code | `WebSearch`, `WebFetch`, `Read`, `Write`, `Edit`, `Bash` |

If any MCP tool is missing when a skill runs, the skill explicitly states which step is being skipped and continues with the remaining ones.

---

## Design principles

- **Evidence over narrative.** Every prompt, competitor, and content recommendation is grounded in actual AI chat responses (via Peec's scraped history) or forum data — never invented.
- **Funnel-complete.** Prompts are designed across Awareness → Consideration → Decision → Retention; single-stage setups are flagged as a red flag in phase 1.
- **Buyer language.** Forum pain points are quoted verbatim, never paraphrased into marketing-speak.
- **Credit-aware.** Visibly AI and paid MCP calls are budgeted; heuristic fallbacks exist for every credit-costly step.
- **Idempotent.** Re-running a skill on the same project updates without duplicating (uses Peec's content-hash checks and upsert semantics).

---

## Contributing

Found a better prompt template, a new forum to mine, or a scoring formula improvement? PRs welcome.

- Keep SKILL.md files under 600 lines; long appendices go into `skills/<name>/appendix/*.md`.
- Frontmatter must include `name`, `description`, `user-invocable: true`.
- German and English triggers both welcome — German community is primary.

---

## License

MIT © [Antonio Blago](https://antonioblago.de) — Neuro-SEO System®

---

## See also

- [Peec AI](https://app.peec.ai) — the platform these skills integrate with
- [visiblyai-mcp-server](https://pypi.org/project/visiblyai-mcp-server/) — companion MCP server for GSC / backlinks / OnPage data
- [Claude Code skills documentation](https://docs.claude.com/en/docs/claude-code/skills)
