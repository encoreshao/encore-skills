# Workflow Skills Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a portable GitLab-focused skills library (6 skills + 3 setup scripts) that installs into Claude Code, Cursor, and Codex with a single command.

**Architecture:** Single canonical `SKILL.md` per skill under `skills/`. Setup scripts transform and install into each tool's native format. No runtime dependencies — pure bash + standard Unix tools.

**Tech Stack:** Bash scripts, Markdown (SKILL.md), YAML frontmatter, GitLab CLI (`glab`, optional)

## Global Constraints

- All setup scripts: bash only, no Node/Python/Ruby required
- Skills: self-contained, no inter-skill dependencies (except `workflow`)
- GitLab CLI (`glab`) is optional — always provide a manual fallback
- No internet required at skill-invocation time
- SKILL.md frontmatter fields: `name`, `description` (required); `triggers` (optional list)

---

## File Map

```
encore-skills/
  skills/
    write-issue/SKILL.md        # PM: rough idea → structured GitLab issue
    analyze-issue/SKILL.md      # Dev/PM: GitLab issue → requirements + plan
    fix-issue/SKILL.md          # Dev: implement following human-thinking loop
    review-code/SKILL.md        # Dev/Lead: pre-MR review
    create-mr/SKILL.md          # Dev: create GitLab MR
    workflow/SKILL.md           # All: full loop orchestrator
  scripts/
    setup.sh                    # Main entry point (delegates to below)
    setup-claude.sh             # Symlinks skills/ → ~/.claude/skills/
    setup-cursor.sh             # Generates .cursor/rules/*.mdc in cwd
    setup-codex.sh              # Generates AGENTS.md in cwd
  CLAUDE.md                     # Claude context for this repo
  AGENTS.md                     # Pre-generated Codex manifest
  README.md
  docs/
    superpowers/
      specs/2026-07-01-workflow-skills-design.md
      plans/2026-07-01-workflow-skills-library.md  (this file)
```

---

### Task 1: Repo scaffolding

**Files:**
- Create: `README.md`
- Create: `CLAUDE.md`
- Create: `skills/.gitkeep` (placeholder until skills are added)

**Interfaces:**
- Produces: working git repo with base structure

- [ ] **Step 1: Initialize git repo and create directory structure**

```bash
cd /Users/encore/Dev/Github/encore-skills
git init
mkdir -p skills scripts docs/superpowers/specs docs/superpowers/plans
```

- [ ] **Step 2: Write README.md**

```markdown
# encore-skills

A portable workflow skills library for GitLab-focused development. Works with Claude Code, Cursor, and Codex.

## Skills

| Skill | Role | Purpose |
|-------|------|---------|
| `write-issue` | PM | Turn a rough idea into a structured GitLab issue |
| `analyze-issue` | Dev / PM | Read an issue → requirements, risks, implementation plan |
| `fix-issue` | Dev | Implement following the human-thinking loop |
| `review-code` | Dev / Lead | Pre-MR code review |
| `create-mr` | Dev | Create a GitLab Merge Request |
| `workflow` | All | Full loop: analyze → fix → review → create-mr |

## Install

```bash
# Claude Code (global)
./scripts/setup.sh --claude

# Cursor (project-level, run inside your project)
./scripts/setup.sh --cursor

# Codex (project-level, run inside your project)
./scripts/setup.sh --codex

# All at once
./scripts/setup.sh --all
```

## One-liner install (Claude Code)

```bash
curl -fsSL https://raw.githubusercontent.com/encore/encore-skills/main/scripts/setup.sh | bash -s -- --claude
```

## Workflow loop

```
write-issue → analyze-issue → fix-issue → review-code → create-mr
      ↑                                                        |
      └────────────── feedback / new issue ────────────────────┘
```
```

Save to `README.md`.

- [ ] **Step 3: Write CLAUDE.md**

