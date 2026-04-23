#!/usr/bin/env python3
"""
peec-detect — shared Peec project detector for the peec-ai-skills hook + /start-peec.

Reads:
  - $CLAUDE_PROJECT_DIR or cwd as the project root
  - <root>/growth_loop/setup_state.json (and up to 2 parent levels)
  - On UserPromptSubmit: stdin JSON {hook_event_name, prompt, ...} — keyword-filtered

Writes to stdout (becomes additionalContext for Claude):
  A short status block + a recommended next-action.
  Silent if neither a state file nor Peec-trigger keywords are present
  (so non-Peec sessions are not polluted).

Exit codes:
  0 — always (never block the user)

Usage in ~/.claude/settings.json:

    {
      "hooks": {
        "UserPromptSubmit": [
          {
            "matcher": "",
            "hooks": [
              { "type": "command",
                "command": "python ~/PycharmProjects/peec-ai-skills/hooks/peec-detect.py" }
            ]
          }
        ],
        "SessionStart": [
          {
            "hooks": [
              { "type": "command",
                "command": "python ~/PycharmProjects/peec-ai-skills/hooks/peec-detect.py --session-start" }
            ]
          }
        ]
      }
    }
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Force UTF-8 stdout so Unicode arrows and Umlauts survive Windows cp1252 consoles.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

TRIGGER_KEYWORDS = {
    # English
    "peec", "ai visibility", "ai-visibility", "growth loop", "growth-loop",
    "citation outreach", "content cluster", "ai search", "llm visibility",
    # German
    "peec ai", "sichtbarkeit", "ki-sichtbarkeit", "ki sichtbarkeit",
    "ai-sichtbarkeit", "ai sichtbarkeit", "wachstumsschleife",
    # Slash-style mentions (helps when user types "@peec" or refers to skills)
    "/ai-visibility-setup", "/ai-growth-agent", "/peec-content-intel",
    "/content-cluster-builder", "/citation-outreach", "/growth-loop-reporter",
    "/start-peec",
}

STATE_FILENAME = "setup_state.json"
STATE_DIR = "growth_loop"
MAX_PARENT_LEVELS = 2


def find_state_file(start: Path) -> Path | None:
    """Walk up at most MAX_PARENT_LEVELS looking for growth_loop/setup_state.json."""
    cur = start.resolve()
    for _ in range(MAX_PARENT_LEVELS + 1):
        candidate = cur / STATE_DIR / STATE_FILENAME
        if candidate.is_file():
            return candidate
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def parse_iso8601(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        # Accept trailing Z by replacing it with +00:00
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def load_state(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def age_days(dt: datetime | None) -> int | None:
    if dt is None:
        return None
    return (datetime.now(timezone.utc) - dt).days


def classify_age(days: int | None) -> str:
    if days is None:
        return "unknown"
    if days < 30:
        return "fresh"
    if days < 90:
        return "stale"
    return "very stale"


def build_state_summary(state: dict[str, Any], state_path: Path) -> str:
    completed_at = parse_iso8601(state.get("completed_at"))
    days = age_days(completed_at)
    age_label = classify_age(days)
    snapshot = state.get("snapshot") or {}
    phases = state.get("phases_completed") or []
    project_id = state.get("peec_project_id", "?")
    domain = state.get("domain", "?")
    lang = state.get("prompt_language", "?")
    country = state.get("target_country", "?")

    next_action = recommend_action(age_label, phases)

    lines = [
        "=== PEEC PROJECT DETECTED ===",
        f"State file:       {state_path}",
        f"Project:          {domain} (peec_project_id={project_id})",
        f"Locale:           country={country} · language={lang}",
        f"Setup age:        {days if days is not None else '?'} days ({age_label})",
        f"Phases completed: {', '.join(phases) if phases else '—'}",
        f"Snapshot:         brands={snapshot.get('brands','?')} · "
        f"prompts={snapshot.get('prompts','?')} · topics={snapshot.get('topics','?')} · "
        f"tags={snapshot.get('tags','?')}",
        "",
        f"RECOMMENDED NEXT ACTION: {next_action}",
        "If the user is here for Peec growth work, immediately invoke the recommended skill.",
        "============================",
    ]
    return "\n".join(lines)


def recommend_action(age_label: str, phases: list[str]) -> str:
    required = {"competitors", "prompts", "topics", "tags"}
    missing = required - set(phases or [])
    if missing:
        return (
            f"/ai-visibility-setup partial:{sorted(missing)[0]} "
            f"— missing phases: {sorted(missing)}"
        )
    if age_label == "very stale":
        return "/ai-visibility-setup audit — setup older than 90 days"
    if age_label == "stale":
        return "/ai-growth-agent (then consider /ai-visibility-setup audit if drift detected)"
    return "/ai-growth-agent — pick the single next move for this cycle"


def build_no_state_hint(reason: str) -> str:
    return "\n".join([
        "=== PEEC CONTEXT ===",
        f"No setup_state.json found (reason: {reason}).",
        "",
        "RECOMMENDED NEXT ACTION: /start-peec",
        "  → if Peec project exists with brands/prompts → import mode (no destructive setup)",
        "  → if greenfield → run /ai-visibility-setup full",
        "===================",
    ])


def is_session_start(argv: list[str]) -> bool:
    return "--session-start" in argv


def read_stdin_event() -> dict[str, Any] | None:
    """UserPromptSubmit hooks receive a JSON event on stdin."""
    if sys.stdin.isatty():
        return None
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return None
        return json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return None


def prompt_mentions_peec(prompt: str) -> bool:
    if not prompt:
        return False
    low = prompt.lower()
    return any(k in low for k in TRIGGER_KEYWORDS)


def emit_context(text: str, event_name: str) -> None:
    """
    Emit Claude Code hook output as JSON envelope.

    Per hook schema, additionalContext under hookSpecificOutput is the documented
    way to inject text into the model context. Raw stdout is event-dependent and
    less reliable. Always wrap.
    """
    payload = {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": text,
        }
    }
    json.dump(payload, sys.stdout, ensure_ascii=False)


def extract_prompt(event: dict[str, Any]) -> str:
    """Hook stdin uses different field names across versions — check both."""
    return event.get("prompt") or event.get("user_prompt") or ""


def main() -> int:
    session_start = is_session_start(sys.argv[1:])
    event = read_stdin_event() if not session_start else None
    event_name = "SessionStart" if session_start else "UserPromptSubmit"

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    state_path = find_state_file(Path(project_dir))

    if state_path:
        state = load_state(state_path)
        if state:
            emit_context(build_state_summary(state, state_path), event_name)
            return 0

    # No state file. Decide whether to be loud or silent.
    if session_start:
        # Silent on SessionStart with no state — don't pollute non-Peec sessions.
        return 0

    # UserPromptSubmit path: only speak up if the prompt mentions Peec.
    if event and prompt_mentions_peec(extract_prompt(event)):
        emit_context(
            build_no_state_hint("prompt mentions Peec but no state file in CWD"),
            event_name,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
