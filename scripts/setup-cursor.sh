#!/usr/bin/env bash
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPTS_DIR/../skills" && pwd)"
TARGET_DIR="${PWD}/.cursor/rules"

# Self-hosted: the project we're installing into IS this repo (or a copy of
# it), so a local skills/ directory sits right next to .cursor/. In that case
# reference the canonical SKILL.md via Cursor's @-mention instead of copying
# it, so skills/ stays the single source of truth. For the general case
# (installing into an unrelated project from a separately-cloned encore-skills
# checkout, per the README), there is no local skills/ to reference — Cursor
# resolves @-mentions relative to the current workspace root, not to this
# script's location — so we fall back to embedding the full content, which is
# self-contained and safe to commit/share with teammates who don't have
# encore-skills installed at all.
SELF_HOSTED=false
if [ -d "${PWD}/skills" ] && [ "$(cd "${PWD}/skills" && pwd)" = "$SKILLS_DIR" ]; then
  SELF_HOSTED=true
fi

echo "Installing skills into Cursor rules..."
echo "  Source: $SKILLS_DIR"
echo "  Target: $TARGET_DIR"
if $SELF_HOSTED; then
  echo "  Mode: reference (local skills/ detected — rules point at it, no content copied)"
else
  echo "  Mode: embed (no local skills/ — copying full content so rules are self-contained)"
fi
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

  target_file="$TARGET_DIR/${skill_name}.mdc"

  if $SELF_HOSTED; then
    cat > "$target_file" <<MDC
---
description: ${description}
globs: []
alwaysApply: false
---

@skills/${skill_name}/SKILL.md
MDC
  else
    # Strip frontmatter from body
    body=$(awk 'BEGIN{found=0} /^---/{found++; if(found==2){skip=0; next} else{skip=1; next}} !skip{print}' "$skill_md")

    cat > "$target_file" <<MDC
---
description: ${description}
globs: []
alwaysApply: false
---

${body}
MDC
  fi

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