```markdown
# encore-skills

This repo contains workflow skills for Claude Code, Cursor, and Codex.

## Structure

- `skills/` — canonical skill sources (one directory per skill, each with SKILL.md)
- `scripts/` — setup scripts for each tool
- `docs/` — specs and plans

## Adding a skill

1. Create `skills/<name>/SKILL.md` with frontmatter: `name`, `description`
2. Run `./scripts/setup.sh --claude` to install into Claude Code
3. Run `./scripts/setup-cursor.sh` and `./scripts/setup-codex.sh` to regenerate adapter files

## Skills follow the human-thinking workflow

Understand → Plan → Implement → Validate → Ship or Loop
```

Save to `CLAUDE.md`.

- [ ] **Step 4: Initial commit**

```bash
git add README.md CLAUDE.md docs/
git commit -m "chore: initial repo scaffold"
```

Expected: commit succeeds, `git log --oneline` shows 1 commit.

---

### Task 2: write-issue skill

**Files:**
- Create: `skills/write-issue/SKILL.md`

**Interfaces:**
- Produces: `skills/write-issue/SKILL.md` (consumed by setup scripts in Tasks 8–11)

- [ ] **Step 1: Write skills/write-issue/SKILL.md**

```markdown
---
name: write-issue
description: Turn a rough idea into a well-structured GitLab issue ready to copy-paste or create via glab
---

# Write Issue

Use when you have a rough idea, feature request, or bug report and need to turn it into a proper GitLab issue.

## Steps

### 1. Understand the rough idea
Ask if unclear: What problem does this solve? Who is affected? Is this a bug, feature, or improvement?

### 2. Draft the issue

Structure:

**Title:** `[Type] Short imperative description` (e.g., `[Bug] Login fails when email has uppercase`, `[Feature] Add CSV export to reports`)

**Description:**
```
## Background
Why does this matter? What's the current situation?

## What / Why
What should happen? Why is this the right solution?

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] ...

## Out of scope
What this issue does NOT cover.
```

**Labels:** suggest based on content (e.g., `bug`, `feature`, `backend`, `frontend`, `design`)

**Assignee:** ask who should own this

**Milestone:** ask which milestone/sprint

### 3. Present the draft
Show the full issue text and ask: "Does this look right? Anything to add or change?"

### 4. Create the issue

If `glab` is available:
```bash
glab issue create --title "TITLE" --description "DESCRIPTION" --label "LABELS"
```

Otherwise: output the formatted issue text ready to paste into GitLab.
```

- [ ] **Step 2: Verify file content**

```bash
cat skills/write-issue/SKILL.md
```

Expected: file exists, frontmatter has `name: write-issue` and `description` field.

- [ ] **Step 3: Commit**

```bash
git add skills/write-issue/SKILL.md
git commit -m "feat: add write-issue skill"
```

---

### Task 3: analyze-issue skill

**Files:**
- Create: `skills/analyze-issue/SKILL.md`

**Interfaces:**
- Produces: `skills/analyze-issue/SKILL.md`
- Produces: structured analysis format (consumed conceptually by `fix-issue` and `workflow`)

- [ ] **Step 1: Write skills/analyze-issue/SKILL.md**

```markdown
---
name: analyze-issue
description: Read a GitLab issue and produce a structured analysis — requirements, risks, unknowns, and implementation approach — before any coding begins
---

# Analyze Issue

Use at the start of any development task. Run this before writing a single line of code.

## Input
Provide one of:
- GitLab issue URL (e.g., `https://gitlab.com/org/repo/-/issues/42`)
- Issue number (e.g., `#42`) — must be run inside the repo
- Paste the issue text directly

## Steps

### 1. Fetch the issue

If `glab` is available and inside the repo:
```bash
glab issue view <number>
```
Otherwise read from pasted content or URL.

### 2. Extract requirements
List every explicit requirement from the description and acceptance criteria. Be literal — don't infer.

