# Available Skills

This project uses the [encore-skills](https://github.com/encoreshao/encore-skills) workflow library.
Invoke a skill by name when the task matches its description.

## Skills

| Skill | Role | When to use |
|-------|------|-------------|
| `analyze-issue` | — | Read a GitLab issue, identify the root cause (not just symptoms), surface real risks, and produce an implementation approach before writing any code |
| `create-mr` | — | Create a GitLab Merge Request — clear title, high-level summary of what was changed and why, explicit confirmation the issue is resolved |
| `eng-workflow` | — | Full GitLab development loop — from issue to confirmed-resolved. Covers write-issue, analyze-issue, fix-issue, review-code, create-mr, triage-issue, and post-merge verification. |
| `fix-issue` | — | Implement a fix following the human-thinking loop — understand the root cause, plan the minimal change, implement, verify the problem is actually gone |
| `gitlab-config` | — | Wire up GitLab API access — multiple instances, project aliases, tokens. Run this once before any other GitLab skill. |
| `pm-workflow` | — | Full PM/designer loop — draft an issue, interact with users and stakeholders to validate it, refine until dev-ready, then finalize |
| `project-memory` | — | Record what was learned fixing an issue into docs/CONTEXT.md — so the next analysis starts from knowledge, not a blank scan |
| `review-code` | — | Pre-MR self-review — first confirm the problem is actually solved, then check for security, correctness, and simplicity |
| `triage-issue` | — | Use when a GitLab issue has comments that might tag you or be waiting on your reply as assignee, and you need to decide what actually needs a response |
| `write-issue` | — | Turn a rough idea into a well-structured GitLab issue with clear problem statement, root cause, and testable acceptance criteria |

---

## Skill: `analyze-issue`

> Read a GitLab issue, identify the root cause (not just symptoms), surface real risks, and produce an implementation approach before writing any code


# Analyze Issue

Run this before writing a single line of code. The goal is to understand the *real* problem, not just execute the ticket literally.

## Input
- Issue number (`#42`) with project alias or path, GitLab URL, or paste the issue text

```bash
# Preferred — supports multiple GitLab servers
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"
python $GITLAB get-issue <project> <number>
# e.g. python $GITLAB get-issue webapp 42
# e.g. python $GITLAB --instance=personal get-issue blog 7

# Fallback with glab (single instance)
glab issue view <number>
```

See `gitlab-config` skill for first-time setup.

## Before you start

Load only what's relevant — don't dump all context into memory.

```bash
# 1. Discover what exists
ls docs/CONTEXT.md 2>/dev/null && wc -l docs/CONTEXT.md
ls docs/context/ 2>/dev/null

# 2a. Single file under 100 lines — load whole file
cat docs/CONTEXT.md

# 2b. Single file over 100 lines — scan headers, then load relevant sections
grep "^## " docs/CONTEXT.md
awk '/^## Solved Issues/,/^## /' docs/CONTEXT.md

# 2c. Directory — read index first, then only domain files that match this issue
cat docs/context/index.md
cat docs/context/<relevant-domain>.md   # only the domains that apply
```

Check **Solved Issues** for similar past fixes, **Patterns** for established approaches, **Gotchas** for known traps. If it's already documented, use it — don't re-derive it.

## Steps

### 1. Understand the actual problem

Don't just read the description — interrogate it:
- What is the **root cause**? (not just the symptom reported)
- Is the issue asking for the right solution, or just the first solution someone thought of?
- What would a user notice if this were fixed? How would they know?

If the issue describes a symptom but not a cause, flag it before proceeding.

### 2. Extract real requirements

List the explicit requirements AND the implicit ones. Implicit requirements matter:
- What existing behavior must NOT break?
- What are the performance expectations?
- What are the security boundaries?
- Does this touch any API contract, schema, or shared interface?

### 3. Identify genuine risks

Check the actual codebase — don't guess:
```bash
grep -r "relevant_keyword" --include="*.rb" .
```
- What code does this touch, and what else depends on that code?
- Are there race conditions, caching issues, or N+1 risks?
- Does changing this break any existing tests or contracts?

### 4. Surface blockers

List questions that **must** be answered before coding. Don't start if these are open:
- Missing requirements
- Ambiguous acceptance criteria
- Unknown dependencies or owners

### 5. Propose the simplest approach

What is the smallest, most targeted change that fixes the root cause?
- 2–3 sentences on approach
- Files likely affected (verify in the codebase, don't guess)
- Complexity: small / medium / large — and why

### 6. Output

```
## Analysis: #<number> — <title>

### Root cause
<What is actually causing the problem — not just the symptom>

### Requirements
- [ ] Explicit: ...
- [ ] Implicit: ...

### Risks
- <Risk> → <Mitigation>

### Blockers (must resolve before coding)
- [ ] ...

### Approach
<2–3 sentences — simplest solution that addresses root cause>

### Files likely affected
- `path/to/file` — why

### Ready to code? Yes / No
```

---

## Skill: `create-mr`

> Create a GitLab Merge Request — clear title, high-level summary of what was changed and why, explicit confirmation the issue is resolved


# Create MR

Use after `review-code` passes. A good MR description tells the reviewer what problem was solved and whether it's actually fixed — in 30 seconds or less. Don't list every file you touched. Don't over-explain. Give them the mental model they need to review well.

## Pre-flight

The MR must target the branch you actually branched from — not always `main`. If `fix-issue` created your branch, that base branch was recorded automatically; resolve it before diffing or opening the MR.

```bash
RESOLVE="$HOME/.claude/skills/gitlab-config/scripts/auto_resolve_issue.py"
BRANCH=$(git branch --show-current)
BASE=$(git config --local --get branch.$BRANCH.base || echo main)

git fetch origin
git log origin/$BASE..HEAD --oneline       # confirm what's going in
glab pipeline status 2>/dev/null || true   # check CI
```

## Title

One line. What was fixed or added — from the user's perspective, not the implementation's.

```
fix: users with uppercase emails can now log in
feat: CSV export on the reports page
```

Not: `fix: add .downcase to auth query` — that's the how, not the what.

## Description

Keep it to 3 sections. No more.

```markdown
## What and why

Closes #<issue-number>

<2–3 sentences: what problem does this solve, and does it solve it? 
State this clearly. The reviewer needs to know if the goal was achieved — 
not just what files changed.>

## How

<1–2 sentences on the approach. High-level only. If the reviewer needs 
to understand a non-obvious decision, explain it here. Skip the obvious.>

## Verified

- [ ] Original problem reproduced and confirmed fixed
- [ ] Tests pass
- [ ] Manually tested: <what you did to verify>
```

The `Closes #<number>` line goes at the top of the description so GitLab auto-links and auto-closes the issue on merge.

## Create

```bash
# Preferred — API script (supports multiple GitLab servers)
# target "auto" resolves to the branch you branched from, falling back to main
RESOLVE="$HOME/.claude/skills/gitlab-config/scripts/auto_resolve_issue.py"
git push -u origin HEAD
python $RESOLVE create-mr <project> <branch> auto \
  "fix: <what was fixed>" \
  "Closes #<issue-number>

<2-3 sentence summary>" \
  <issue_iid>
# e.g. python $RESOLVE create-mr webapp feat/42-fix-login auto \
#   "fix: users with uppercase emails can now log in" \
#   "Closes #42\n\nNormalizes email input before DB lookup." 42

# With glab (single instance)
glab mr create \
  --title "fix: <what was fixed>" \
  --target-branch "$BASE" \
  --fill \
  --assignee @me \
  --remove-source-branch

# Without glab (manual)
git push -u origin HEAD
# Open the URL GitLab prints, paste the description above
```

## After creating

Share the MR URL. Post a note on the issue:

```bash
# Via API (any instance)
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"
python $GITLAB post-issue-comment <project> <issue_iid> "Fixed in !<mr-number>: <url>"

# Via glab
glab issue note <number> --message "Fixed in !<mr-number>. MR: <url>"
```

---

## Skill: `eng-workflow`

> Full GitLab development loop — from issue to confirmed-resolved. Covers write-issue, analyze-issue, fix-issue, review-code, create-mr, triage-issue, and post-merge verification.


# Engineer Workflow

Full development loop. The goal is not to merge an MR — it's to confirm the problem is actually gone.

## The loop

```
write-issue → analyze-issue → fix-issue → review-code → create-mr → [merge] → project-memory
      ↑            ↑ reads                                                           |
      │       docs/CONTEXT.md                                                        ↓
      └──────── new issue from feedback ─────────────────────── docs/CONTEXT.md grows smarter
```

## Entry points

| Where you are | Start here |
|---------------|------------|
| Have a rough idea or bug report | `write-issue` |
| Have a GitLab issue | `analyze-issue` |
| Have an analysis, ready to code | `fix-issue` |
| Code done, ready to ship | `review-code` |
| Issue has comments that may need your reply | `triage-issue` |

## Phase guide

### Phase 0: Write Issue
*Skip if issue already exists in GitLab.*

Use `write-issue`. Focus on the root cause, not just the symptom. Define what "fixed" looks like before any code is written.

**Gate:** Issue has a clear problem statement and testable acceptance criteria.

---

## Skill: `fix-issue`

> Implement a fix following the human-thinking loop — understand the root cause, plan the minimal change, implement, verify the problem is actually gone


# Fix Issue

Implements a fix following how a senior engineer actually thinks: understand first, code second, verify the problem is gone — not just the tests pass.

## Input
- Analysis from `analyze-issue`, or the issue itself
- A feature branch (not `main`/`master`/`develop`/`staging`)

### Branch check

Before touching any code, check the current branch:

```bash
git branch --show-current
```

If it's a protected branch (`main`, `master`, `develop`, `staging`), create a new one off it, named `<type>/<issue-number>-<func-name>` — `<type>` matches the commit convention below (`feat`, `fix`, `refactor`, `test`, `chore`, `docs`).

```bash
# Preferred — creates the branch and records the current branch as its base,
# so create-mr can later target the MR back to the right branch
RESOLVE="$HOME/.claude/skills/gitlab-config/scripts/auto_resolve_issue.py"
python $RESOLVE create-branch <issue_iid> "<func name>" <type>
# e.g. python $RESOLVE create-branch 123 "add login" feat  ->  feat/123-add-login

# Fallback (manual)
BASE=$(git branch --show-current)
git checkout -b <type>/<issue-number>-<func-name>
git config --local branch.<type>/<issue-number>-<func-name>.base "$BASE"
```

Already on a non-protected feature branch? Keep working on it — don't create a nested branch.

## The loop

### Phase 1: Understand before touching anything

Read the relevant code before writing a single line. You cannot fix what you don't understand.

- Check `docs/CONTEXT.md` (or `docs/context/<domain>.md` for large projects) first — scan Solved Issues for similar past fixes and Patterns for established approaches before searching the codebase from scratch
- Find the code involved: `grep`, file search, follow the call chain
- Understand why the current behavior happens — confirm the root cause from the analysis
- If the root cause turns out to be different from the analysis, stop and update the analysis

### Phase 2: Plan the minimal change

Write a short plan (bullet points) before coding:
- What exactly will you change and why
- What you will NOT touch (scope boundary)
- What could go wrong with your approach

The plan should describe the fix to the root cause — not a workaround or a patch over the symptom. If you're writing a workaround, say so explicitly and explain why.

Show the plan: "Here's my approach — does this look right?"

### Phase 3: Implement

Follow existing patterns — check nearby files before writing new code.

Rules:
- One commit per logical concern — don't bundle unrelated changes
- Write the test first when possible — it forces you to define "fixed" before you code
- If you find an unrelated bug, open an issue for it. Do not fix it here.

### Phase 4: Check your own work

Before declaring done, ask yourself:
- Did I fix the **root cause** or just suppress the symptom?
- Does any existing test now fail? (`git stash` your changes, run tests, restore)
- Did I introduce any security issues? (auth bypass, injection, exposed secrets)
- Did I change any API contract or schema without a migration?

For any serious risk found: stop, flag it, don't merge.

### Phase 5: Verify the problem is actually gone

- Run the tests — they must pass
- Manually reproduce the original problem from the issue — confirm it no longer occurs
- Check the acceptance criteria one by one — don't assume, verify each one

The problem is not fixed until you've confirmed it's gone, not just that tests are green.

### Phase 6: Ship or loop

All criteria met, problem confirmed gone → proceed to `review-code`.

If something is off:
- Unmet criterion → back to Phase 3
- Root cause was wrong → back to Phase 1
- Scope grew → open a new issue, stay focused here

## Commit convention

```bash
git commit -m "fix(scope): what was broken and how it's fixed

Closes #<issue-number>"
```

Types: `feat`, `fix`, `refactor`, `test`, `chore`, `docs`

---

## Skill: `gitlab-config`

> Wire up GitLab API access — multiple instances, project aliases, tokens. Run this once before any other GitLab skill.


# GitLab Config

Do this once. Every other skill reads from the same config — get it right here and everything else just works.

## Install

```bash
pip install requests
# or
pip install -r ~/.claude/skills/gitlab-config/requirements.txt
```

## Configure

```bash
cp ~/.claude/skills/gitlab-config/gitlab_config.json.template ~/.gitlab/config.json
chmod 600 ~/.gitlab/config.json
```

Edit `~/.gitlab/config.json`:

```json
{
  "default": "work",
  "instances": {
    "work": {
      "url": "https://gitlab.company.com",
      "token": "glpat-xxxxxxxxxxxxxxxxxxxx"
    },
    "personal": {
      "url": "https://gitlab.com",
      "token": "glpat-yyyyyyyyyyyyyyyyyyyy"
    }
  },
  "projects": {
    "webapp": {
      "project_id": "acme/webapp",
      "instance": "work"
    }
  }
}
```

Get a token: **GitLab → Settings → Access Tokens** — create with `api` scope. It won't be shown again.

**Env var fallback** (single instance only):
```bash
export GITLAB_URL="https://gitlab.com"
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
```

## Verify

```bash
python ~/.claude/skills/gitlab-config/scripts/gitlab_api.py list-instances
python ~/.claude/skills/gitlab-config/scripts/gitlab_api.py list-projects
```

## API reference

All other skills use these scripts:

```bash
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"

# Issues
python $GITLAB get-issue <project> <issue_iid>
python $GITLAB list-issues <project> [state] [labels...]
python $GITLAB post-issue-comment <project> <issue_iid> "<comment>"

# Merge Requests
python $GITLAB get-mr <project> <mr_iid>
python $GITLAB list-mrs <project> [state]
python $GITLAB get-diff <project> <mr_iid>
python $GITLAB post-mr-comment <project> <mr_iid> "<comment>"

# Stats
python $GITLAB aggregate-issues <project> [days]

# Override instance for a single call
python $GITLAB --instance=personal get-issue blog 42
```

`<project>` accepts: alias (`webapp`), numeric ID (`123`), or full path (`acme/webapp`).

Config lookup order: `./gitlab_config.json` → `~/.gitlab/config.json` → skill directory.

Instance resolution: `--instance` flag → project's configured instance → `default`.

## Troubleshooting

| Error | Fix |
|-------|-----|
| `GitLab configuration not found` | Create `~/.gitlab/config.json` or set env vars |
| `Instance 'X' not found` | Check spelling; run `list-instances` |
| `HTTP 401` | Token expired or wrong scope — regenerate with `api` scope |
| `HTTP 403` | Token lacks permission for this action |
| `HTTP 404` | Wrong project ID or issue number |

---

## Skill: `pm-workflow`

> Full PM/designer loop — draft an issue, interact with users and stakeholders to validate it, refine until dev-ready, then finalize


# PM Workflow

The PM loop is not about code — it's about getting the problem definition right before anyone writes a line. A vague issue creates vague work. Your job is done when an engineer can pick this up and start without asking you a single question.

## The loop

```
write-issue → share → gather-feedback → synthesize → refine → validate → finalize
      ↑                      |
      └───────── iterate ────┘
```

## Entry points

| Where you are | Start here |
|---------------|------------|
| Rough idea, bug report, user complaint | Phase 1: Draft |
| Issue drafted, not yet shared | Phase 2: Share |
| Feedback collected, need to update issue | Phase 4: Synthesize |
| Issue refined, checking if it's ready | Phase 5: Validate |

---

## Skill: `project-memory`

> Record what was learned fixing an issue into docs/CONTEXT.md — so the next analysis starts from knowledge, not a blank scan


# Project Memory

Every issue fix teaches you something about the codebase. Record it. The next session shouldn't have to rediscover the same root causes, the same patterns, the same traps. `docs/CONTEXT.md` (or `docs/context/` for large projects) is the living knowledge layer — it grows smarter with every resolved issue.

Three modes: **discover** what context exists, **load** only what's relevant, **update** after merging.

## Structure

**Small to medium projects** — single file:

```
docs/CONTEXT.md
```

**Large projects** — split by domain into a directory:

```
docs/context/
  index.md        ← overview + quick-reference table across all domains
  auth.md
  payments.md
  api.md
  background-jobs.md
  <domain>.md     ← one file per major area of the codebase
```

Start with the single file. Split into a directory only when `CONTEXT.md` grows past ~150 lines or covers more than 4–5 clearly separate domains.

---

## Skill: `review-code`

> Pre-MR self-review — first confirm the problem is actually solved, then check for security, correctness, and simplicity


# Review Code

Self-review before opening an MR. A reviewer's time is expensive — don't waste it on things you could have caught yourself.

## Input

```bash
# Local diff (self-review before opening MR)
git diff origin/main

# Review an existing MR via API (supports multiple GitLab servers)
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"
python $GITLAB get-mr <project> <mr_iid>      # MR metadata + comments
python $GITLAB get-diff <project> <mr_iid>    # unified diff of all changes

# Fallback with glab
glab mr view <number> --web
```

## Review order

### 1. Does it actually solve the problem? (most important)

Go back to the issue. Read it again. Ask:
- Does my change fix the **root cause** identified in the analysis?
- Would the user who reported this issue confirm it's resolved?
- Can I trace from the issue → root cause → my fix and see a clear line?

If the answer is "probably" or "I think so" — that's not good enough. Go verify.

### 2. Is it the simplest solution?

Before checking anything else, ask: is there a simpler way to fix this?

A 10-line change that's hard to follow is worse than a 30-line change that's obvious. But a 30-line change where 20 lines are unnecessary is worse than both. Cut what isn't needed.

### 3. Security

- [ ] No secrets, tokens, or credentials in code or comments
- [ ] User input is validated before use — not after, not maybe
- [ ] SQL/queries use parameterized inputs
- [ ] Auth checks exist on any new endpoints or actions
- [ ] No `eval`, `exec`, or dynamic code execution with user input

### 4. Correctness

- [ ] Edge cases covered: empty inputs, nulls, zero, large values
- [ ] Error cases handled — what happens when things fail?
- [ ] No silent failures (exceptions swallowed, errors ignored)
- [ ] Concurrency safe if relevant

### 5. Code quality

- [ ] Follows existing patterns — you're not the first person in this codebase
- [ ] No dead code, debug logs, or commented-out blocks left in
- [ ] Names describe intent, not implementation
- [ ] No unnecessary abstraction for a one-time use case

### 6. Tests

- [ ] New behavior has a test that would fail if you reverted the fix
- [ ] The regression case from the issue is covered
- [ ] Tests assert behavior, not internal implementation details

### 7. CI

- [ ] Pipeline passes
- [ ] No new lint warnings
- [ ] Migrations are reversible (if any)

## Output

```
## Self-review: <branch>

### Does it solve the problem?
<Yes/No + one sentence explanation>

### ✅ Looks good
- ...

### ⚠️ Suggestions (non-blocking)
- ...

### ❌ Must fix
- ...

### Verdict: Ready to merge / Needs changes
```

If verdict is "Needs changes" → back to `fix-issue`. Fix, don't rationalize.

---

## Skill: `triage-issue`

> Use when a GitLab issue has comments that might tag you or be waiting on your reply as assignee, and you need to decide what actually needs a response


# Triage Issue

Reads an issue and its comment thread, figures out which comments genuinely need a reply from you, grounds the reply in the actual codebase (not guesswork), and replies — directly when it's clearly warranted, or after checking with you when it's not.

## Input
- Issue number (`#42`) with project alias or path, or a GitLab URL
- A local clone of the relevant repo, if you want the reply grounded in current code (optional — skip Step 3 if there's no codebase)

```bash
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"
python $GITLAB whoami                            # confirm your username once per session
python $GITLAB get-issue <project> <number>       # issue + full comment thread
```

See `gitlab-config` skill for first-time setup.

## Steps

### 1. Fetch the issue and comments

`get-issue` returns the issue plus every note in `notes[]`, oldest-last. Each note has `author`, `body`, `system` (true = GitLab-generated, e.g. "assigned to @x" — never needs a reply), and `created_at`.

### 2. Decide which comments need your reply

Walk the notes in chronological order (reverse the array first — GitLab returns newest-first). Skip system notes and anything you authored. For everything else, a comment needs your reply if:

- It `@mentions` your username directly, **or**
- You're the assignee, it asks a direct question or requests an action, and no later comment from you addresses it

Then classify what's left:

| Signal | Verdict |
|---|---|
| Explicit `@you` mention with a clear question/request, nothing from you after it | **Clearly needs reply** |
| Directed at you but vague, or tags several people with no clear owner, or looks like it might already be resolved elsewhere (linked commit/MR, later comment) | **Ambiguous** |

If there's nothing needing a reply, say so and stop — don't invent a reason to post.

### 3. Ground the reply in the codebase

Don't draft from the issue text alone. For each comment needing a reply:
- Find the code the comment is actually about — `grep`, follow the call chain, check recent commits/MRs linked in the thread
- Confirm current behavior before claiming it's fixed, broken, or unchanged
- If there's no local codebase available, say so in the draft instead of guessing

### 4. Draft and act

- **Clearly needs reply** → draft the comment, then post it directly:
  ```bash
  python $GITLAB post-issue-comment <project> <number> "<reply>"
  ```
- **Ambiguous** → show the draft and your reasoning, and ask before posting. Don't post ambiguous replies unprompted.

### 5. Report

Summarize: what was posted, what's waiting on your confirmation (with the draft), and what was skipped and why (already answered, system note, no reply needed).

---

## Skill: `write-issue`

> Turn a rough idea into a well-structured GitLab issue with clear problem statement, root cause, and testable acceptance criteria


# Write Issue

Use when you have a rough idea, bug report, or feature request that needs to become a trackable GitLab issue.

## Steps

### 1. Nail the problem first

Before writing anything, ask:
- **What is actually broken or missing?** (the symptom)
- **Why does it happen?** (the root cause — for bugs)
- **Who is affected and how often?**
- **What does "fixed" look like?**

Don't start drafting until you can answer these. A vague issue creates vague work.

### 2. Draft the issue

**Title:** Short, imperative, problem-focused.
- Bug: `Users cannot log in when email contains uppercase letters`
- Feature: `Add CSV export to the reports page`
- No `[Type]` prefix — use labels for that.

**Description:**
```
## Problem
What is broken or missing? What is the root cause (for bugs)?
Be specific — include error messages, affected users, frequency.

## Expected behavior
What should happen instead?

## Acceptance Criteria
- [ ] <specific, testable outcome — not "it works">
- [ ] <regression test covers this case>
- [ ] <no related behavior is broken>

## Out of scope
What this issue does NOT cover. Prevents scope creep.
```

**Labels:** `bug` / `feature` / `improvement` + area (`backend`, `frontend`, `design`)

### 3. Sanity check before submitting

Ask yourself:
- Could an engineer start working on this without asking you any questions?
- Are the acceptance criteria specific enough to verify with a test?
- Is the root cause identified (for bugs) or is it still a guess?

If not — improve the issue before creating it.

### 4. Create

```bash
# With glab
glab issue create --title "TITLE" --description "DESCRIPTION" --label "bug,backend"

# Without glab: copy the text and paste into GitLab
```

---

