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
# Preferred — supports multiple GitLab servers, merges into the local cache
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"
python $GITLAB sync-issue <project> <number>
# e.g. python $GITLAB sync-issue webapp 42
# e.g. python $GITLAB --instance=personal sync-issue blog 7

# Fallback with glab (single instance)
glab issue view <number>
```

See `gitlab-config` skill for first-time setup and the local-memory cache it maintains — a prior analysis you saved with `annotate-issue` is worth checking before you redo the work.

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

Save it so re-analysis doesn't start from scratch next time:
```bash
CACHE="$HOME/.claude/skills/gitlab-config/scripts/gitlab_cache.py"
python $CACHE annotate-issue <instance> <project_id> <number> analysis "<root cause + approach, 2-3 sentences>"
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

## Check the issue thread for related work first

Other people may have already posted context in the issue — a prior attempt, a linked commit, a related MR, a decision made in a comment. If your MR description doesn't mention it, reviewers re-derive context that already exists, or miss that something relevant already happened.

```bash
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"
python $GITLAB sync-issue <project> <issue_iid>   # merges into the cache — see gitlab-config
```

Scan the returned `notes[]` for: other MRs (`!123`, "mentioned in merge request"), commits ("mentioned in commit `<sha>`"), other issues, or a comment stating a decision or a prior fix attempt. If you find any, list them — this becomes the MR's "Related" section below. If there's nothing, skip that section; don't invent context.

## Title

One line. What was fixed or added — from the user's perspective, not the implementation's.

```
fix: users with uppercase emails can now log in
feat: CSV export on the reports page
```

Not: `fix: add .downcase to auth query` — that's the how, not the what.

## Description

Keep it to 3 sections, plus a 4th only if Step 1 found something. No more.

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

## Related
<Only if the issue thread mentioned it — one line each, skip the section entirely otherwise>
- Follows up on !<mr-number> — <why it wasn't enough / what changed>
- Prior attempt in <commit-sha> — <why this MR differs>
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

## Local memory (instance / group / project / issue cache)

Every other skill should prefer these over the plain `get-issue`/`get-project` calls above — they hit the API the same way, but merge the result into `~/.gitlab/cache/<instance>/...` instead of throwing it away. Nothing already cached is ever dropped; new data layers on top.

```bash
python $GITLAB sync-project <project>              # project metadata + team roster -> project.json, feeds users.json
                                                    # also syncs the project's parent group, if it has one
python $GITLAB sync-group <group_path>             # group metadata + members -> group.json, feeds users.json
python $GITLAB sync-issue <project> <issue_iid>     # issue + notes, merged by note id -> issues/<iid>.json
python $GITLAB cached-issue <project> <issue_iid>   # read the cache with no network call

CACHE="$HOME/.claude/skills/gitlab-config/scripts/gitlab_cache.py"
python $CACHE get-users <instance>                            # instance-level team/user directory
python $CACHE get-group <instance> <group_path>               # group-level metadata + members
python $CACHE get-project <instance> <project_id>              # project-level metadata
python $CACHE annotate-issue <instance> <project_id> <issue_iid> <key> <value>     # record analysis/notes against an issue
python $CACHE annotate-project <instance> <project_id> <key> <value>               # record project-wide memory (see project-memory)
```