### 3. Identify risks
- What existing code does this touch? (check with `grep`, file search)
- What could break?
- Are there performance, security, or data concerns?
- Does this affect any API contracts or database schemas?

### 4. Surface unknowns
List questions that must be answered before coding. Flag anything missing from the spec.

### 5. Propose implementation approach
- 2–3 sentence summary of the approach
- Files likely to be created or changed (check the codebase)
- Rough complexity: small / medium / large

### 6. Output the analysis

```
## Issue Analysis: #<number> — <title>

### Requirements
- [ ] ...

### Risks
- [ ] Risk: ... → Mitigation: ...

### Unknowns (resolve before coding)
- [ ] ...

### Approach
<2–3 sentences>

### Files likely affected
- `path/to/file.rb` — reason
- ...

### Ready to code?
[ ] Yes — no blockers
[ ] No — blockers: ...
```

### 7. Confirm before proceeding
Ask: "Does this analysis look complete? Shall I start on the implementation?"
```

- [ ] **Step 2: Verify**

```bash
cat skills/analyze-issue/SKILL.md | head -5
```

Expected: first line is `---`, second line is `name: analyze-issue`.

- [ ] **Step 3: Commit**

```bash
git add skills/analyze-issue/SKILL.md
git commit -m "feat: add analyze-issue skill"
```

---

### Task 4: fix-issue skill

**Files:**
- Create: `skills/fix-issue/SKILL.md`

**Interfaces:**
- Consumes: output format from `analyze-issue` (requirements, risks, approach)
- Produces: `skills/fix-issue/SKILL.md`

- [ ] **Step 1: Write skills/fix-issue/SKILL.md**

```markdown
---
name: fix-issue
description: Implement a GitLab issue following the human-thinking loop — understand, plan, implement, identify risks, validate, ship or loop
---

# Fix Issue

Use after analyze-issue. Implements a fix following human thinking, not just "write code and hope".

## Input
- Analysis from `analyze-issue` (or paste issue details directly)
- Current branch (should be a feature branch, not main/master)

## Loop: Understand → Plan → Implement → Validate → Ship or Repeat

### Phase 1: Understand
Re-read the requirements and risks from the analysis. If no analysis exists, run `analyze-issue` first.

Confirm:
- Branch is not `main` or `master` — if it is, create a feature branch: `git checkout -b feat/<issue-number>-<short-description>`
- You know which files to touch

### Phase 2: Plan
Before writing code, write a brief plan (2–5 bullet points):
- What you will change and why
- What you will NOT change (scope boundary)
- Any tricky parts to watch for

Show the plan and ask: "Does this approach look right before I start?"

### Phase 3: Implement
Write the code. Follow existing patterns — check nearby files first.

Rules:
- One concern per commit — don't bundle unrelated changes
- Write tests alongside implementation, not after
- If you find a bug unrelated to this issue, note it but do NOT fix it here

### Phase 4: Identify risks
After implementing, check:
- Did you introduce any security issues? (SQL injection, XSS, auth bypass, secrets in code)
- Did you break any existing tests? Run `git stash && <test command> && git stash pop` to check baseline
- Did you change any API contracts or database schemas without a migration?
- Are there edge cases not covered by the acceptance criteria?

Flag any risk found. For high-severity risks, stop and ask before continuing.

### Phase 5: Validate
- Run tests: verify they pass
- Re-read the acceptance criteria — check each one manually
- Check: does the implementation match the approach from Phase 2?

### Phase 6: Ship or Loop
If all acceptance criteria are met and no unresolved risks: proceed to `review-code` or `create-mr`.

If something is off:
- Unmet criterion → go back to Phase 3
- New risk discovered → go back to Phase 2 (update the plan)
- Scope creep identified → open a new issue, stay focused here

## Commit convention
```bash
git commit -m "type(scope): description

Closes #<issue-number>"
```

