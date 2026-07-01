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
echo "=== Updating Claude Code ==="
bash "$SCRIPTS_DIR/setup-claude.sh"
echo ""

echo "✓ Claude Code updated."
echo ""
echo "If you use Cursor or Codex, re-run inside each project:"
echo "  ./scripts/setup.sh --cursor   # regenerate .cursor/rules/*.mdc"
echo "  ./scripts/setup.sh --codex    # regenerate AGENTS.md"
