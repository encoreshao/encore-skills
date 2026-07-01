---
name: create-mr
description: Create a GitLab Merge Request — clear title, high-level summary of what was changed and why, explicit confirmation the issue is resolved
license: MIT
compatibility: git required. glab CLI optional. GitLab project access required.
metadata:
  author: encoreshao
  version: "1.1"
  tags: gitlab mr merge-request dev workflow ship
---

# Create MR

Use after `review-code` passes. A good MR description tells the reviewer what problem was solved and whether it's actually fixed — in 30 seconds or less. Don't list every file you touched. Don't over-explain. Give them the mental model they need to review well.

## Pre-flight

```bash
git fetch origin
git log origin/main..HEAD --oneline        # confirm what's going in
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
RESOLVE="$HOME/.claude/skills/gitlab-config/scripts/auto_resolve_issue.py"
git push -u origin HEAD
python $RESOLVE create-mr <project> <branch> main \
  "fix: <what was fixed>" \
  "Closes #<issue-number>

<2-3 sentence summary>" \
  <issue_iid>
# e.g. python $RESOLVE create-mr webapp issue-42-fix-login main \
#   "fix: users with uppercase emails can now log in" \
#   "Closes #42\n\nNormalizes email input before DB lookup." 42

# With glab (single instance)
glab mr create \
  --title "fix: <what was fixed>" \
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