Types: `feat`, `fix`, `refactor`, `test`, `chore`, `docs`
```

- [ ] **Step 2: Verify**

```bash
cat skills/fix-issue/SKILL.md | grep "^name:"
```

Expected: `name: fix-issue`

- [ ] **Step 3: Commit**

```bash
git add skills/fix-issue/SKILL.md
git commit -m "feat: add fix-issue skill"
```

---

### Task 5: review-code skill

**Files:**
- Create: `skills/review-code/SKILL.md`

**Interfaces:**
- Produces: `skills/review-code/SKILL.md`
- Produces: structured review output (consumed by `workflow`)

- [ ] **Step 1: Write skills/review-code/SKILL.md**

```markdown
---
name: review-code
description: Pre-MR code review — security, logic, best practices, test coverage, GitLab CI. Run before creating an MR.
---

# Review Code

Use before creating a Merge Request. Catches issues before they reach reviewers.

## Input
- Current diff: `git diff main` or `git diff origin/main`
- Or a GitLab MR URL: `glab mr view <number>`

## Review checklist

### 1. Security
- [ ] No secrets, tokens, or credentials in code or comments
- [ ] SQL queries use parameterized inputs (no string interpolation)
- [ ] User input is validated and sanitized before use
- [ ] Auth/permission checks are present on new endpoints
- [ ] No `eval`, `exec`, or equivalent with user-controlled input

### 2. Logic and correctness
- [ ] Does the implementation match the issue's acceptance criteria?
- [ ] Are edge cases handled? (empty inputs, nulls, large values, concurrent requests)
- [ ] Are error cases handled and logged appropriately?
- [ ] No obvious off-by-one errors or boundary mistakes

### 3. Code quality
- [ ] Follows existing patterns in the codebase (check nearby files)
- [ ] No dead code or commented-out code left in
- [ ] Naming is clear and consistent
- [ ] No unnecessary complexity — simplest solution that works

### 4. Tests
- [ ] New behavior has test coverage
- [ ] Tests test behavior, not implementation details
- [ ] No tests that always pass regardless of code

### 5. GitLab CI
- [ ] Pipeline passes (check `.gitlab-ci.yml` for relevant jobs)
- [ ] No new linter warnings introduced
- [ ] Database migrations are reversible (if applicable)

## Output format

```
## Code Review: <branch or MR>

### ✅ Looks good
- ...

### ⚠️ Suggestions (non-blocking)
- ...

### ❌ Must fix before merge
- ...

### Verdict
[ ] Ready to merge
[ ] Needs changes (see ❌ above)
```

## After review
- If "Ready to merge": proceed to `create-mr`
- If "Needs changes": go back to `fix-issue` Phase 3
```

- [ ] **Step 2: Verify**

```bash
grep "^name:" skills/review-code/SKILL.md
```

Expected: `name: review-code`

- [ ] **Step 3: Commit**

```bash
git add skills/review-code/SKILL.md
git commit -m "feat: add review-code skill"
```

---

### Task 6: create-mr skill

**Files:**
- Create: `skills/create-mr/SKILL.md`

**Interfaces:**
- Produces: `skills/create-mr/SKILL.md`

- [ ] **Step 1: Write skills/create-mr/SKILL.md**

```markdown
---
name: create-mr
description: Create a GitLab Merge Request with a proper description, linked issue, and checklist. Supports glab CLI and manual fallback.
---

# Create MR

Use after `review-code` passes. Creates a well-formed GitLab Merge Request.

## Pre-flight checks

```bash
# Ensure branch is up to date
git fetch origin
git log origin/main..HEAD --oneline   # see what commits will be in the MR

# Ensure CI is passing (if pipeline already ran)
glab pipeline status 2>/dev/null || echo "Check CI manually in GitLab"
```

## Draft the MR description

