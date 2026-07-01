---
name: review-code
description: Pre-MR self-review — first confirm the problem is actually solved, then check for security, correctness, and simplicity
license: MIT
compatibility: git required. glab CLI optional.
metadata:
  author: encore
  version: "1.1"
  tags: gitlab review security code-quality dev workflow pre-mr
---

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
