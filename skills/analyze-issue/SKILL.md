---
name: analyze-issue
description: Read a GitLab issue, identify the root cause (not just symptoms), surface real risks, and produce an implementation approach before writing any code
license: MIT
compatibility: GitLab project access required. glab CLI optional. git required.
metadata:
  author: encoreshao
  version: "1.3"
  tags: gitlab issues analysis planning engineer pm root-cause cache memory
---

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

See `gitlab-config` skill for first-time setup and the local-memory cache it maintains — a prior analysis you saved with `annotate` is worth checking before you redo the work.

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
python $CACHE annotate <instance> <project_id> <number> analysis "<root cause + approach, 2-3 sentences>"
```