Template:
```
## What
<1–3 sentences: what changed and why>

## How
<Brief explanation of implementation approach>

## Testing
- [ ] Unit tests pass
- [ ] Manually tested: <describe what you tested>
- [ ] Edge cases considered: <list them>

## Checklist
- [ ] Linked to issue
- [ ] No secrets in code
- [ ] Migration is reversible (if applicable)
- [ ] Documentation updated (if applicable)

Closes #<issue-number>
```

## Create the MR

### With glab (preferred)
```bash
glab mr create \
  --title "feat: <short description>" \
  --description "$(cat mr-description.md)" \
  --assignee @me \
  --label "ready for review" \
  --remove-source-branch
```

### Without glab (manual)
1. Push branch: `git push -u origin HEAD`
2. GitLab will print a URL to create the MR — open it
3. Paste the description template above
4. Set: assignee, reviewer, labels, milestone
5. Check "Delete source branch when merged"
6. Click "Create merge request"

## After creating
Output the MR URL and ask: "MR created. Shall I notify anyone or update the issue?"

If the issue should be updated with a progress comment:
```bash
glab issue note <number> --message "MR created: <MR URL>"
```
```

- [ ] **Step 2: Verify**

```bash
grep "^name:" skills/create-mr/SKILL.md
```

Expected: `name: create-mr`

- [ ] **Step 3: Commit**

```bash
git add skills/create-mr/SKILL.md
git commit -m "feat: add create-mr skill"
```

---

### Task 7: workflow skill

**Files:**
- Create: `skills/workflow/SKILL.md`

**Interfaces:**
- Consumes: conceptually references all other skills
- Produces: `skills/workflow/SKILL.md`

- [ ] **Step 1: Write skills/workflow/SKILL.md**

```markdown
---
name: workflow
description: Full GitLab development loop — from issue to merged MR. Orchestrates write-issue, analyze-issue, fix-issue, review-code, create-mr.
---

# Workflow

Full development loop. Start here when beginning any task from scratch, or jump in at any phase.

## The loop

```
write-issue → analyze-issue → fix-issue → review-code → create-mr
      ↑                                                        |
      └──────── new issue from feedback ──────────────────────┘
```

Each phase follows human thinking:
1. **Understand** — what is the problem exactly?
2. **Plan** — how to approach it, what are the risks?
3. **Implement** — do the work
4. **Validate** — does it meet requirements? new risks?
5. **Ship or loop** — merge or go back

## Entry points

**Starting from a rough idea:**
→ Begin at `write-issue`

**Starting from an existing GitLab issue:**
→ Begin at `analyze-issue`

**Already have analysis, ready to code:**
→ Begin at `fix-issue`

**Code done, ready to ship:**
→ Begin at `review-code`

## Phase guide

### Phase 0: Write Issue (PM role)
*Skip if issue already exists.*

Use the `write-issue` skill to turn a rough idea into a structured GitLab issue with acceptance criteria.

Output: GitLab issue number (e.g., `#42`)

---

### Phase 1: Analyze Issue (Dev / PM)
Use the `analyze-issue` skill.

Input: issue number or URL
Output: requirements list, risks, unknowns, implementation approach

**Gate:** Do not proceed to Phase 2 until all unknowns are resolved.

---

### Phase 2: Fix Issue (Dev)
Use the `fix-issue` skill.

Follow the loop: Understand → Plan → Implement → Validate → Ship or Repeat

**Gate:** All acceptance criteria checked off. No unresolved ❌ risks.

---

### Phase 3: Review Code (Dev / Lead)
Use the `review-code` skill.

Input: `git diff main` or MR URL
Output: review verdict (Ready / Needs Changes)

**Gate:** Verdict is "Ready to merge". If "Needs Changes" → back to Phase 2.

---

### Phase 4: Create MR (Dev)
Use the `create-mr` skill.

Output: MR URL

---

### Phase 5: After merge
- Close the issue if not auto-closed via `Closes #<number>`
- Delete the feature branch (or let GitLab do it automatically)
- If the MR review revealed new issues → open new issues and start the loop again

