#!/usr/bin/env bash
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPTS_DIR/../skills" && pwd)"
TARGET_DIR="${PWD}/.cursor/rules"

echo "Installing skills into Cursor rules..."
echo "  Source: $SKILLS_DIR"
echo "  Target: $TARGET_DIR"
echo ""

mkdir -p "$TARGET_DIR"

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  skill_md="$skill_dir/SKILL.md"

  if [ ! -f "$skill_md" ]; then
    echo "  ⚠ $skill_name — no SKILL.md, skipping"
    continue
  fi

  # Extract description from frontmatter
  description=$(awk '/^---/{found++; next} found==1 && /^description:/{sub(/^description:[[:space:]]*/, ""); print; exit}' "$skill_md")

  # Strip frontmatter from body
  body=$(awk 'BEGIN{found=0} /^---/{found++; if(found==2){skip=0; next} else{skip=1; next}} !skip{print}' "$skill_md")

  target_file="$TARGET_DIR/${skill_name}.mdc"

  cat > "$target_file" <<MDC
---
description: ${description}
globs: []
alwaysApply: false
---

${body}
MDC

  echo "  ✓ $skill_name → .cursor/rules/${skill_name}.mdc"
done

# Prune rule files for skills that no longer exist in the source (e.g. removed skills)
pruned=0
shopt -s nullglob
for target in "$TARGET_DIR"/*.mdc; do
  skill_name="$(basename "$target" .mdc)"
  if [ ! -d "$SKILLS_DIR/$skill_name" ]; then
    rm "$target"
    echo "  ✗ $skill_name.mdc (removed from source, pruned)"
    ((pruned++)) || true
  fi
done
shopt -u nullglob

echo ""
echo "Done. $pruned pruned. Restart Cursor to pick up new rules."
