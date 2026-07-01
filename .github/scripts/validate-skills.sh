#!/usr/bin/env bash
# Validates SKILL.md frontmatter for every skill in skills/
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../skills" && pwd)"
errors=0

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  skill_md="$skill_dir/SKILL.md"

  if [ ! -f "$skill_md" ]; then
    echo "ERROR: $skill_name — no SKILL.md found"
    ((errors++)) || true
    continue
  fi

  # Extract frontmatter fields
  fm_name=$(awk '/^---/{found++; next} found==1 && /^name:/{sub(/^name:[[:space:]]*/, ""); print; exit}' "$skill_md")
  fm_desc=$(awk '/^---/{found++; next} found==1 && /^description:/{sub(/^description:[[:space:]]*/, ""); print; exit}' "$skill_md")
  fm_license=$(awk '/^---/{found++; next} found==1 && /^license:/{sub(/^license:[[:space:]]*/, ""); print; exit}' "$skill_md")
  fm_version=$(awk '/^---/{found++; next} found==1 && /^  version:/{sub(/^[[:space:]]*version:[[:space:]]*/, ""); print; exit}' "$skill_md")

  skill_ok=true

  # name must match folder
  if [ "$fm_name" != "$skill_name" ]; then
    echo "ERROR: $skill_name — name field '$fm_name' does not match folder name '$skill_name'"
    skill_ok=false
  fi

  # description must be present and non-empty
  if [ -z "$fm_desc" ]; then
    echo "ERROR: $skill_name — description field is missing or empty"
    skill_ok=false
  fi

  # description must be under 1024 chars
  desc_len=${#fm_desc}
  if [ "$desc_len" -gt 1024 ]; then
    echo "ERROR: $skill_name — description is $desc_len chars (max 1024)"
    skill_ok=false
  fi

  # license should be present
  if [ -z "$fm_license" ]; then
    echo "WARN:  $skill_name — license field is missing (recommended)"
  fi

  # version should be present
  if [ -z "$fm_version" ]; then
    echo "WARN:  $skill_name — metadata.version field is missing (recommended)"
  fi

  # examples/ directory should exist
  if [ ! -d "$skill_dir/examples" ] || [ -z "$(ls -A "$skill_dir/examples" 2>/dev/null)" ]; then
    echo "WARN:  $skill_name — examples/ directory is missing or empty"
  fi

  if $skill_ok; then
    echo "OK:    $skill_name"
  else
    ((errors++)) || true
  fi
done

echo ""
if [ "$errors" -gt 0 ]; then
  echo "Validation failed: $errors error(s). Fix the above and re-run."
  exit 1
else
  echo "All skills valid."
fi
