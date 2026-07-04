#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../skills" && pwd)"
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"

echo "Installing skills into Claude Code..."
echo "  Source: $SKILLS_DIR"
echo "  Target: $CLAUDE_SKILLS_DIR"
echo ""

mkdir -p "$CLAUDE_SKILLS_DIR"

installed=0
skipped=0
pruned=0

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  target="$CLAUDE_SKILLS_DIR/$skill_name"

  if [ -L "$target" ]; then
    echo "  ↻ $skill_name (already linked, updating)"
    ln -sfn "$skill_dir" "$target"
    ((skipped++)) || true
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
echo "Done. $installed installed, $skipped skipped, $pruned pruned."

# Install Python dependencies for gitlab-config skill
REQS="$CLAUDE_SKILLS_DIR/gitlab-config/requirements.txt"
if [ -f "$REQS" ]; then
  echo ""
  echo "Installing Python dependencies for gitlab-config..."
  pip install -q -r "$REQS" && echo "  ✓ requests installed" || echo "  ⚠ pip install failed — run manually: pip install requests"
fi

echo ""
echo "Restart Claude Code to pick up new skills."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next: configure GitLab access"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Option 1 — from Claude Code (recommended):"
echo "    Restart Claude Code, then type:"
echo "      /gitlab-config"
echo "    Follow the prompts to add your GitLab instance and token."
echo ""
echo "  Option 2 — manual:"
echo "    cp ~/.claude/skills/gitlab-config/gitlab_config.json.template ~/.gitlab/config.json"
echo "    chmod 600 ~/.gitlab/config.json"
echo "    \# Edit ~/.gitlab/config.json with your GitLab URL and token"
echo "    python ~/.claude/skills/gitlab-config/scripts/gitlab_api.py list-instances"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
