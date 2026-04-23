#!/usr/bin/env bash
# claude-peec-ai.sh — install Peec AI skills into Claude Code.
#
# Usage:
#   ./claude-peec-ai.sh                # symlink into ~/.claude/skills/
#   ./claude-peec-ai.sh --copy         # copy instead of symlink
#   ./claude-peec-ai.sh --target DIR   # install into DIR/skills/ (e.g. a project-local .claude)
#   ./claude-peec-ai.sh --force        # overwrite existing skill dirs/links
#   ./claude-peec-ai.sh --dry-run      # show what would happen, touch nothing
#   ./claude-peec-ai.sh --uninstall    # remove the 6 skill entries from the target
#   ./claude-peec-ai.sh --only NAME[,NAME...]   # restrict to specific skills
#
# Symlink mode needs either Developer Mode or admin rights on Windows.
# On WSL / Git Bash it usually just works if the target is on the same drive.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/skills"

MODE="symlink"
TARGET=""
FORCE=0
DRY_RUN=0
UNINSTALL=0
ONLY=""

SKILLS=(
  ai-visibility-setup
  peec-content-intel
  content-cluster-builder
  citation-outreach
  growth-loop-reporter
  skillmind-learner
  ai-growth-agent
  start-peec
  peec-checkup
)

c_reset=$'\033[0m'
c_green=$'\033[32m'
c_yellow=$'\033[33m'
c_red=$'\033[31m'
c_dim=$'\033[2m'

log()  { printf '%s\n' "$*"; }
ok()   { printf '%s✓%s %s\n' "$c_green" "$c_reset" "$*"; }
warn() { printf '%s!%s %s\n' "$c_yellow" "$c_reset" "$*"; }
err()  { printf '%s✗%s %s\n' "$c_red" "$c_reset" "$*" >&2; }
dim()  { printf '%s%s%s\n' "$c_dim" "$*" "$c_reset"; }

usage() { sed -n '2,15p' "$0"; exit "${1:-0}"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy)      MODE="copy";       shift ;;
    --symlink)   MODE="symlink";    shift ;;
    --target)    TARGET="${2:?--target needs a path}"; shift 2 ;;
    --force)     FORCE=1;           shift ;;
    --dry-run)   DRY_RUN=1;         shift ;;
    --uninstall) UNINSTALL=1;       shift ;;
    --only)      ONLY="${2:?--only needs a comma-separated list}"; shift 2 ;;
    -h|--help)   usage 0 ;;
    *) err "unknown flag: $1"; usage 1 ;;
  esac
done

# Resolve target skills directory.
if [[ -z "$TARGET" ]]; then
  TARGET="${CLAUDE_HOME:-$HOME/.claude}"
fi
DEST_DIR="$TARGET/skills"

# Filter skills if --only was given.
if [[ -n "$ONLY" ]]; then
  IFS=',' read -r -a want <<< "$ONLY"
  filtered=()
  for s in "${SKILLS[@]}"; do
    for w in "${want[@]}"; do
      [[ "$s" == "$w" ]] && filtered+=("$s") && break
    done
  done
  if [[ ${#filtered[@]} -eq 0 ]]; then
    err "none of the requested skills exist in this repo: $ONLY"
    err "available: ${SKILLS[*]}"
    exit 1
  fi
  SKILLS=("${filtered[@]}")
fi

run() {
  if [[ $DRY_RUN -eq 1 ]]; then
    dim "    would: $*"
  else
    "$@"
  fi
}

log "source : $SRC_DIR"
log "target : $DEST_DIR"
log "mode   : $([[ $UNINSTALL -eq 1 ]] && echo uninstall || echo "$MODE")"
[[ $DRY_RUN -eq 1 ]] && warn "dry-run: no filesystem changes"
echo

if [[ $UNINSTALL -eq 1 ]]; then
  for name in "${SKILLS[@]}"; do
    dest="$DEST_DIR/$name"
    if [[ -L "$dest" || -e "$dest" ]]; then
      run rm -rf "$dest"
      ok "removed $name"
    else
      dim "    skip   $name (not installed)"
    fi
  done
  exit 0
fi

if [[ ! -d "$SRC_DIR" ]]; then
  err "source skills dir missing: $SRC_DIR"
  exit 1
fi
run mkdir -p "$DEST_DIR"

installed=0; skipped=0; failed=0

for name in "${SKILLS[@]}"; do
  src="$SRC_DIR/$name"
  dest="$DEST_DIR/$name"

  if [[ ! -d "$src" ]]; then
    err "$name: source missing at $src"
    failed=$((failed+1))
    continue
  fi
  if [[ ! -f "$src/SKILL.md" ]]; then
    err "$name: no SKILL.md in $src"
    failed=$((failed+1))
    continue
  fi

  if [[ -L "$dest" || -e "$dest" ]]; then
    if [[ $FORCE -eq 1 ]]; then
      run rm -rf "$dest"
    else
      warn "$name: already present, use --force to overwrite"
      skipped=$((skipped+1))
      continue
    fi
  fi

  if [[ "$MODE" == "symlink" ]]; then
    if run ln -s "$src" "$dest" 2>/dev/null; then
      ok "linked   $name"
      installed=$((installed+1))
    else
      warn "$name: symlink failed, falling back to copy"
      if run cp -r "$src" "$dest"; then
        ok "copied   $name (fallback)"
        installed=$((installed+1))
      else
        err "$name: copy failed"
        failed=$((failed+1))
      fi
    fi
  else
    if run cp -r "$src" "$dest"; then
      ok "copied   $name"
      installed=$((installed+1))
    else
      err "$name: copy failed"
      failed=$((failed+1))
    fi
  fi
done

echo
log "summary: $installed installed · $skipped skipped · $failed failed"
[[ $failed -gt 0 ]] && exit 1 || exit 0
