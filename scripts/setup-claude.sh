#!/usr/bin/env bash
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPTS_DIR/../skills" && pwd)"
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"

echo "Installing skills into Claude Code..."
echo "  Source: $SKILLS_DIR"
echo "  Target: $CLAUDE_SKILLS_DIR"
echo ""

source "$SCRIPTS_DIR/lib-progress.sh"

mkdir -p "$CLAUDE_SKILLS_DIR"

installed=0
updated=0
skipped=0
pruned=0

total=0
for skill_dir in "$SKILLS_DIR"/*/; do ((total++)) || true; done

i=0
for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  target="$CLAUDE_SKILLS_DIR/$skill_name"
  ((i++)) || true

  if [ -L "$target" ]; then
    ln -sfn "$skill_dir" "$target"
    ((updated++)) || true
    [ -t 1 ] || echo "  ↻ $skill_name (already linked, updating)"
  elif [ -d "$target" ]; then
    progress_break
    echo "  ⚠ $skill_name (directory exists, not a symlink — skipping)"
    ((skipped++)) || true
  else
    ln -s "$skill_dir" "$target"
    ((installed++)) || true
    [ -t 1 ] || echo "  ✓ $skill_name"
  fi
  progress_bar "$i" "$total" "$skill_name"
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

if [ -n "${ENCORE_SKILLS_STATS_FILE:-}" ]; then
  echo "Claude|$installed|$updated|$skipped|$pruned" >> "$ENCORE_SKILLS_STATS_FILE"
else
  echo ""
  echo "Done. $installed installed, $updated updated, $skipped skipped, $pruned pruned."
fi

# Install Python dependencies for gitlab-config skill
REQS="$CLAUDE_SKILLS_DIR/gitlab-config/requirements.txt"
if [ -f "$REQS" ]; then
  echo ""
  echo "Installing Python dependencies for gitlab-config..."
  pip install -q --disable-pip-version-check -r "$REQS" && echo "  ✓ requests installed" || echo "  ⚠ pip install failed — run manually: pip install requests"
fi

echo ""
echo "Restart Claude Code to pick up new skills."

if [ -z "${ENCORE_SKILLS_STATS_FILE:-}" ]; then
  source "$SCRIPTS_DIR/lib-gitlab-banner.sh"
  print_gitlab_banner "$CLAUDE_SKILLS_DIR" claude
fi
