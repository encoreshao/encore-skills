---
name: triage-issue
description: Use when a GitLab issue has comments that might tag you or be waiting on your reply as assignee, and you need to decide what actually needs a response
license: MIT
compatibility: GitLab project access required. glab CLI optional. Local codebase optional — codebase analysis is skipped if none is available.
metadata:
  author: encoreshao
  version: "1.1"
  tags: gitlab issue comments reply triage mention assignee engineer
---

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
- A quick lookup (one file, one symbol) — `grep` it yourself inline
- A real investigation (spans multiple files, root cause unclear, need to trace a call chain or check recent commits/MRs) — dispatch an agent (e.g. an `Explore` subagent) to do it. Keeps this skill's main thread on triage and drafting, not spelunking
- Confirm current behavior before claiming it's fixed, broken, or unchanged
- If there's no local codebase available, say so in the draft instead of guessing

### 4. Draft and act

**Match the reply's length and format to the comment it answers — don't run every reply through the same template.**

- A one-line question ("is this fixed?") gets a one-line answer ("Yes, fixed in prod — see `abc1234`."). Padding a yes/no into paragraphs is wrong, not thorough.
- A multi-part question or a request with several asks gets a structured reply (short intro + bullets), one point per ask — no more.
- A comment that's really a status update or FYI, not a question, may not need prose at all — a link or a single confirming line is enough.
- Never add sections, disclaimers, or "let me know if you have questions" filler the comment didn't ask for.

Then:

- **Clearly needs reply** → draft the comment at the right size, then post it directly:
  ```bash
  python $GITLAB post-issue-comment <project> <number> "<reply>"
  ```
- **Ambiguous** → show the draft and your reasoning, and ask before posting. Don't post ambiguous replies unprompted.

### 5. Report

Summarize: what was posted, what's waiting on your confirmation (with the draft), and what was skipped and why (already answered, system note, no reply needed).
