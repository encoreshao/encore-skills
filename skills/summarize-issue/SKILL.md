---
name: summarize-issue
description: After an issue is fixed and its MR is created, summarize the work in high-level markdown and post it as a comment on the GitLab issue
license: MIT
compatibility: git required. glab CLI recommended. API script is the fallback.
metadata:
  author: encoreshao
  version: "1.1"
  tags: gitlab issue summary comment engineer workflow markdown glab post-mr
---

# Summarize Issue

Use when the user asks to summarize completed work and post it to the issue — e.g. "summarize this and post it to the issue", "add a summary comment to #42". Typically comes right after `create-mr`, once the issue is fixed and the MR exists (open or merged).

This is not the one-line "Fixed in !123" note `create-mr` already posts. This is a fuller, high-level recap for anyone landing on the issue later — reporter, reviewer, or future-you — who wants to know what happened without reading the diff or the whole comment thread.

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

This skill assumes the issue is actually fixed — use the template below for that case. If the attempt didn't fully land (still failing, blocked on something outside your control, or you couldn't verify it), don't force it into "What's done" — that misleads a reader into thinking it shipped. Replace `## Changes`/`## Verified` with a plain `## Problem` (or `## Blocked on`) section stating what was tried, what actually failed or is blocking, and what's needed to unblock it. Same markdown/bullet discipline either way — headers and bullets per fact, never a run-on paragraph — just don't dress up a failure as a success.

## Write the summary

High-level only — this is a recap, not a diff. No file-by-file listings, no line-count stats. Markdown, always:

```markdown
## Summary

<2-3 sentences: what was wrong and what changed, in plain language.>

## Root cause

<1-2 sentences — only if non-obvious. Skip this section if the fix was straightforward.>

## Changes

- <what changed, one bullet per logical change — not per file>
- <...>

## Verified

- <what confirms this is actually fixed — test added, manually reproduced and checked, etc.>

## MR

!<mr-number> — <merged / open, awaiting review>
```

Omit any section that has nothing to say — don't pad it out. Keep the whole thing skimmable in under 30 seconds. Never collapse this into one dense paragraph mixing what shipped with what's still open or unverified — a caveat that needs a human's action (e.g. "couldn't verify locally, needs X before merge") always gets its own heading or bold label, not a trailing clause. See `examples/companies-grid-sort-fix.md` for a real before/after.

## Post the comment

```bash
# Default — API script (works across configured instances)
GITLAB="$HOME/.claude/skills/gitlab-config/scripts/gitlab_api.py"
python $GITLAB post-issue-comment <project> <issue_iid> "$SUMMARY"

# Fallback — glab
glab issue note <issue_number> --message "$SUMMARY"
```

Confirm back to the user with the issue URL and a one-line recap of what was posted — don't repeat the whole summary back to them, they just wrote it with you.
