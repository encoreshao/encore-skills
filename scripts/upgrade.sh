#!/usr/bin/env bash
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
REPO_DIR="$(cd "$SCRIPTS_DIR/.." && pwd)"

echo "Upgrading encore-skills..."
echo ""

# Pull latest from remote
cd "$REPO_DIR"
if git remote get-url origin &>/dev/null; then
  echo "Pulling latest from origin..."
  git pull origin "$(git rev-parse --abbrev-ref HEAD)"
  echo ""
else
  echo "No remote configured — skipping git pull."
  echo ""
fi

# Re-run Claude install (picks up any new skill directories)
STATS_FILE="$(mktemp)"
trap 'rm -f "$STATS_FILE"' EXIT
export ENCORE_SKILLS_STATS_FILE="$STATS_FILE"

echo "=== Updating Claude Code ==="
bash "$SCRIPTS_DIR/setup-claude.sh"
echo ""

SKILLS_DIR="$(cd "$SCRIPTS_DIR/../skills" && pwd)"
source "$SCRIPTS_DIR/lib-summary-table.sh"
print_summary_table "$STATS_FILE"

source "$SCRIPTS_DIR/lib-gitlab-banner.sh"
print_gitlab_banner "$SKILLS_DIR" claude

echo "✓ Claude Code updated."
echo ""
echo "If you use Cursor or Codex, re-run inside each project:"
echo "  ./scripts/setup.sh --cursor   # regenerate .cursor/rules/*.mdc"
echo "  ./scripts/setup.sh --codex    # regenerate AGENTS.md"
