---
name: summarize-issue
description: After an issue is fixed and its MR is created, summarize the work in high-level markdown and post it as a comment on the GitLab issue
license: MIT
compatibility: git required. glab CLI recommended. API script is the fallback.
metadata:
  author: encoreshao
  version: "1.2"
  tags: gitlab issue summary comment engineer workflow markdown glab post-mr
---

# Summarize Issue

Use when the user asks to summarize completed work and post it to the issue — e.g. "summarize this and post it to the issue", "add a summary comment to #42". Typically comes right after `create-mr`, once the issue is fixed and the MR exists (open or merged).

`create-mr` already posts a brief goal-based comment when the MR is opened. Use this skill for an updated recap (e.g. after merge or further changes) — a short, goal-based recap for anyone landing on the issue later — reporter, reviewer, or future-you — who wants to know whether the issue's goal was met without reading the diff or the whole comment thread.

## Gather context

Don't summarize from memory alone — pull the actual issue, MR, and commits so the summary reflects what shipped, not what was planned.

```bash
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"

python $GITLAB sync-issue <project> <issue_iid>       # issue body + existing notes
python $GITLAB get-mr <project> <mr_iid>              # MR title, description, state
git log origin/<base>..<branch> --oneline             # commits that make up the fix
```

If the MR is already merged, note that. If it's still open, say so instead of implying it's done.

## Pick the shape based on outcome

This skill assumes the issue is actually fixed — use the template below for that case. If the attempt didn't fully land (still failing, blocked on something outside your control, or you couldn't verify it), don't dress it up as delivered: replace the **Goal** line with **Blocked on:** and list what was tried, what failed, and what a human needs to do, one bullet each.

## Write the summary

Goal-based, not action-based. The issue comment answers "did we get what we asked for?"; *how* it was done — changes, files, classes, commands, branches, commits — already lives in the MR description (see `create-mr`), so don't repeat it here. Markdown, always:

```markdown
**Merge request:** !<mr-number> → `<target-branch>` — <merged / open, awaiting review>

**Goal:** <the outcome the issue asked for, now delivered, in one sentence from the user's view>
- <key result or metric — what a user can now do>
- <edge case now handled, or a number that matters: records affected, tests added, time saved>
- Checks: <n>/<n> passed ✅ (commands in the MR)
```

2-4 result bullets, one fact each; skip any you'd have to pad. Readable in 10 seconds. A caveat that needs a human's action (e.g. "couldn't verify locally, needs X before merge") gets its own bold **Needs:** line, never a trailing clause on a result bullet. See `examples/companies-grid-sort-fix.md` for a real before/after.

## Post the comment

```bash
# Default — API script (works across configured instances)
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"
python $GITLAB post-issue-comment <project> <issue_iid> "$SUMMARY"

# Fallback — glab
glab issue note <issue_number> --message "$SUMMARY"
```

Confirm back to the user with the issue URL and a one-line recap of what was posted — don't repeat the whole summary back to them, they just wrote it with you.
