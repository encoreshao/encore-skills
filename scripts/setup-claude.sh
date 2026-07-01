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

echo ""
echo "Done. $installed installed, $skipped skipped."

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
echo "Next: set up GitLab access with the gitlab-config skill:"
echo "  cp ~/.claude/skills/gitlab-config/gitlab_config.json.template ~/.gitlab/config.json"
echo "  # Edit ~/.gitlab/config.json with your tokens"
echo "  python ~/.claude/skills/gitlab-config/scripts/gitlab_api.py list-instances"
