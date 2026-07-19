#!/usr/bin/env bash
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPTS_DIR/../skills" && pwd)"
TARGET_FILE="${PWD}/AGENTS.md"

# Self-hosted: the project we're installing into IS this repo (or a copy of
# it), so a local skills/ directory sits right next to AGENTS.md — an agent
# reading AGENTS.md can open skills/<name>/SKILL.md on demand, and skills/
# stays the single source of truth. For the general case (installing into an
# unrelated project from a separately-cloned encore-skills checkout, per the
# README), there is no local skills/ and no import syntax in AGENTS.md, so a
# path reference would dangle — we fall back to embedding full content,
# which is self-contained and safe to commit/share with teammates who don't
# have encore-skills installed at all.
SELF_HOSTED=false
if [ -d "${PWD}/skills" ] && [ "$(cd "${PWD}/skills" && pwd)" = "$SKILLS_DIR" ]; then
  SELF_HOSTED=true
fi

echo "Generating AGENTS.md for Codex..."
echo "  Source: $SKILLS_DIR"
echo "  Target: $TARGET_FILE"
if $SELF_HOSTED; then
  echo "  Mode: reference (local skills/ detected — table points at it, no content copied)"
else
  echo "  Mode: embed (no local skills/ — copying full content so AGENTS.md is self-contained)"
fi
echo ""

if $SELF_HOSTED; then
  cat > "$TARGET_FILE" <<'HEADER'
# Available Skills

This project uses the [encore-skills](https://github.com/encoreshao/encore-skills) workflow library.
AGENTS.md has no file-import syntax, so skill instructions are NOT duplicated
here — `skills/` stays the single source of truth. When a task matches a
skill's description below, open its SKILL.md at the given path and follow it
before proceeding.

## Skills

| Skill | Path | When to use |
|-------|------|-------------|
HEADER

  for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name="$(basename "$skill_dir")"
    skill_md="$skill_dir/SKILL.md"

    if [ ! -f "$skill_md" ]; then
      continue
    fi

    description=$(awk '/^---/{found++; next} found==1 && /^description:/{sub(/^description:[[:space:]]*/, ""); print; exit}' "$skill_md")
    echo "| \`${skill_name}\` | \`skills/${skill_name}/SKILL.md\` | ${description} |" >> "$TARGET_FILE"
    echo "  ✓ $skill_name"
  done

  echo "" >> "$TARGET_FILE"
else
  cat > "$TARGET_FILE" <<'HEADER'
# Available Skills

This project uses the [encore-skills](https://github.com/encoreshao/encore-skills) workflow library.
Invoke a skill by name when the task matches its description.

## Skills

| Skill | Role | When to use |
|-------|------|-------------|
HEADER

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
fi

echo ""
echo "Done. AGENTS.md written to $TARGET_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next: configure GitLab access"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Option 1 — from Codex (recommended):"
echo "    In your Codex session, prompt:"
echo "      \"run the gitlab-config skill to set up my GitLab access\""
echo ""
echo "  Option 2 — manual:"
echo "    cp ~/.encore-skills/skills/gitlab-config/gitlab_config.json.template ~/.gitlab/config.json"
echo "    chmod 600 ~/.gitlab/config.json"
echo "    \# Edit ~/.gitlab/config.json with your GitLab URL and token"
echo "    python ~/.encore-skills/skills/gitlab-config/scripts/gitlab_api.py list-instances"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