Why this exists: analysis, triage, and reply-drafting all re-read the same issue and the same team roster repeatedly. `sync-issue` still calls the API every time (so new comments are never missed) but merges onto the cached copy — so your own annotations (root cause, which comments you've already handled) survive, and you're not re-deriving what you already knew. `sync-project` builds the team directory once so usernames resolve to real names without a separate lookup per comment.

A GitLab **group** can hold several projects — e.g. group `ekohe/kurrant` holds projects `kurrant.web` and `camp`. `sync-project` automatically syncs the parent group too (detected from the project's `namespace`), so the group's roster and metadata are fetched once and shared across every project under it instead of being duplicated per project.

Cache layout:
```
~/.gitlab/cache/<instance>/users.json                              # instance-level: every user seen, keyed by id
~/.gitlab/cache/<instance>/groups/<group>/group.json               # group-level: metadata + members, shared by its projects
~/.gitlab/cache/<instance>/projects/<project>/project.json         # project-level: metadata, members, and your own `_memory`
~/.gitlab/cache/<instance>/projects/<project>/issues/<iid>.json    # issue-level: issue + notes + your own `_notes` annotations
```

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

Reads an issue and its comment thread, figures out which comments genuinely need a reply from you, grounds the reply in the actual codebase (not guesswork), drafts it in your own voice, and shows it to you — every time, no exceptions — before anything gets posted.

## Input
- Issue number (`#42`) with project alias or path, or a GitLab URL
- A local clone of the relevant repo, if you want the reply grounded in current code (optional — skip Step 3 if there's no codebase)

```bash
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"
python $GITLAB whoami                            # confirm your username once per session
python $GITLAB sync-project <project>             # once per project — builds the team/user directory
python $GITLAB sync-issue <project> <number>      # issue + full comment thread, merged into the cache
```

See `gitlab-config` skill for first-time setup and the local-memory cache it maintains.

## Steps

### 1. Fetch the issue and comments

Use `sync-issue`, not `get-issue` — same API call, but it merges onto whatever's already cached for this issue instead of discarding it, so any comment you've already handled (see Step 4) stays marked. It returns the issue plus every note in `notes[]`, oldest-last. Each note has `author`, `body`, `system` (true = GitLab-generated, e.g. "assigned to @x" — never needs a reply), and `created_at`.

Resolve `@mentions` and author names against the cached team directory (`gitlab_cache.py get-users <instance>`) instead of guessing from the raw GitLab username — it's already built from `sync-project` and every issue you've synced.

### 2. Decide which comments need your reply

Walk the notes in chronological order (reverse the array first — GitLab returns newest-first). Skip system notes, anything you authored, and any note id already listed in the cached `_notes.replied_note_ids` (see Step 4 — you've handled it in a prior run). For everything else, a comment needs your reply if:

- It `@mentions` your username directly, **or**
- You're the assignee, it asks a direct question or requests an action, and no later comment from you addresses it

Then classify what's left — this only shapes how you present the draft in Step 4, it never decides whether you ask first, because you always ask first:

| Signal | Verdict |
|---|---|
| Explicit `@you` mention with a clear question/request, nothing from you after it | **Clearly needs reply** — present the draft as ready to send |
| Directed at you but vague, or tags several people with no clear owner, or looks like it might already be resolved elsewhere (linked commit/MR, later comment) | **Ambiguous** — present the draft plus your reasoning for why it's unclear |

If there's nothing needing a reply, say so and stop — don't invent a reason to post.

### 3. Ground the reply in the codebase

Don't draft from the issue text alone. For each comment needing a reply:
- A quick lookup (one file, one symbol) — `grep` it yourself inline
- A real investigation (spans multiple files, root cause unclear, need to trace a call chain or check recent commits/MRs) — dispatch an agent (e.g. an `Explore` subagent) to do it. Keeps this skill's main thread on triage and drafting, not spelunking
- Confirm current behavior before claiming it's fixed, broken, or unchanged
- If there's no local codebase available, say so in the draft instead of guessing

### 4. Draft, then always confirm before posting

**Match the reply's length and format to the comment it answers — don't run every reply through the same template.**

- A one-line question ("is this fixed?") gets a one-line answer ("Yes, fixed in prod — see `abc1234`."). Padding a yes/no into paragraphs is wrong, not thorough.
- A multi-part question or a request with several asks gets a structured reply (short intro + bullets), one point per ask — no more.
- A comment that's really a status update or FYI, not a question, may not need prose at all — a link or a single confirming line is enough.
- Never add sections, disclaimers, or "let me know if you have questions" filler the comment didn't ask for.

**Write it in the assignee's own voice — first person, like they'd actually type it, not a templated support-ticket reply.** Match their tone from their own earlier comments in the thread (direct vs. casual, how much context they usually give). Personalized doesn't mean less accurate: state what's true, cite the file/commit/behavior you actually checked in Step 3, and don't oversell or hedge past what you confirmed.

**Never post without an explicit go-ahead — for both verdicts, every time:**

1. Show the draft, labeled by its Step 2 verdict (ready to send / ambiguous + why).
2. Wait for the user to approve, edit, or reject it.
3. Only after approval:
   ```bash
   python $GITLAB post-issue-comment <project> <number> "<reply>"
   CACHE="$HOME/.claude/skills/gitlab-config/scripts/gitlab_cache.py"
   python $CACHE annotate-issue <instance> <project_id> <number> replied_note_ids '[<note_id>, ...]'
   ```

Don't post a "clearly needs reply" draft just because it's clearly needed — clear only means you're confident in the content, not that you skip confirmation.

### 5. Report

Summarize: what's drafted and waiting on your approval (show each draft), and what was skipped and why (already answered, system note, no reply needed). Nothing here should say "posted" unless the user already approved it in this session.

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

