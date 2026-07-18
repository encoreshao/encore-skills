---
name: triage-issue
description: Use when replying to comments on a GitLab issue, or when an issue has comments that might tag you or be waiting on your reply as assignee — figures out which comments genuinely need a response, drafts each reply grounded in the codebase, and posts after you confirm
license: MIT
compatibility: GitLab project access required. glab CLI optional. Local codebase optional — codebase analysis is skipped if none is available.
metadata:
  author: encoreshao
  version: "1.3"
  tags: gitlab issue comments reply triage mention assignee engineer cache memory
---

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
