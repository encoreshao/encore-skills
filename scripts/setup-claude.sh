#!/usr/bin/env bash
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPTS_DIR/../skills" && pwd)"
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"

echo "Installing skills into Claude Code..."
echo "  Source: $SKILLS_DIR"
echo "  Target: $CLAUDE_SKILLS_DIR"
echo ""

mkdir -p "$CLAUDE_SKILLS_DIR"

installed=0
updated=0
skipped=0
pruned=0

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  target="$CLAUDE_SKILLS_DIR/$skill_name"

  if [ -L "$target" ]; then
    echo "  ↻ $skill_name (already linked, updating)"
    ln -sfn "$skill_dir" "$target"
    ((updated++)) || true
  elif [ -d "$target" ]; then
    echo "  ⚠ $skill_name (directory exists, not a symlink — skipping)"
    ((skipped++)) || true
  else
    ln -s "$skill_dir" "$target"
    echo "  ✓ $skill_name"
    ((installed++)) || true
  fi
done

# Prune symlinks for skills that no longer exist in the source (e.g. removed skills)
shopt -s nullglob
for target in "$CLAUDE_SKILLS_DIR"/*; do
  [ -L "$target" ] || continue
  skill_name="$(basename "$target")"
  if [ ! -d "$SKILLS_DIR/$skill_name" ]; then
    rm "$target"
    echo "  ✗ $skill_name (removed from source, pruned)"
    ((pruned++)) || true
  fi
done
shopt -u nullglob

echo ""
echo "Done. $installed installed, $updated updated, $skipped skipped, $pruned pruned."

# Install Python dependencies for gitlab-config skill
REQS="$CLAUDE_SKILLS_DIR/gitlab-config/requirements.txt"
if [ -f "$REQS" ]; then
  echo ""
  echo "Installing Python dependencies for gitlab-config..."
  pip install -q --disable-pip-version-check -r "$REQS" && echo "  ✓ requests installed" || echo "  ⚠ pip install failed — run manually: pip install requests"
fi

echo ""
echo "Restart Claude Code to pick up new skills."

if [ "${ENCORE_SKILLS_SUPPRESS_GITLAB_BANNER:-}" != "1" ]; then
  source "$SCRIPTS_DIR/lib-gitlab-banner.sh"
  print_gitlab_banner "$CLAUDE_SKILLS_DIR" claude
fi
