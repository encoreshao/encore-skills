---
name: create-mr
description: Create a GitLab Merge Request — clear title, high-level summary of what was changed and why, explicit confirmation the issue is resolved
license: MIT
compatibility: git required. glab CLI optional. GitLab project access required.
metadata:
  author: encoreshao
  version: "1.5"
  tags: gitlab mr merge-request engineer workflow ship branch related-work
---

# Create MR

Use after `review-code` passes. A good MR description tells the reviewer what problem was solved and whether it's actually fixed — in 30 seconds or less. Don't list every file you touched. Don't over-explain. Give them the mental model they need to review well.

## Pre-flight

The MR must target the branch you actually branched from — not always `main`. If `fix-issue` created your branch, that base branch was recorded automatically; resolve it before diffing or opening the MR.

```bash
RESOLVE="$HOME/.claude/skills/gitlab-config/scripts/auto_resolve_issue.py"
BRANCH=$(git branch --show-current)
BASE=$(git config --local --get branch.$BRANCH.base || echo main)

git fetch origin
git status --porcelain             # anything uncommitted?
git log origin/$BASE..HEAD --oneline       # confirm what's going in
glab pipeline status 2>/dev/null || true   # check CI
```

If `git status --porcelain` shows uncommitted changes, commit them before pushing — an MR should never leave work behind uncommitted. Follow `fix-issue`'s commit convention (one commit per logical concern):

```bash
git add <files>
git commit -m "fix(scope): what was broken and how it's fixed

Closes #<issue-number>"
```

Don't commit unrelated or leftover debug changes — if something in the working tree doesn't belong in this MR, that's a signal to stop and ask, not to bundle it in.

## Check the issue thread for related work first

Other people may have already posted context in the issue — a prior attempt, a linked commit, a related MR, a decision made in a comment. If your MR description doesn't mention it, reviewers re-derive context that already exists, or miss that something relevant already happened.

```bash
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"
python $GITLAB sync-issue <project> <issue_iid>   # merges into the cache — see gitlab-config
```

Scan the returned `notes[]` for: other MRs (`!123`, "mentioned in merge request"), commits ("mentioned in commit `<sha>`"), other issues, or a comment stating a decision or a prior fix attempt. If you find any, list them — this becomes the MR's "Related" section below. If there's nothing, skip that section; don't invent context.

## Title

Format, always: `<feature_type>: #<issue_number> <description>`. The issue number is never optional — if there's no issue, that's a blocker, not a reason to drop it (see `write-issue`/`analyze-issue`).

`<feature_type>` matches the commit convention: `feat`, `fix`, `refactor`, `test`, `chore`, `docs`. `<description>` is what was fixed or added — from the user's perspective, not the implementation's.

```
fix: #42 users with uppercase emails can now log in
feat: #108 CSV export on the reports page
```

Not: `fix: add .downcase to auth query` (missing issue number, and describes the how, not the what). Not: `fix: users with uppercase emails can now log in` (missing issue number).

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
  "<feature_type>: #<issue-number> <what was fixed>" \
  "Closes #<issue-number>

<2-3 sentence summary>" \
  <issue_iid>
# e.g. python $RESOLVE create-mr webapp feat/42-fix-login auto \
#   "fix: #42 users with uppercase emails can now log in" \
#   "Closes #42\n\nNormalizes email input before DB lookup." 42

# With glab (single instance)
glab mr create \
  --title "<feature_type>: #<issue-number> <what was fixed>" \
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