## Tips
- Keep issues small — one concern per issue, one MR per issue
- If scope grows during Phase 2, open a new issue for the extra work
- The loop is not a failure — looping means you caught something before it reached production
```

- [ ] **Step 2: Verify**

```bash
grep "^name:" skills/workflow/SKILL.md
```

Expected: `name: workflow`

- [ ] **Step 3: Commit**

```bash
git add skills/workflow/SKILL.md
git commit -m "feat: add workflow orchestrator skill"
```

---

### Task 8: setup-claude.sh

**Files:**
- Create: `scripts/setup-claude.sh`

**Interfaces:**
- Produces: symlinks at `~/.claude/skills/<name>` for each skill directory

- [ ] **Step 1: Write scripts/setup-claude.sh**

```bash
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
echo "Restart Claude Code to pick up new skills."
```

- [ ] **Step 2: Make executable**

```bash
chmod +x scripts/setup-claude.sh
```

- [ ] **Step 3: Verify the script**

```bash
bash -n scripts/setup-claude.sh && echo "Syntax OK"
```

Expected: `Syntax OK`

- [ ] **Step 4: Dry-run test**

```bash
# Preview what it would do without running it
ls skills/
```

Expected: shows all 6 skill directories.

- [ ] **Step 5: Commit**

```bash
git add scripts/setup-claude.sh
git commit -m "feat: add setup-claude.sh install script"
```

---

### Task 9: setup-cursor.sh

**Files:**
- Create: `scripts/setup-cursor.sh`

**Interfaces:**
- Produces: `.cursor/rules/<name>.mdc` files in the current working directory

- [ ] **Step 1: Write scripts/setup-cursor.sh**

```bash
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

echo ""
echo "Done. Restart Cursor to pick up new rules."
```

- [ ] **Step 2: Make executable**

```bash
chmod +x scripts/setup-cursor.sh
```

- [ ] **Step 3: Verify syntax**

```bash
bash -n scripts/setup-cursor.sh && echo "Syntax OK"
```

Expected: `Syntax OK`

- [ ] **Step 4: Commit**

```bash
git add scripts/setup-cursor.sh
git commit -m "feat: add setup-cursor.sh install script"
```

---

### Task 10: setup-codex.sh

**Files:**
- Create: `scripts/setup-codex.sh`

**Interfaces:**
- Produces: `AGENTS.md` in the current working directory

- [ ] **Step 1: Write scripts/setup-codex.sh**

```bash
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
```

- [ ] **Step 2: Make executable**

```bash
chmod +x scripts/setup-codex.sh
```

- [ ] **Step 3: Verify syntax**

```bash
bash -n scripts/setup-codex.sh && echo "Syntax OK"
```

Expected: `Syntax OK`

- [ ] **Step 4: Commit**

```bash
git add scripts/setup-codex.sh
git commit -m "feat: add setup-codex.sh install script"
```

---

### Task 11: setup.sh (main wrapper)

**Files:**
- Create: `scripts/setup.sh`

**Interfaces:**
- Consumes: `setup-claude.sh`, `setup-cursor.sh`, `setup-codex.sh`
- Produces: single entry point for all install options

- [ ] **Step 1: Write scripts/setup.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<EOF
Usage: setup.sh [OPTIONS]

Install encore-skills into AI coding tools.

Options:
  --claude    Install globally into Claude Code (~/.claude/skills/)
  --cursor    Install into current project (.cursor/rules/)
  --codex     Install into current project (AGENTS.md)
  --all       Install for all tools
  --help      Show this help

Examples:
  ./scripts/setup.sh --claude
  ./scripts/setup.sh --cursor --codex
  ./scripts/setup.sh --all

One-liner (Claude Code):
  curl -fsSL https://raw.githubusercontent.com/encore/encore-skills/main/scripts/setup.sh | bash -s -- --claude
EOF
}

if [ $# -eq 0 ]; then
  usage
  exit 1
fi

do_claude=false
do_cursor=false
do_codex=false

for arg in "$@"; do
  case "$arg" in
    --claude) do_claude=true ;;
    --cursor) do_cursor=true ;;
    --codex)  do_codex=true ;;
    --all)    do_claude=true; do_cursor=true; do_codex=true ;;
    --help)   usage; exit 0 ;;
    *)
      echo "Unknown option: $arg"
      usage
      exit 1
      ;;
  esac
done

if $do_claude; then
  echo "=== Claude Code ==="
  bash "$SCRIPTS_DIR/setup-claude.sh"
  echo ""
fi

if $do_cursor; then
  echo "=== Cursor ==="
  bash "$SCRIPTS_DIR/setup-cursor.sh"
  echo ""
fi

if $do_codex; then
  echo "=== Codex ==="
  bash "$SCRIPTS_DIR/setup-codex.sh"
  echo ""
fi

echo "✓ Setup complete."
```

