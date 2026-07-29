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

source "$SCRIPTS_DIR/lib-progress.sh"

mkdir -p "$TARGET_DIR"

created=0
updated=0
skipped=0

total=0
for skill_dir in "$SKILLS_DIR"/*/; do ((total++)) || true; done

i=0
for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  skill_md="$skill_dir/SKILL.md"
  ((i++)) || true

  if [ ! -f "$skill_md" ]; then
    progress_break
    echo "  ⚠ $skill_name — no SKILL.md, skipping"
    ((skipped++)) || true
    progress_bar "$i" "$total" "$skill_name"
    continue
  fi

  # Extract description from frontmatter
  description=$(awk '/^---/{found++; next} found==1 && /^description:/{sub(/^description:[[:space:]]*/, ""); print; exit}' "$skill_md")

  target_file="$TARGET_DIR/${skill_name}.mdc"
  existed=false
  if [ -f "$target_file" ]; then existed=true; fi

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

  if $existed; then ((updated++)) || true; else ((created++)) || true; fi
  [ -t 1 ] || echo "  ✓ $skill_name → .cursor/rules/${skill_name}.mdc"
  progress_bar "$i" "$total" "$skill_name"
done

# Prune rule files for skills that no longer exist in the source (e.g. removed skills)
pruned=0
shopt -s nullglob
for target in "$TARGET_DIR"/*.mdc; do
  skill_name="$(basename "$target" .mdc)"
  if [ ! -d "$SKILLS_DIR/$skill_name" ]; then
    rm "$target"
    progress_break
    echo "  ✗ $skill_name.mdc (removed from source, pruned)"
    ((pruned++)) || true
  fi
done
shopt -u nullglob

if [ -n "${ENCORE_SKILLS_STATS_FILE:-}" ]; then
  echo "Cursor|$created|$updated|$skipped|$pruned" >> "$ENCORE_SKILLS_STATS_FILE"
else
  echo ""
  echo "Done. $created created, $updated updated, $skipped skipped, $pruned pruned. Restart Cursor to pick up new rules."
fi

if [ -z "${ENCORE_SKILLS_STATS_FILE:-}" ]; then
  source "$SCRIPTS_DIR/lib-gitlab-banner.sh"
  print_gitlab_banner "$SKILLS_DIR" cursor
fi
