#!/usr/bin/env bash
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPTS_DIR/../skills" && pwd)"
TARGET_FILE="${PWD}/AGENTS.md"

echo "Generating AGENTS.md for Codex..."
echo "  Source: $SKILLS_DIR"
echo "  Target: $TARGET_FILE"
echo ""

cat > "$TARGET_FILE" <<'HEADER'
# Available Skills

This project uses the [encore-skills](https://github.com/encore/encore-skills) workflow library.
Invoke a skill by name when the task matches its description.

## Skills

| Skill | Role | When to use |
|-------|------|-------------|
HEADER

# Build the table
for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  skill_md="$skill_dir/SKILL.md"

  if [ ! -f "$skill_md" ]; then
    continue
  fi

  description=$(awk '/^---/{found++; next} found==1 && /^description:/{sub(/^description:[[:space:]]*/, ""); print; exit}' "$skill_md")
  echo "| \`${skill_name}\` | — | ${description} |" >> "$TARGET_FILE"
done

echo "" >> "$TARGET_FILE"
echo "---" >> "$TARGET_FILE"
echo "" >> "$TARGET_FILE"

# Append full content for each skill
for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  skill_md="$skill_dir/SKILL.md"

  if [ ! -f "$skill_md" ]; then
    continue
  fi

  description=$(awk '/^---/{found++; next} found==1 && /^description:/{sub(/^description:[[:space:]]*/, ""); print; exit}' "$skill_md")
  body=$(awk 'BEGIN{found=0} /^---/{found++; if(found==2){skip=0; next} else{skip=1; next}} !skip{print}' "$skill_md")

  {
    echo "## Skill: \`${skill_name}\`"
    echo ""
    echo "> ${description}"
    echo ""
    echo "${body}"
    echo ""
    echo "---"
    echo ""
  } >> "$TARGET_FILE"

  echo "  ✓ $skill_name"
done

echo ""
echo "Done. AGENTS.md written to $TARGET_FILE"
