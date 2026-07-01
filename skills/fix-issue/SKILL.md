---
name: fix-issue
description: Implement a fix following the human-thinking loop — understand the root cause, plan the minimal change, implement, verify the problem is actually gone
license: MIT
compatibility: git required. Project test runner expected (any language).
metadata:
  author: encoreshao
  version: "1.2"
  tags: gitlab dev implementation fix tdd root-cause workflow
---

# Fix Issue

Implements a fix following how a senior engineer actually thinks: understand first, code second, verify the problem is gone — not just the tests pass.

## Input
- Analysis from `analyze-issue`, or the issue itself
- A feature branch (not `main`/`master`)

```bash
# Preferred — creates branch named issue-<iid>-<title> automatically
RESOLVE="$HOME/.claude/skills/gitlab-config/scripts/auto_resolve_issue.py"
python $RESOLVE create-branch <issue_iid> "<issue title>"

# Fallback (manual)
git checkout -b fix/<issue-number>-<short-description>
```

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