- [ ] **Step 2: Make executable**

```bash
chmod +x scripts/setup.sh
```

- [ ] **Step 3: Verify syntax**

```bash
bash -n scripts/setup.sh && echo "Syntax OK"
```

Expected: `Syntax OK`

- [ ] **Step 4: Smoke test help flag**

```bash
./scripts/setup.sh --help
```

Expected: usage message printed, exit 0.

- [ ] **Step 5: Commit**

```bash
git add scripts/setup.sh
git commit -m "feat: add main setup.sh wrapper"
```

---

### Task 12: Pre-generate AGENTS.md and run full install verification

**Files:**
- Create: `AGENTS.md` (pre-generated for this repo)
- Modify: `CLAUDE.md` (already exists from Task 1)

**Interfaces:**
- Consumes: all 6 SKILL.md files, `setup-codex.sh`
- Produces: verified working install for all three tools

- [ ] **Step 1: Generate AGENTS.md for this repo**

```bash
cd /Users/encore/Dev/Github/encore-skills
./scripts/setup-codex.sh
```

Expected: `AGENTS.md` created in repo root with all 6 skills listed.

- [ ] **Step 2: Verify AGENTS.md content**

```bash
grep "^## Skill:" AGENTS.md
```

Expected output (6 lines):
```
## Skill: `analyze-issue`
## Skill: `create-mr`
## Skill: `fix-issue`
## Skill: `review-code`
## Skill: `workflow`
## Skill: `write-issue`
```

- [ ] **Step 3: Run Claude install and verify**

```bash
./scripts/setup.sh --claude
ls -la ~/.claude/skills/ | grep -E "analyze-issue|fix-issue|create-mr|write-issue|review-code|workflow"
```

Expected: 6 symlinks appear in `~/.claude/skills/`.

- [ ] **Step 4: Test Cursor generation in a temp directory**

```bash
tmp=$(mktemp -d)
cd "$tmp"
bash /Users/encore/Dev/Github/encore-skills/scripts/setup-cursor.sh
ls .cursor/rules/
cd /Users/encore/Dev/Github/encore-skills
rm -rf "$tmp"
```

Expected: 6 `.mdc` files listed.

- [ ] **Step 5: Test Codex generation in a temp directory**

```bash
tmp=$(mktemp -d)
cd "$tmp"
bash /Users/encore/Dev/Github/encore-skills/scripts/setup-codex.sh
head -5 AGENTS.md
cd /Users/encore/Dev/Github/encore-skills
rm -rf "$tmp"
```

Expected: first 5 lines show the AGENTS.md header.

- [ ] **Step 6: Final commit**

```bash
git add AGENTS.md
git commit -m "chore: pre-generate AGENTS.md for repo"
```

- [ ] **Step 7: Verify git log**

```bash
git log --oneline
```

Expected: ~12 commits, all tasks represented.
```
