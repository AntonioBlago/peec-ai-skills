# Peec AI Skills for Claude Code

Production-tested [Claude Code](https://claude.com/claude-code) skills for **Peec AI** — the brand-visibility tracking platform for LLM-powered search (ChatGPT, Perplexity, Google AI Overviews, Gemini).

These skills turn a freshly-invoked Peec AI project into an operator-ready setup with the right competitors, the right prompts, a proper customer-journey taxonomy, and an actionable content pipeline — using the Peec AI MCP server, Visibly AI (GSC/GA4), and web research.

---

## What's inside

| Skill | What it does | Credits | When to trigger |
|---|---|---|---|
| [`ai-visibility-setup`](skills/ai-visibility-setup/SKILL.md) | End-to-end Peec project configuration: competitor discovery from real AI chats, forum pain-mining (Reddit, Gutefrage, t3n, OMR), customer-journey prompt design across Awareness → Consideration → Decision → Retention, and structured topic/tag taxonomy. 9 phases, fully automated. | free (uses Peec + Visibly MCPs directly) | "Set up Peec for [client]", "My Peec competitors are wrong", "Restructure Peec topics" |
| [`peec-content-intel`](skills/peec-content-intel/SKILL.md) | Content-intelligence workflow: Peec gap-URLs → Query Fan-Out → Reddit/forum pain mining (via Peec's scraped index, bypassing Reddit's WebFetch block) → Visibly backlinks + onpage → opportunity scoring → publish-ready content brief. 6 phases. | ~10–45 Visibly credits per prompt analyzed | "Which content wins Peec prompt X?", "Build a content brief from Peec data" |

Both skills are **user-invocable** — Claude Code will trigger them automatically when the conversation matches, and users can also invoke them explicitly with `/ai-visibility-setup` or `/peec-content-intel`.

---

## Prerequisites

**Required:**
- [Claude Code](https://claude.com/claude-code) (CLI, VS Code extension, or JetBrains plugin)
- Peec AI MCP server connected — [official docs](https://app.peec.ai) (provides `mcp__peec-ai__*` tools)

**Optional but strongly recommended:**
- Visibly AI MCP server connected — [`visiblyai-mcp-server`](https://pypi.org/project/visiblyai-mcp-server/) **≥ v0.6.0** (provides GSC/GA4 read-through, backlinks, onpage-analysis, and — since v0.6.0 — the `query_fanout` coverage analyzer)

Install the Visibly AI MCP locally:
```bash
pip install "visiblyai-mcp-server>=0.6.0"
```

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

- **Without Visibly AI**: both skills still do the Peec-side setup, competitor discovery from chats, Reddit/forum mining via Peec's scraped index, and taxonomy setup. They skip: GSC keyword mapping (Phase 4 of visibility-setup) and coverage analysis (Phase 2 of content-intel). The content brief is still generated, just without the depth/coverage scores.
- **Without `query_fanout` (Visibly MCP < 0.6.0)**: the content-intel skill falls back to an inline Claude-generated 6-axis heuristic (synonym, decision, comparison, problem, long-tail, forum). Coverage matching is skipped.
- **Without `classify_keywords`**: funnel-stage detection drops to keyword pattern matching inside the SKILL.md logic.

---

## Install

### Option A — Global install (affects all Claude Code projects)

```bash
git clone https://github.com/AntonioBlago/peec-ai-skills.git ~/peec-ai-skills

# macOS / Linux
cp -r ~/peec-ai-skills/skills/* ~/.claude/skills/

# Windows (Git Bash / WSL)
cp -r ~/peec-ai-skills/skills/* "$USERPROFILE/.claude/skills/"
```

### Option B — Symlinked (follows updates from `git pull`)

```bash
git clone https://github.com/AntonioBlago/peec-ai-skills.git ~/peec-ai-skills
cd ~/.claude/skills
ln -s ~/peec-ai-skills/skills/ai-visibility-setup ai-visibility-setup
ln -s ~/peec-ai-skills/skills/peec-content-intel peec-content-intel
```

### Option C — Per-project (only this project)

Clone into the project's `.claude/skills/` directory instead of `~/.claude/skills/`.

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
| `mcp__visiblyai__*` | Visibly AI MCP (optional) | `get_google_connections`, `query_search_console`, `get_keywords`, `get_backlinks`, `onpage_analysis`, `classify_keywords`, `query_fanout` |
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
